import mech_analyser.experiment.collation as ma_collation
import mech_analyser.experiment.microtester_g2.microindentation.data as ma_data
import pandas as pd

from typing import Optional


class RawTranscoder(ma_collation.RawTranscoder):
    """
    Microtester G2 microindentation experiment collated raw data file transcoders.
    """

    def __init__(self) -> None:
        super().__init__(ma_data.ma_data.RawTranscoder().columns)


class SummaryTranscoder(ma_collation.SummaryHorizontalTranscoder):
    """
    Microtester G2 microindentation experiment collated summary data file transcoders.
    """

    def __init__(self) -> None:
        # Obtain the base columns
        base_columns: dict[str, ma_data.SummaryTranscoder.Column] = (
            ma_data.SummaryTranscoder().columns
        )

        # Remove the heading column from the base column
        heading_column: ma_data.SummaryTranscoder.Column = base_columns.pop(
            "Cycle",
            ma_data.SummaryTranscoder.Column(
                name="Cycle",
                input_included=False,
                output_name="Cycle",
                output_header_column=0,
                data_type=str,
            ),
        )

        super().__init__(base_columns, heading_column)


class SummaryCollation(ma_collation.SummaryHorizontalCollation):
    """
    Microtester G2 microindentation experiment summary collation.

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
