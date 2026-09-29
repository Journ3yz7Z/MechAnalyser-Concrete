import dataclasses
import mech_analyser.experiment.instron_68tm.analyser as ma_analyser
import mech_analyser.experiment.instron_68tm.failure.data as ma_data
import mech_analyser.experiment.instron_68tm.failure.phase as ma_phase
import mech_analyser.util.units as ma_units

from pathlib import Path
from typing import Optional, cast


@dataclasses.dataclass
class Parameters(ma_analyser.Parameters):
    """
    Instron 68TM compression-to-failure experiment analyser parameters.

    Args:
        tare_force_N: The force which will be used to tare the experiment.  All
            raw data points with force less than the tare force will be
            discarded, and all data points with force greater than the tare
            force will be offset accordingly.
        properties_file: The path to the properties file containing the cross-sectional
            area and initial length of the sample.
        read_cross_sectional_area: Whether to read the cross-sectional area from the
            properties file.
        read_initial_length: Whether to read the initial length from the properties
            file.
        cross_sectional_area_m2: The cross-sectional surface area of the sample.
        initial_length_m: The initial length of the sample.
        abort_strain_pct: The strain at which the experiment aborts even if the
            sample has not yet failed.
        toughness_strain_pct: The strain at which the toughness is calculated.
            If set to None, the failure or abort strain will be used.
        e_modulus_method: Method used to calculate the Young's modulus.
        e_modulus_fixed_strain1_pct: The strain value which defines the first
            datapoint on the stress-strain curve used to calculate the Young's
            modulus.  It is ε1 in the equation E = (σ2 - σ1) / (ε2 - ε1)
        e_modulus_fixed_strain2_pct: The strain value which defines the second
            datapoint on the stress-strain curve used to calculate the Young's
            modulus.  It is ε2 in the equation E = (σ2 - σ1) / (ε2 - ε1)
        e_modulus_anchor_point: The point used to anchor the strain range over
            which the Young's modulus is to be calculated.
        e_modulus_anchor_offset_pct: The strain offset from the specific point
            on the stress-strain curve from/to which the Young's modulus will be
            calculated.  It, in combination with the anchor point, specifies ε1
            in the equation E = (σ2 - σ1) / (ε2 - ε1).
        e_modulus_anchor_strain_width_pct: The width of the range on the
            stress-strain curve over which the Young's modulus will be
            calculated.  It, in combination with the strain offset and anchor
            point, specifies ε2 in the equation E = (σ2 - σ1) / (ε2 - ε1).
        e_modulus_find_strain_min_pct: The strain value which defines the
            minimum strain that can be used to find the best approximation of
            the linear region of the stress-strain curve.
        e_modulus_find_strain_max_pct: The strain value which defines the
            maximum strain that can be used to find the best approximation of
            the linear region of the stress-strain curve.
        e_modulus_find_strain_width_pct: The width of the strain window which
            will be used to find the best approximation of the linear region of
            the stress-strain curve for all possible regions between the minimum
            and maximum strains.
    """

    abort_strain_pct: float = 95.0
    toughness_strain_pct: Optional[float] = None
    e_modulus_method: ma_phase.Parameters.Method = ma_phase.Parameters.Method.FIXED_RANGE
    e_modulus_fixed_strain1_pct: float = 10.0
    e_modulus_fixed_strain2_pct: float = 15.0
    e_modulus_anchor_point: ma_phase.Parameters.AnchorPoint = (
        ma_phase.Parameters.AnchorPoint.ULTIMATE
    )
    e_modulus_anchor_offset_pct: float = 5.0
    e_modulus_anchor_strain_width_pct: float = 5.0
    e_modulus_find_strain_min_pct: float = 10.0
    e_modulus_find_strain_max_pct: float = 90.0
    e_modulus_find_strain_width_pct: float = 5.0

    @property
    def abort_strain(self) -> float:
        return ma_units.convert_to_base_units(
            self.abort_strain_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_anchor_offset(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_anchor_offset_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_anchor_strain_width(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_anchor_strain_width_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_find_strain_max(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_find_strain_max_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_find_strain_min(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_find_strain_min_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_find_strain_width(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_find_strain_width_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_fixed_strain1(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_fixed_strain1_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_fixed_strain2(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_fixed_strain2_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def toughness_strain(self) -> Optional[float]:
        if self.toughness_strain_pct is None:
            return None

        return ma_units.convert_to_base_units(
            self.toughness_strain_pct,
            ma_units.unit_registry.Unit("%"),
        )


class Analyser(ma_analyser.Analyser):
    """
    Instron 68TM compression-to-failure experiment analyser.

    Args:
        input_file: The path to the input file containing the output of the Instron 68TM
            compression-to-failure experiment.
        parameters: The parameters to use when analysing the experiment.
        raw_transcoder: The raw experiment data file transcoder.
        processed_transcoder: The processed experiment data file transcoder.
        summary_transcoder: The experiment summary data file transcoder.
        phases: The phases of the experiment.
        id: The unique identifier for the analyser.  If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        input_file: Path,
        parameters: Parameters,
        raw_transcoder: ma_data.ma_data.RawTranscoder,
        processed_transcoder: ma_data.ProcessedTranscoder,
        summary_transcoder: ma_data.SummaryTranscoder,
        phases: list[ma_phase.Phase] = [],
        id: str = "",
    ) -> None:
        super().__init__(
            input_file,
            parameters,
            raw_transcoder,
            ma_data.SummaryData(summary_transcoder),
            [phase for phase in phases],
            id,
        )

        # Create the phases if they do not exist
        if not self.phases:
            self.phases.append(ma_phase.Phase(self.raw_data, processed_transcoder))

    @property
    def parameters(self) -> Parameters:
        return cast(Parameters, self._parameters)

    @property
    def phases(self) -> list[ma_phase.Phase]:  # type: ignore
        return cast(list[ma_phase.Phase], self._phases)

    @property
    def summary_data(self) -> ma_data.SummaryData:
        return cast(ma_data.SummaryData, self._summary_data)

    def analyse(self) -> None:
        """
        Analyses the output of the Instron 68TM compression-to-failure experiment.
        """

        self.summary_data.clear_all_rows()

        for i in range(len(self.phases)):
            parameters = ma_phase.Parameters(
                cross_sectional_area_m2=self.parameters.cross_sectional_area_m2,
                initial_length_m=self.parameters.initial_length_m,
                abort_strain_pct=self.parameters.abort_strain_pct,
                toughness_strain_pct=self.parameters.toughness_strain_pct,
                e_modulus_method=self.parameters.e_modulus_method,
                e_modulus_fixed_strain1_pct=self.parameters.e_modulus_fixed_strain1_pct,
                e_modulus_fixed_strain2_pct=self.parameters.e_modulus_fixed_strain2_pct,
                e_modulus_anchor_point=self.parameters.e_modulus_anchor_point,
                e_modulus_anchor_offset_pct=self.parameters.e_modulus_anchor_offset_pct,
                e_modulus_anchor_strain_width_pct=self.parameters.e_modulus_anchor_strain_width_pct,
                e_modulus_find_strain_min_pct=self.parameters.e_modulus_find_strain_min_pct,
                e_modulus_find_strain_max_pct=self.parameters.e_modulus_find_strain_max_pct,
                e_modulus_find_strain_width_pct=self.parameters.e_modulus_find_strain_width_pct,
            )
            self.phases[i].process(parameters)

            row = ma_data.SummaryData.Row(
                ultimate_force_N=self.phases[i].ultimate_force_N,
                ultimate_strain=self.phases[i].ultimate_strain,
                ultimate_strength_Pa=self.phases[i].ultimate_strength_Pa,
                e_modulus_strain_1=self.phases[i].e_modulus_strain1,
                e_modulus_strain_2=self.phases[i].e_modulus_strain2,
                c_Pa=self.phases[i].c_Pa,
                e_modulus_Pa=self.phases[i].e_modulus_Pa,
                e_modulus_r2=self.phases[i].e_modulus_r2,
                toughness_strain=self.phases[i].toughness_strain,
                toughness_Pa=self.phases[i].toughness_Pa,
            )
            self.summary_data.append_row(row)
