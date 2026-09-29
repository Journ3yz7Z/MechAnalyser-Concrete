import mech_analyser.experiment.data as ma_data
from mech_analyser.util.serialiser import Serialiser
import pandas as pd
from pathlib import Path
from typing import Any, Optional, Union, cast


class Transcoder(ma_data.Transcoder):
    """
    Base class for all collation data file transcoders.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        base_columns: dict[str, ma_data.Transcoder.Column],
        columns: dict[str, ma_data.Transcoder.Column] = {},
        id: str = "",
    ) -> None:
        super().__init__(columns, id)

        self._base_columns: dict[str, ma_data.Transcoder.Column] = base_columns

    @property
    def base_columns(self) -> dict[str, ma_data.Transcoder.Column]:
        return self._base_columns

    def load(self, input_file: Path, **kwargs: Any) -> pd.DataFrame:
        """
        Loads the input file into a frame and validates its contents.

        NOTE: Collation transcoders cannot load data.

        Args:
            input_file: The path to the input file.

        Raises:
            NotImplementedError: Collation transcoders cannot load data.

        Returns:
            pd.DataFrame: The loaded frame.
        """

        raise NotImplementedError("Collation transcoders cannot load data.")

    def get_base_column(self, base_name: str) -> ma_data.Transcoder.Column:
        """
        Returns the base column mapping.

        Args:
            base_name: The name of the base column as recognised by the program.

        Returns:
            ma_data.Transcoder.Column: The base column mapping.
        """

        return self._base_columns[base_name]

    def get_base_input_name(self, base_name: str) -> str:
        """
        Returns the name of the base column in the input file.

        Args:
            base_name: The name of the base column as recognised by the program.

        Returns:
            str: The name of the base column in the input file.
        """

        return self._base_columns[base_name].input_name

    def get_base_output_name(self, base_name: str) -> str:
        """
        Returns the name of the base column in the output file.

        Args:
            base_name: The name of the base column as recognised by the program.

        Returns:
            str: The name of the base column in the output file.
        """

        return self._base_columns[base_name].output_name

    def add_base_column(self, base_column: ma_data.Transcoder.Column) -> None:
        """
        Adds a base column to the mapping.

        Args:
            base_column: The base column to add to the mapping.
        """

        # Add the base column
        self._base_columns[base_column.name] = base_column.copy()

        # Adds any columns that can be derived from this base column
        # TODO

    def remove_base_column(self, base_name: str) -> None:
        """
        Removes a base column from the mapping.

        Args:
            base_name: The name of the base column to remove from the mapping.
        """

        # Remove the base column
        if base_name in self._base_columns:
            del self._base_columns[base_name]

        # Remove all columns derived from this base column
        # TODO

    def remove_all_base_columns(self) -> None:
        """
        Removes all base columns from the mapping.
        """

        self._base_columns.clear()

    def reorder_base_columns(self) -> None:
        """
        Reorders the base columns such that their output header columns are indexed
        sequentially from 0.
        """

        sorted_columns: list[ma_data.Transcoder.Column] = list(
            self._base_columns.values()
        )
        sorted_columns.sort(key=lambda c: c.output_header_column)

        # Update the output header column indices
        for i, column in enumerate(sorted_columns):
            self._base_columns[column.name].output_header_column = i

    def init_columns(self) -> None:
        """
        Initialises the columns from the base columns.
        """

        self.reorder_base_columns()
        self.remove_all_columns()


class Collation(ma_data.Data):
    """
    Base class for all collated data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to save the data.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: Transcoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

    @property
    def transcoder(self) -> Transcoder:
        return cast(Transcoder, self._transcoder)

    def append(self, data: ma_data.Data, name: str) -> None:
        """
        Appends the data to the collated data.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        Args:
            data: The data to append.
            name: The name of the data.
        """

        pass


class VerticalTranscoder(Transcoder):
    """
    Base class for all vertically-collated data file transcoders.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.
        heading_column: The mapping between the column name that the program recognises
            and the column name in the output file for the column which contains the
            row heading.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        base_columns: dict[str, ma_data.Transcoder.Column],
        heading_column: ma_data.Transcoder.Column,
        columns: dict[str, ma_data.Transcoder.Column] = {},
        id: str = "",
    ) -> None:
        super().__init__(base_columns, columns, id)

        self._heading_column: ma_data.Transcoder.Column = heading_column

    @property
    def heading_column(self) -> ma_data.Transcoder.Column:
        return self._heading_column

    def init_columns(self) -> None:
        """
        Initialises the columns from the base columns.
        """

        super().init_columns()

        # Add the heading column
        self._columns[self._heading_column.name] = self._heading_column.copy()

        # Add the base columns, offsetting their output header columns by 1 to account
        # for the heading column
        for column_name, column in self._base_columns.items():
            self._columns[column_name] = column.copy()
            self._columns[column_name].output_header_column += 1


class VerticalCollation(Collation):
    """
    Base class for all vertically-collated data.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created using the transcoder columns.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: VerticalTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(
            frame or pd.DataFrame(columns=list(transcoder.columns)),
            transcoder,
            id,
        )

    @property
    def transcoder(self) -> VerticalTranscoder:
        return cast(VerticalTranscoder, self._transcoder)

    def append(self, data: ma_data.Data, name: str) -> None:
        """
        Appends the data to the collated data.

        Args:
            data: The data to append.
            name: The name of the data.
        """

        # Extract the relevant columns from the data and add the name
        subset_frame: pd.DataFrame = data.frame[
            [column_name for column_name in self.transcoder.base_columns]
        ].copy(deep=True)
        subset_frame.insert(0, self.transcoder.heading_column.name, name)  # type: ignore

        # Append the subset frame to the collated frame
        if self._frame.empty:
            self._frame = subset_frame.copy(deep=True)
        else:
            self._frame = pd.concat([self._frame, subset_frame], ignore_index=True)


class HorizontalTranscoder(Transcoder):
    """
    Base class for all horizontally-collated data file transcoders.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.  The elements
            of `columns` should be constructed from this mapping and the data name
            according to the format `{data name}: {base column name}`.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class HorizontalCollation(Collation):
    """
    Base class for all horizontally-collated data.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: HorizontalTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(frame or pd.DataFrame(), transcoder, id)

    @property
    def transcoder(self) -> HorizontalTranscoder:
        return cast(HorizontalTranscoder, self._transcoder)

    def append(self, data: ma_data.Data, name: str) -> None:
        """
        Appends the data to the collated data.

        Args:
            data: The data to append.
            name: The name of the data.
        """

        # Extract the relevant columns from the data and add the name
        subset_frame: pd.DataFrame = data.frame[
            [column_name for column_name in self.transcoder.base_columns]
        ].copy(deep=True)
        subset_frame.columns = [
            f"{name}: {column_name}" for column_name in subset_frame.columns
        ]

        # Append the subset frame to the collated frame
        if self._frame.empty:
            self._frame = subset_frame.copy(deep=True)
        else:
            self._frame = pd.concat([self._frame, subset_frame], axis=1)

        # Update the transcoder columns to include the new columns
        start_index: int = (
            max(
                [c.output_header_column for c in self.transcoder.columns.values()],
                default=-1,
            )
            + 1
        )
        for column_name, column in self.transcoder.base_columns.items():
            self.transcoder.add_column(
                ma_data.Transcoder.Column(
                    name=f"{name}: {column_name}",
                    input_included=False,
                    output_name=f"{name}\n{column.output_name}",
                    output_units=column.output_units,
                    output_header_column=start_index + column.output_header_column,
                    data_type=column.data_type,
                )
            )


class HorizontalTranscoderWithHeader(HorizontalTranscoder):
    """
    Base class for all horizontally-collated data file transcoders with a header column.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.  The elements
            of `columns` should be constructed from this mapping and the data name
            according to the format `{data name}: {base column name}`.
        heading_column: The mapping between the column name that the program recognises
            and the column name in the output file for the column which contains the
            row heading.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        base_columns: dict[str, ma_data.Transcoder.Column],
        heading_column: ma_data.Transcoder.Column,
        columns: dict[str, ma_data.Transcoder.Column] = {},
        id: str = "",
    ) -> None:
        super().__init__(base_columns, columns, id)

        self._heading_column: ma_data.Transcoder.Column = heading_column

    @property
    def heading_column(self) -> ma_data.Transcoder.Column:
        return self._heading_column

    def init_columns(self) -> None:
        """
        Initialises the columns from the base columns.
        """

        super().init_columns()

        # Add the heading column
        self._columns[self._heading_column.name] = self._heading_column.copy()


class HorizontalCollationWithHeader(HorizontalCollation):
    """
    Base class for all horizontally-collated data with a header column.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created using the transcoder columns.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: HorizontalTranscoderWithHeader,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(transcoder, frame, id)

    @property
    def transcoder(self) -> HorizontalTranscoderWithHeader:
        return cast(HorizontalTranscoderWithHeader, self._transcoder)

    def append(self, data: ma_data.Data, name: str) -> None:
        """
        Appends the data to the collated data.  The row header column is assumed to be
        the same for all data sets.

        Args:
            data: The data to append.
            name: The name of the data.
        """

        # Add the row header column to all blank frames
        if self._frame.empty:
            self._frame = data.frame[[self.transcoder.heading_column.name]].copy(
                deep=True
            )

        super().append(data, name)


class RawTranscoder(HorizontalTranscoder):
    """
    Base class for all collated raw data file transcoders.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.  The elements
            of `columns` should be constructed from this mapping and the data name
            according to the format `{data name}: {base column name}`.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def save(
        self,
        output_file: Path,
        frame: pd.DataFrame,
        name: str = "Raw Data",
        **kwargs: Any,
    ) -> None:
        """
        Saves the raw frame to the output file.

        NOTE: This method can be overwritten in the child classes if the output file
                is not an Excel file.

        Args:
            output_file: The path to the output file.
            frame: The frame to save to the output file.
            name: The name by which the data will be referenced within the output file.
        """

        super().save(output_file, frame, name, **kwargs)


class RawCollation(HorizontalCollation):
    """
    Base class for all collated raw data.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created using the transcoder columns.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: RawTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(transcoder, frame, id)

    @property
    def transcoder(self) -> RawTranscoder:
        return cast(RawTranscoder, self._transcoder)


class ProcessedTranscoder(HorizontalTranscoder):
    """
    Base class for all collated processed data file transcoders.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.  The elements
            of `columns` should be constructed from this mapping and the data name
            according to the format `{data name}: {base column name}`.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class ProcessedCollation(HorizontalCollation):
    """
    Base class for all collated processed data.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created using the transcoder columns.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: ProcessedTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(transcoder, frame, id)

    @property
    def transcoder(self) -> ProcessedTranscoder:
        return cast(ProcessedTranscoder, self._transcoder)


class SummaryVerticalTranscoder(VerticalTranscoder):
    """
    Base class for all vertically-collated summary data file transcoders.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.
        heading_column: The mapping between the column name that the program recognises
            and the column name in the output file for the column which contains the
            row heading.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class SummaryVerticalCollation(VerticalCollation):
    """
    Base class for all vertically-collated summary data.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created using the transcoder columns.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: SummaryVerticalTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(transcoder, frame, id)


class SummaryHorizontalTranscoder(HorizontalTranscoderWithHeader):
    """
    Base class for all horizontally-collated summary data file transcoders with a header
    column.

    Args:
        base_columns: The mapping between the column name of the data to be collated that
            the program recognises and the column name in the output file.  The elements
            of `columns` should be constructed from this mapping and the data name
            according to the format `{data name}: {base column name}`.
        heading_column: The mapping between the column name that the program recognises
            and the column name in the output file for the column which contains the
            row heading.
        columns: The mapping between the column name that the program recognises and the
            column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class SummaryHorizontalCollation(HorizontalCollationWithHeader):
    """
    Base class for all horizontally-collated summary data with a header column.

    Args:
        transcoder: The transcoder used to load and save the data.
        frame: The underlying pd.DataFrame representation of the data.  If none is
            provided, an empty frame is created using the transcoder columns.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        transcoder: SummaryHorizontalTranscoder,
        frame: Optional[pd.DataFrame] = None,
        id: str = "",
    ) -> None:
        super().__init__(transcoder, frame, id)


# Summary type aliases
SummaryTranscoder = Union[SummaryHorizontalTranscoder, SummaryVerticalTranscoder]
SummaryCollation = Union[SummaryHorizontalCollation, SummaryVerticalCollation]


class Collator(Serialiser):
    """
    Base class for all collators.

    Args:
        raw_collation: The collated raw data.
        summary_collations: The dictionary of all summary collations.  The keys are the
            names of the summary collations.
        id: The unique identifier for the collator. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        raw_collation: RawCollation,
        summary_collations: dict[str, SummaryCollation],
        id: str = "",
    ) -> None:
        super().__init__(id)

        self._raw_collation: RawCollation = raw_collation
        self._summary_collations: dict[str, SummaryCollation] = summary_collations

    @property
    def raw_collation(self) -> RawCollation:
        return self._raw_collation

    @property
    def summary_collations(self) -> dict[str, SummaryCollation]:
        return self._summary_collations

    def save(self, output_file: Path, **kwargs: Any) -> None:
        """
        Saves the collation to a file.  This includes the collated raw data, and all
        collated summary data.

        Args:
            output_file: The path to the output file which will contain the collation.
        """

        # Remove the file if it already exists
        if output_file.exists():
            output_file.unlink()

        # Save the raw and summary collations
        self._raw_collation.save(output_file, **kwargs)
        for name, summary_collation in self.summary_collations.items():
            summary_collation.save(output_file, name, **kwargs)
