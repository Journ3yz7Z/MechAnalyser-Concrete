import mech_analyser.experiment.collation as ma_collation
import mech_analyser.experiment.instron_68tm.stepwise.data as ma_data
import mech_analyser.util.units as ma_units
import pandas as pd

from typing import Optional


class RawTranscoder(ma_collation.RawTranscoder):
    """
    Instron 68TM stepwise compression experiment collated raw data file transcoders.
    """

    def __init__(self) -> None:
        super().__init__(ma_data.ma_data.RawTranscoder().columns)


class SummaryTranscoder(ma_collation.SummaryHorizontalTranscoder):
    """
    Instron 68TM stepwise compression experiment collated summary data file transcoders.
    """

    def __init__(self) -> None:
        # Obtain the base columns
        base_columns: dict[str, ma_data.SummaryTranscoder.Column] = (
            ma_data.SummaryTranscoder().columns
        )

        # Remove the heading column from the base columns
        heading_column: ma_data.SummaryTranscoder.Column = base_columns.pop(
            "Strain",
            ma_data.SummaryTranscoder.Column(
                name="Strain",
                input_included=False,
                output_name="Strain (%)",
                output_units=ma_units.unit_registry.parse_units("%"),
                output_header_column=0,
            ),
        )

        super().__init__(base_columns, heading_column)


class SummaryCollation(ma_collation.SummaryHorizontalCollation):
    """
    Instron 68TM stepwise compression experiment summary collation.

    Args:
        transcoder: The summary data transcoder.
        frame: The data frame containing the summary data.
        id: The unique identifier for the collation. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        transcoder: SummaryTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(transcoder, frame, id)
