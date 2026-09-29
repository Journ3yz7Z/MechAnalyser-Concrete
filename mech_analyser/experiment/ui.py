from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QStackedWidget, QTableView, QVBoxLayout, QWidget
import mech_analyser.experiment.analyser as ma_analyser
import mech_analyser.experiment.data as ma_data
import mech_analyser.study.sample as ma_sample
import pandas as pd
import pyqtgraph as pg  # type: ignore
from typing import Protocol, Optional


class ViewBase(Protocol):
    """
    Structural subtype base class for generated user interface widgets.
    """

    def setupUi(self, parent: QWidget) -> None: ...
    def retranslateUi(self, parent: QWidget) -> None: ...


class Widget(QWidget):
    """
    Base class for all user interface widgets.
    """

    def __init__(self) -> None:
        super().__init__()

    def activate(self, viewer: QStackedWidget) -> None:
        """
        Activates and displays the widget within the viewer.

        Args:
            viewer: The viewer in which to display the widget.
        """

        viewer.setCurrentWidget(self)


class ConfigWidget(Widget):
    """
    Base class for all user interface configuration widgets.

    Args:
        view: Generated user interface configuration widget.
        parameters: The parameters to use when analysing the experiment.
    """

    def __init__(self, view: ViewBase, parameters: ma_analyser.Parameters) -> None:
        super().__init__()

        self._view: ViewBase = view
        self._parameters: ma_analyser.Parameters = parameters

        self.view.setupUi(self)

    @property
    def parameters(self) -> ma_analyser.Parameters:
        return self._parameters

    @property
    def view(self) -> ViewBase:
        return self._view

    def create_analyser(
        self,
        sample: ma_sample.Sample,
        raw_transcoder: ma_data.RawTranscoder,
        processed_transcoder: ma_data.ProcessedTranscoder,
        summary_transcoder: ma_data.SummaryTranscoder,
    ) -> None:
        """
        Creates the experiment analyser.

        Args:
            sample: The sample being tested in the experiment.
            raw_transcoder: The raw data transcoder.
            processed_transcoder: The processed data transcoder.
            summary_transcoder: The summary data transcoder.
        """

        raise NotImplementedError

    def init(self) -> None:
        """
        Initialises the widget by setting the input fields to the defaults of
        the parameters to use when analysing the experiment and connecting any
        signals with an associated slot.

        NOTE: this is an abstract method that will be overwritten in the child
              classes.
        """

        raise NotImplementedError

    def sync_parameters(self) -> None:
        """
        Synchronise the parameters to use when analysing the experiment with the
        widget input fields.

        NOTE: this is an abstract method that will be overwritten in the child
              classes.
        """

        raise NotImplementedError


class TableWidget(Widget):
    """
    Base class for all user interface table widgets.

    Args:
        frame: Underlying pd.DataFrame representation of the table.
    """

    def __init__(self, frame: pd.DataFrame) -> None:
        super().__init__()

        # Create the table viewer
        table = QTableView()
        table.setModel(self.Model(frame))

        # Add the table viewer to the widget
        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)

    class Model(QAbstractTableModel):
        """
        Model for displaying a pandas DataFrame in a QTableView.

        Args:
            frame: Underlying pd.DataFrame representation of the data to be
                displayed.
        """

        def __init__(self, frame: pd.DataFrame) -> None:
            super().__init__()

            self._frame: pd.DataFrame = frame

        def columnCount(
            self,
            parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
        ) -> int:
            """
            Returns the number of columns in the underlying pd.DataFrame
            representation of the data.

            Args:
                parent: Required by the Qt model interface (not used here).

            Returns:
                Number of columns in the underlying pd.DataFrame representation of
                the data.
            """

            return len(self._frame.columns)

        def data(
            self,
            index: QModelIndex | QPersistentModelIndex,
            role: int = Qt.ItemDataRole.DisplayRole,
        ) -> str | None:
            """
            Returns the data to be displayed in the table for the given index and
            role.

            Args:
                index: The cell index (row, column).
                role: The role for which the data is requested.

            Returns:
                str: The string representation of the underlying pd.DataFrame
                    representation of the data value for display.
                None: If the role is not DisplayRole.
            """

            if role != Qt.ItemDataRole.DisplayRole:
                return None

            return str(self._frame.iloc[index.row(), index.column()])

        def headerData(
            self,
            section: int,
            orientation: Qt.Orientation,
            role: int = Qt.ItemDataRole.DisplayRole,
        ) -> Optional[str]:
            """
            Returns the header label for the given section and orientation.

            Args:
                section: The index of the header section.
                orientation: Horizontal (column) or Vertical (row) header.
                role: The role for which the header data is requested.

            Returns:
                str: The column name or row index as a string.
                None: If role is not DisplayRole.
            """

            if role != Qt.ItemDataRole.DisplayRole:
                return None
            elif orientation == Qt.Orientation.Horizontal:
                return self._frame.columns[section]
            else:
                return self._frame.index[section]  # type: ignore

        def rowCount(
            self,
            parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
        ) -> int:
            """
            Returns the number of rows in the underlying pd.DataFrame representation
            of the data.

            Args:
                parent: Required by the Qt model interface (not used here).

            Returns:
                Number of rows in the underlying pd.DataFrame representation of the
                data.
            """

            return len(self._frame)


class PlotWidget(Widget):
    """
    Base class for all user interface plot widgets.

    Args:
        plot: The plot object to be displayed.
    """

    def __init__(self, plot: pg.PlotWidget) -> None:
        super().__init__()

        # Add the table viewer to the widget
        layout = QVBoxLayout()
        layout.addWidget(plot)
        self.setLayout(layout)
