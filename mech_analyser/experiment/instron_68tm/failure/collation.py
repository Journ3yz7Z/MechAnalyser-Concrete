import mech_analyser.experiment.collation as ma_collation
import mech_analyser.experiment.instron_68tm.failure.data as ma_data
import pandas as pd

from typing import Optional


class RawTranscoder(ma_collation.RawTranscoder):
    """
    Instron 68TM compression-to-failure experiment collated raw data file transcoders.
    """

    def __init__(self) -> None:
        super().__init__(ma_data.ma_data.RawTranscoder().columns)


class SummaryTranscoder(ma_collation.SummaryVerticalTranscoder):
    """
    Instron 68TM compression-to-failure experiment collated summary data file transcoders.
    """

    def __init__(self) -> None:
        super().__init__(
            ma_data.SummaryTranscoder().columns,
            ma_data.SummaryTranscoder.Column(
                name="Name",
                input_included=False,
                output_name="Sample",
                output_header_column=0,
                data_type=str,
            ),
        )


class SummaryCollation(ma_collation.SummaryVerticalCollation):
    """
    Instron 68TM compression-to-failure experiment summary collation.

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
