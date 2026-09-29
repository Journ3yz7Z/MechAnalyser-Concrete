import dataclasses
from mech_analyser.util.serialiser import SerialisedObject, Serialiser
from mech_analyser.util.units import convert_from_base_units, convert_to_base_units
import openpyxl.utils
import openpyxl.worksheet.worksheet
import pandas as pd
from pathlib import Path
import pint
import pyqtgraph as pg  # type: ignore
from typing import Any, Literal, Mapping, Optional, Self, Union, cast

# Serialised type aliases
SerialisedColumn = Mapping[str, Union[str, int, list[int], type, pint.Unit]]
SerialisedColumns = Mapping[str, SerialisedColumn]
SerialisedTranscoder = Mapping[str, Union[str, SerialisedColumns]]
SerialisedFrame = Mapping[str, list[Union[float, int, str]]]
SerialisedData = Mapping[str, Union[str, SerialisedFrame]]


class Transcoder(Serialiser):
    """
    Base class for all data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    @dataclasses.dataclass
    class Column(Serialiser):
        """
        Storage class for the mapping between the column name that the program recognises,
        the column name in the input file, and the column name in the output file.

        Args:
            name: The name of the column as recognised by the program.
            input_included: Whether the column is included in the input file.
            input_included_editing: Whether the input_included flag can be edited.
            input_name: The name of the column in the input file.
            input_units: The units of the data in the input file.
            input_header_rows: The rows in the input file that contain the header.
            input_header_column: The column in the input file that contains the header.
            output_included: Whether the column is included in the output file.
            output_included_editing: Whether the output_included flag can be edited.
            output_name: The name of the column in the output file.  To utilise multiple
                rows for the name of the column, use a newline character ('\n') to
                separate the rows.
            output_units: The units of the data in the output file.
            output_header_column: The column in the output file that contains the header.
            data_type: The type of the data in the column.
        """

        name: str = dataclasses.field(default="")
        input_included: bool = dataclasses.field(default=True)
        input_included_editing: bool = dataclasses.field(default=False)
        input_name: str = dataclasses.field(default="")
        input_units: pint.Unit = dataclasses.field(default=pint.Unit("dimensionless"))
        input_header_rows: list[int] = dataclasses.field(default_factory=lambda: [0])
        input_header_column: int = dataclasses.field(default=0)
        output_included: bool = dataclasses.field(default=True)
        output_included_editing: bool = dataclasses.field(default=True)
        output_name: str = dataclasses.field(default="")
        output_units: pint.Unit = dataclasses.field(default=pint.Unit("dimensionless"))
        output_header_column: int = dataclasses.field(default=0)
        data_type: type = dataclasses.field(default=float)

        def __post_init__(self) -> None:
            super().__post_init__()

            if self.input_included and not self.input_units.is_compatible_with(
                self.output_units
            ):
                raise ValueError(
                    f"Units are incompatible ({self.input_units} with "
                    f"{self.output_units})"
                )

            for i in range(1, len(self.input_header_rows)):
                if self.input_header_rows[i] != self.input_header_rows[0] + i:
                    raise ValueError(
                        f"Header must occupy consecutive rows in CSV file: "
                        f"{self.input_header_rows}"
                    )

        def copy(self) -> Self:
            """
            Returns a copy of the column.

            Returns:
                Self: A copy of the column.
            """
            return type(self)(**dataclasses.asdict(self))

        def get_output_name_as_tuple(self, number_of_rows: int) -> tuple[str, ...]:
            """
            Returns the output name as a tuple of strings, split by newline characters.

            Args:
                number_of_rows: The number of rows in the output file that contain the
                    header.

            Returns:
                tuple[str, ...]: The output name as a tuple of strings.
            """

            return tuple(
                self.output_name.split("\n")
                + [""] * (number_of_rows - (self.output_name.count("\n") + 1))
            )

        def load(
            self,
            input_file: Path,
            encoding: str = "utf-8",
            **kwargs: Any,
        ) -> pd.DataFrame:
            """
            Loads the column from the input file.

            NOTE: This method can be overwritten in the child classes if the input file is
                  not a CSV file.

            Args:
                input_file: The path to the input file.
                encoding: The encoding of the input file.

            Returns:
                pd.DataFrame: The loaded column.
            """

            frame: pd.DataFrame = pd.read_csv(  # type: ignore
                input_file,
                header=self.input_header_rows,
                skip_blank_lines=False,
                encoding=encoding,
            )
            if len(self.input_header_rows) > 1:
                frame.columns = [
                    " ".join(
                        [
                            str(row).strip()
                            for row in column
                            if not str(row).startswith("Unnamed")
                        ]
                    )
                    for column in frame.columns
                ]

            # Raw data is not included in the input file: create an empty column
            # NOTE: due to how load() is called, this condition should actually never
            #       trigger, but it is included as a safeguard in case it is called
            if not self.input_included:
                return pd.DataFrame([self.data_type()] * len(frame), columns=[self.name])

            # Select the desired column manually
            if self.input_header_column < 0:
                raise ValueError("Input header column index cannot be negative.")
            elif self.input_header_column >= len(frame.columns):
                raise ValueError(
                    f"Column index {self.input_header_column} is out of bounds."
                )
            frame = frame.iloc[:, [self.input_header_column]]

            # Update the column name to match the name as recognised by the program
            if frame.columns[0] != self.input_name:
                raise ValueError(
                    f"Column name in input file does not match expected name: "
                    f"{self.input_name} != {frame.columns[0]}"
                )
            frame.rename(columns={self.input_name: self.name}, inplace=True)

            # Validate the data type
            try:
                frame[self.name] = frame[self.name].astype(self.data_type)
            except ValueError:
                raise ValueError(
                    f"Column '{self.name}' in input file cannot be converted to "
                    f"{self.data_type.__name__}"
                )

            # Convert the units of the column to base units
            try:
                frame[self.name] = (
                    frame[self.name]
                    .apply(  # type: ignore
                        lambda x: convert_to_base_units(x, self.input_units)  # type: ignore
                    )
                    .astype(self.data_type)
                )
            except pint.UndefinedUnitError:
                raise ValueError(
                    f"Column '{self.name}' in input file has undefined units: "
                    f"{self.input_units}"
                )

            return frame

        def serialise(self) -> SerialisedColumn:
            """
            Serialises the column.

            Returns:
                SerialisedColumn: The serialised column.
            """

            return {
                **super().serialise(),
                **dataclasses.asdict(self),
            }

        @classmethod
        def deserialise(cls, serialised_object: SerialisedColumn, **kwargs: Any) -> Self:
            """
            Deserialises the column.

            Args:
                serialised_object: The serialised column.

            Returns:
                Column: The deserialised column.
            """

            # NOTE: need to remove the custom module and class keys
            serialised_column: SerialisedColumn = dict(serialised_object)
            del serialised_column["module"]
            del serialised_column["class"]

            return cls(**serialised_column)  # type: ignore (subclasses will have different parameters)

    def __init__(self, columns: dict[str, Column] = {}, id: str = "") -> None:
        super().__init__(id)

        self._columns: dict[str, Transcoder.Column] = columns

    @property
    def columns(self) -> dict[str, Column]:
        return self._columns

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def header_rows(self) -> int:
        return (
            max(column.output_name.count("\n") + 1 for column in self._columns.values())
            if len(self._columns) > 0
            else 1
        )

    def get_column(self, name: str) -> Column:
        """
        Returns the column mapping.

        Args:
            name: The name of the column as recognised by the program.

        Returns:
            Transcoder.Column: The column mapping.
        """

        return self._columns[name]

    def get_input_name(self, name: str) -> str:
        """
        Returns the name of the column in the input file.

        Args:
            name: The name of the column as recognised by the program.

        Returns:
            str: The name of the column in the input file.
        """

        return self._columns[name].input_name

    def get_output_name(self, name: str) -> str:
        """
        Returns the name of the column in the output file.

        Args:
            name: The name of the column as recognised by the program.

        Returns:
            str: The name of the column in the output file.
        """

        return self._columns[name].output_name

    def add_column(self, column: Column) -> None:
        """
        Adds a column to the mapping.

        Args:
            column: The column to add to the mapping.
        """

        self._columns[column.name] = column

    def remove_column(self, name: str) -> None:
        """
        Removes a column from the mapping.

        Args:
            name: The name of the column to remove from the mapping.
        """

        if name in self._columns:
            del self._columns[name]

    def remove_all_columns(self) -> None:
        """
        Removes all columns from the mapping.
        """

        self._columns.clear()

    def reorder_columns(self) -> None:
        """
        Reorders the columns such that their output header columns are indexed
        sequentially from 0.
        """

        # Update the output header column indices
        for i, column in enumerate(
            sorted(self._columns.values(), key=lambda c: c.output_header_column)
        ):
            column.output_header_column = i

    def load(self, input_file: Path, **kwargs: Any) -> pd.DataFrame:
        """
        Loads the input file into a frame and validates its contents.

        NOTE: This method can be overwritten in the child classes if the input file is
              not a CSV file.

        Args:
            input_file: The path to the input file.

        Returns:
            pd.DataFrame: The loaded frame.
        """

        # Load the columns from the input file
        frame: pd.DataFrame = pd.concat(
            [
                i.load(input_file, encoding=self.encoding, **kwargs)
                for i in self._columns.values()
                if i.input_included
            ],
            axis=1,
        )

        # Reset the index of the frame
        frame.reset_index(drop=True, inplace=True)

        return frame

    def save(
        self,
        output_file: Path,
        frame: pd.DataFrame,
        name: str = "Data",
        **kwargs: Any,
    ) -> None:
        """
        Saves the frame to the output file.

        NOTE: This method can be overwritten in the child classes if the output file is
              not an Excel file.

        Args:
            output_file: The path to the output file.
            frame: The frame to save to the output file.
            name: The name by which the data will be referenced within the output file.
        """

        # Validate the outputs
        ordered_columns: list[Transcoder.Column] = sorted(
            [column for column in self._columns.values() if column.output_included],
            key=lambda column: column.output_header_column,
        )
        if len(ordered_columns) == 0:
            return
        elif ordered_columns[0].output_header_column < 0:
            raise ValueError("Output header column index cannot be negative.")
        elif (
            len(ordered_columns)
            != ordered_columns[-1].output_header_column
            - ordered_columns[0].output_header_column
            + 1
        ):
            raise ValueError("Output header column indices must be consecutive.")

        # Combine all columns into a single DataFrame, ordered by the output header column
        # If the output name contains newline characters, it will be split into multiple
        # rows in the output file
        output_frame: pd.DataFrame = pd.concat(
            [frame[[column.name]].copy(deep=True) for column in ordered_columns],
            axis=1,
        )
        output_frame.rename(
            columns={
                column.name: self._get_output_name_as_tuple(column)
                for column in ordered_columns
            },
            inplace=True,
        )
        output_frame.columns = pd.MultiIndex.from_tuples(output_frame.columns)  # type: ignore
        output_frame.reset_index(drop=True, inplace=True)

        # Convert the units of the output frame
        for column in ordered_columns:
            try:
                output_frame[self._get_output_name_as_tuple(column)] = output_frame[
                    self._get_output_name_as_tuple(column)
                ].apply(  # type: ignore
                    lambda x: convert_from_base_units(x, column.output_units)  # type: ignore
                )
            except pint.UndefinedUnitError:
                raise ValueError(
                    f"Column '{self._get_output_name_as_tuple(column)}' in output file "
                    f"has undefined units: {column.output_units}"
                )

        # Save the frame to the output file
        mode: Literal["w", "a"] = "w" if not output_file.exists() else "a"
        if_sheet_exists: Optional[Literal["overlay"]] = (
            "overlay" if output_file.exists() else None
        )
        with pd.ExcelWriter(
            output_file,
            engine="openpyxl",
            mode=mode,
            if_sheet_exists=if_sheet_exists,
        ) as writer:
            # NOTE: header and data written separately to avoid blank row between them and
            #       to allow for multi-row headers without an index column
            output_frame.drop(output_frame.index).to_excel(  # type: ignore
                writer,
                sheet_name=name,
                startcol=ordered_columns[0].output_header_column,
            )
            # NOTE: if the Excel file already exists and therefore was opened in append
            #       mode, this second call to to_excel() would always raise an exception.
            #       Therefore, it is necessary to specify if_sheet_exists="overlay" when
            #       opening the ExcelWriter in append mode.
            output_frame.to_excel(  # type: ignore
                writer,
                sheet_name=name,
                header=False,
                startrow=self.header_rows - 1,
                startcol=ordered_columns[0].output_header_column,
            )

            worksheet: openpyxl.worksheet.worksheet.Worksheet = writer.sheets[name]

            # Autofit the column size
            for id, column in enumerate(worksheet.iter_cols(), start=1):
                max_length: int = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column
                )
                worksheet.column_dimensions[
                    openpyxl.utils.get_column_letter(id)
                ].width = (max_length + 2)

            # Hide the index column
            # NOTE: worksheet.delete_cols() does not work if there is a multi-row header
            #       with merged cells
            worksheet.column_dimensions["A"].hidden = True

    def serialise(self) -> SerialisedTranscoder:
        """
        Serialises the transcoder.

        Returns:
            SerialisedTranscoder: The serialised transcoder.
        """

        return {
            **super().serialise(),
            "columns": {
                name: column.serialise() for name, column in self._columns.items()
            },
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedTranscoder, **kwargs: Any) -> Self:
        """
        Deserialises the transcoder.

        Args:
            serialised_object: The serialised transcoder.

        Raises:
            ValueError: If the serialised transcoder cannot be found or is of the wrong
                type.

        Returns:
            Transcoder: The deserialised transcoder.
        """

        id: str = cls._deserialise_id(serialised_object)
        columns: dict[str, Transcoder.Column] = cls._deserialise_columns(
            serialised_object
        )

        return cls._deserialise(id, serialised_object, columns, **kwargs)

    def _get_output_name_as_tuple(self, column: Column) -> tuple[str, ...]:
        """
        Returns the output name as a tuple of strings, split by newline characters.

        Args:
            column: The column object.

        Returns:
            tuple[str, ...]: The output name as a tuple of strings.
        """

        return column.get_output_name_as_tuple(self.header_rows)

    @classmethod
    def _deserialise(
        cls,
        id: str,
        serialised_transcoder: SerialisedTranscoder,
        columns: dict[str, Column],
        **kwargs: Any,
    ) -> Self:
        """
        Deserialises the transcoder.

        NOTE: this is an abstract method that can be overwritten in the child classes.

        Args:
            id: The unique identifier for the transcoder.
            serialised_transcoder: The serialised transcoder.
            columns: The deserialised columns.

        Returns:
            Transcoder: The deserialised transcoder.
        """

        return cls(columns, id)

    @classmethod
    def _deserialise_columns(
        cls, serialised_transcoder: SerialisedTranscoder
    ) -> dict[str, Column]:
        """
        Deserialises the columns.

        Args:
            serialised_transcoder: The serialised transcoder.

        Raises:
            ValueError: If the serialised columns cannot be found or are of the wrong
                type.

        Returns:
            dict[str, Column]: The deserialised columns.
        """

        if (
            not isinstance(serialised_transcoder.get("columns"), dict)
            or not all(
                isinstance(i, str)
                for i in cast(dict[Any, Any], serialised_transcoder.get("columns")).keys()
            )
            or not all(
                isinstance(i, dict)
                for i in cast(
                    dict[str, Any], serialised_transcoder.get("columns")
                ).values()
            )
            or not all(
                all(isinstance(j, str) for j in i.keys())
                for i in cast(
                    dict[str, dict[Any, Any]], serialised_transcoder.get("columns")
                ).values()
            )
            or not all(
                all(isinstance(j, (str, int, list, type, pint.Unit)) for j in i.values())
                for i in cast(
                    dict[str, dict[str, Any]], serialised_transcoder.get("columns")
                ).values()
            )
            or not all(
                all(
                    all(isinstance(k, int) for k in j)
                    for j in i.values()
                    if isinstance(j, list)
                )
                for i in cast(
                    dict[str, dict[str, Union[str, int, list[Any], type, pint.Unit]]],
                    serialised_transcoder.get("columns"),
                ).values()
            )
        ):
            raise ValueError("Invalid frame data")

        return {
            name: Transcoder.Column.deserialise(column)
            for name, column in cast(
                SerialisedColumns,
                serialised_transcoder.get("columns"),
            ).items()
        }


class Data(Serialiser):
    """
    Base class for all data.

    TODO: Alternative for self._plot, self.plot, and self.generate_plot() not yet
          implemented.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(self, frame: pd.DataFrame, transcoder: Transcoder, id: str = "") -> None:
        super().__init__(id)

        self._frame: pd.DataFrame = frame.copy(deep=True)
        self._frame.reset_index(drop=True, inplace=True)
        self._transcoder: Transcoder = transcoder
        self._plot: pg.PlotWidget = (
            pg.PlotWidget()
        )  # TODO: evaluate if plotting should be external to the class

    @property
    def frame(self) -> pd.DataFrame:
        return self._frame

    @property
    def transcoder(self) -> Transcoder:
        return self._transcoder

    @property
    def plot(self) -> pg.PlotWidget:
        # TODO: evaluate if plotting should be external to the class
        return self._plot

    @property
    def columns(self) -> list[str]:
        return [i for i in self._frame.columns]

    def generate_plot(self, **kwargs: Any) -> None:
        """
        Generates a plot of the data.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        TODO: evaluate if plotting should be external to the class
        """

        pass

    def save(self, output_file: Path, name: str = "", **kwargs: Any) -> None:
        """
        Saves the underlying pd.DataFrame representation of the data to the output file.

        Args:
            output_file: The path to the output file.
            name: The name by which the data will be referenced within the output file.

        NOTE: Check the documentation of the transcoder for the available keyword
              arguments.
        """

        if name:
            self._transcoder.save(output_file, self._frame, name, **kwargs)
        else:
            self._transcoder.save(output_file, self._frame, **kwargs)

    def serialise(self) -> SerialisedData:
        """
        Serialises the data.

        Returns:
            SerialisedData: The serialised data.
        """

        return {
            **super().serialise(),
            "frame": self.frame.to_dict(orient="list"),  # type: ignore
            "transcoder": self._transcoder.serialise(),
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedData, **kwargs: Any) -> Self:
        """
        Deserialises the data.

        Args:
            serialised_object: The serialised data.

        Raises:
            ValueError: If the serialised data cannot be found or is of the wrong type.

        Returns:
            Data: The deserialised data.
        """

        id: str = cls._deserialise_id(serialised_object)
        frame: pd.DataFrame = cls._deserialise_frame(serialised_object)
        transcoder: Transcoder = cls._deserialise_transcoder(serialised_object)

        return cls._deserialise(id, serialised_object, frame, transcoder, **kwargs)

    @classmethod
    def _deserialise(
        cls,
        id: str,
        serialised_data: SerialisedData,
        frame: pd.DataFrame,
        transcoder: Transcoder,
        **kwargs: Any,
    ) -> Self:
        """
        Deserialises the data.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        Args:
            id: The unique identifier for the data.
            serialised_data: The serialised data.
            frame: The deserialised frame.
            transcoder: The deserialised transcoder.

        Returns:
            Data: The deserialised data.
        """

        return cls(frame, transcoder, id)

    @classmethod
    def _deserialise_frame(cls, serialised_data: SerialisedData) -> pd.DataFrame:
        """
        Deserialises the frame.

        Args:
            serialised_data: The serialised data.

        Raises:
            ValueError: If the serialised frame cannot be found or is of the wrong type.

        Returns:
            pd.DataFrame: The deserialised frame.
        """

        if (
            not isinstance(serialised_data.get("frame"), dict)
            or not all(
                isinstance(i, str)
                for i in cast(dict[Any, Any], serialised_data.get("frame")).keys()
            )
            or not all(
                isinstance(i, list)
                for i in cast(dict[str, Any], serialised_data.get("frame")).values()
            )
            or not all(
                all(isinstance(j, (float, int, str)) for j in i)
                for i in cast(dict[str, list[Any]], serialised_data.get("frame")).values()
            )
        ):
            raise ValueError("Invalid frame data")

        return pd.DataFrame.from_dict(  # type: ignore
            cast(dict[str, SerialisedFrame], serialised_data.get("frame"))
        )

    @classmethod
    def _deserialise_transcoder(cls, serialised_data: SerialisedData) -> Transcoder:
        """
        Deserialises the transcoder.

        Args:
            serialised_data: The serialised data.

        Raises:
            ValueError: If the serialised transcoder cannot be found or is of the wrong
                type.

        Returns:
            Transcoder: The deserialised transcoder.
        """

        if not isinstance(serialised_data.get("transcoder"), dict) or not all(
            isinstance(i, str)
            for i in cast(dict[Any, Any], serialised_data.get("transcoder")).keys()
        ):
            raise ValueError("Invalid transcoder data")

        return cast(
            Transcoder,
            Serialiser.deserialise(
                cast(SerialisedObject, serialised_data.get("transcoder"))
            ),
        )


class RawTranscoder(Transcoder):
    """
    Base class for all raw data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
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


class RawData(Data):
    """
    Base class for all raw data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: RawTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

        self.generate_plot()

    @property
    def transcoder(self) -> RawTranscoder:
        return cast(RawTranscoder, self._transcoder)

    @classmethod
    def load(cls, input_file: Path, transcoder: RawTranscoder, **kwargs: Any) -> Self:
        """
        Loads the raw data from the input file.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        Args:
            input_file: The path to the input file.
            transcoder: The transcoder used to load the data.

        Returns:
            RawData: The loaded raw data.
        """

        return cls(transcoder.load(input_file, **kwargs), transcoder)


class ProcessedTranscoder(Transcoder):
    """
    Base class for all processed data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class ProcessedData(Data):
    """
    Base class for all processed data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: ProcessedTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

    @property
    def transcoder(self) -> ProcessedTranscoder:
        return cast(ProcessedTranscoder, self._transcoder)


class SummaryTranscoder(Transcoder):
    """
    Base class for all summary data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def save(
        self,
        output_file: Path,
        frame: pd.DataFrame,
        name: str = "Summary",
        **kwargs: Any,
    ) -> None:
        """
        Saves the summary frame to the output file.

        NOTE: This method can be overwritten in the child classes if the output file
                is not an Excel file.

        Args:
            output_file: The path to the output file.
            frame: The frame to save to the output file.
            name: The name by which the data will be referenced within the output file.
        """

        super().save(output_file, frame, name, **kwargs)


class SummaryData(Data):
    """
    Base class for all summary data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    @dataclasses.dataclass
    class Row:
        """
        Base class for all summary data rows.
        """

        pass

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: SummaryTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

    @property
    def transcoder(self) -> SummaryTranscoder:
        return cast(SummaryTranscoder, self._transcoder)

    def append_row(self, row: Row) -> None:
        """
        Append a row to the summary frame.

        Args:
            row: The row to append to the summary data.
        """

        # Create the row to append to the summary data
        frame_row = pd.DataFrame(
            {
                field.metadata.get("column_name", field.name): [getattr(row, field.name)]
                for field in dataclasses.fields(row)
            }
        )

        # Append the row to the summary data
        if self._frame.empty:
            self._frame = frame_row.copy(deep=True)
        else:
            self._frame = pd.concat([self._frame, frame_row], ignore_index=True)
        self._frame.reset_index(drop=True, inplace=True)

    def clear_all_rows(self) -> None:
        """
        Clears all rows in the summary data.
        """

        self._frame.drop(self._frame.index, inplace=True)  # type: ignore

    def get_transcoded_frame(self) -> pd.DataFrame:
        """
        Obtains the transcoded frame.

        Returns:
            pd.DataFrame: The transcoded frame.
        """

        transcoded_frame: pd.DataFrame = pd.DataFrame()

        for column in self.transcoder.columns.values():
            if column.name in self._frame.columns:
                transcoded_frame[column.output_name] = self._frame[column.name].apply(  # type: ignore
                    lambda x: convert_from_base_units(x, column.output_units)  # type: ignore
                )

        return transcoded_frame
