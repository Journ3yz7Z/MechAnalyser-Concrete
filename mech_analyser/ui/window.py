# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QHeaderView, QLabel, QMainWindow, QMenu,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextBrowser, QTreeWidget, QTreeWidgetItem,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.a_OpenDirectory = QAction(MainWindow)
        self.a_OpenDirectory.setObjectName(u"a_OpenDirectory")
        self.a_OpenCsvs = QAction(MainWindow)
        self.a_OpenCsvs.setObjectName(u"a_OpenCsvs")
        self.a_Documentation = QAction(MainWindow)
        self.a_Documentation.setObjectName(u"a_Documentation")
        self.a_Version = QAction(MainWindow)
        self.a_Version.setObjectName(u"a_Version")
        self.tw_Main = QTabWidget(MainWindow)
        self.tw_Main.setObjectName(u"tw_Main")
        self.t_Files = QWidget()
        self.t_Files.setObjectName(u"t_Files")
        self.gl_Files = QGridLayout(self.t_Files)
        self.gl_Files.setObjectName(u"gl_Files")
        self.pb_SaveAnalysis = QPushButton(self.t_Files)
        self.pb_SaveAnalysis.setObjectName(u"pb_SaveAnalysis")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_SaveAnalysis.sizePolicy().hasHeightForWidth())
        self.pb_SaveAnalysis.setSizePolicy(sizePolicy)

        self.gl_Files.addWidget(self.pb_SaveAnalysis, 0, 0, 1, 1)

        self.tb_SaveAnalysis = QTextBrowser(self.t_Files)
        self.tb_SaveAnalysis.setObjectName(u"tb_SaveAnalysis")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tb_SaveAnalysis.sizePolicy().hasHeightForWidth())
        self.tb_SaveAnalysis.setSizePolicy(sizePolicy1)

        self.gl_Files.addWidget(self.tb_SaveAnalysis, 0, 1, 1, 4)

        self.pb_SaveCollation = QPushButton(self.t_Files)
        self.pb_SaveCollation.setObjectName(u"pb_SaveCollation")
        sizePolicy.setHeightForWidth(self.pb_SaveCollation.sizePolicy().hasHeightForWidth())
        self.pb_SaveCollation.setSizePolicy(sizePolicy)

        self.gl_Files.addWidget(self.pb_SaveCollation, 1, 0, 1, 1)

        self.tb_SaveCollation = QTextBrowser(self.t_Files)
        self.tb_SaveCollation.setObjectName(u"tb_SaveCollation")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tb_SaveCollation.sizePolicy().hasHeightForWidth())
        self.tb_SaveCollation.setSizePolicy(sizePolicy2)

        self.gl_Files.addWidget(self.tb_SaveCollation, 1, 1, 1, 4)

        self.tbl_Files = QTableWidget(self.t_Files)
        if (self.tbl_Files.columnCount() < 4):
            self.tbl_Files.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tbl_Files.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tbl_Files.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tbl_Files.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tbl_Files.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tbl_Files.setObjectName(u"tbl_Files")
        self.tbl_Files.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_Files.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_Files.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_Files.setRowCount(0)
        self.tbl_Files.setColumnCount(4)
        self.tbl_Files.horizontalHeader().setVisible(True)
        self.tbl_Files.horizontalHeader().setStretchLastSection(True)

        self.gl_Files.addWidget(self.tbl_Files, 2, 0, 1, 5)

        self.pb_Clear = QPushButton(self.t_Files)
        self.pb_Clear.setObjectName(u"pb_Clear")

        self.gl_Files.addWidget(self.pb_Clear, 3, 0, 1, 1)

        self.s_FilesHorizontal = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gl_Files.addItem(self.s_FilesHorizontal, 3, 1, 1, 1)

        self.pb_EditOutput = QPushButton(self.t_Files)
        self.pb_EditOutput.setObjectName(u"pb_EditOutput")
        sizePolicy.setHeightForWidth(self.pb_EditOutput.sizePolicy().hasHeightForWidth())
        self.pb_EditOutput.setSizePolicy(sizePolicy)

        self.gl_Files.addWidget(self.pb_EditOutput, 3, 2, 1, 1)

        self.pb_EditGroup = QPushButton(self.t_Files)
        self.pb_EditGroup.setObjectName(u"pb_EditGroup")
        sizePolicy.setHeightForWidth(self.pb_EditGroup.sizePolicy().hasHeightForWidth())
        self.pb_EditGroup.setSizePolicy(sizePolicy)

        self.gl_Files.addWidget(self.pb_EditGroup, 3, 3, 1, 1)

        self.pb_EditSample = QPushButton(self.t_Files)
        self.pb_EditSample.setObjectName(u"pb_EditSample")
        sizePolicy.setHeightForWidth(self.pb_EditSample.sizePolicy().hasHeightForWidth())
        self.pb_EditSample.setSizePolicy(sizePolicy)

        self.gl_Files.addWidget(self.pb_EditSample, 3, 4, 1, 1)

        self.tw_Main.addTab(self.t_Files, "")
        self.t_Configuration = QWidget()
        self.t_Configuration.setObjectName(u"t_Configuration")
        self.gl_Configuration = QGridLayout(self.t_Configuration)
        self.gl_Configuration.setObjectName(u"gl_Configuration")
        self.l_Instrument = QLabel(self.t_Configuration)
        self.l_Instrument.setObjectName(u"l_Instrument")
        sizePolicy.setHeightForWidth(self.l_Instrument.sizePolicy().hasHeightForWidth())
        self.l_Instrument.setSizePolicy(sizePolicy)

        self.gl_Configuration.addWidget(self.l_Instrument, 0, 0, 1, 1)

        self.cb_Instrument = QComboBox(self.t_Configuration)
        self.cb_Instrument.setObjectName(u"cb_Instrument")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.cb_Instrument.sizePolicy().hasHeightForWidth())
        self.cb_Instrument.setSizePolicy(sizePolicy3)

        self.gl_Configuration.addWidget(self.cb_Instrument, 0, 1, 1, 1)

        self.l_Experiment = QLabel(self.t_Configuration)
        self.l_Experiment.setObjectName(u"l_Experiment")
        sizePolicy.setHeightForWidth(self.l_Experiment.sizePolicy().hasHeightForWidth())
        self.l_Experiment.setSizePolicy(sizePolicy)

        self.gl_Configuration.addWidget(self.l_Experiment, 0, 2, 1, 1)

        self.cb_Experiment = QComboBox(self.t_Configuration)
        self.cb_Experiment.setObjectName(u"cb_Experiment")
        sizePolicy3.setHeightForWidth(self.cb_Experiment.sizePolicy().hasHeightForWidth())
        self.cb_Experiment.setSizePolicy(sizePolicy3)

        self.gl_Configuration.addWidget(self.cb_Experiment, 0, 3, 1, 1)

        self.s_MainHorizontal = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gl_Configuration.addItem(self.s_MainHorizontal, 0, 4, 1, 1)

        self.sw_Configuration = QStackedWidget(self.t_Configuration)
        self.sw_Configuration.setObjectName(u"sw_Configuration")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.sw_Configuration.sizePolicy().hasHeightForWidth())
        self.sw_Configuration.setSizePolicy(sizePolicy4)

        self.gl_Configuration.addWidget(self.sw_Configuration, 1, 0, 1, 5)

        self.l_Transcoder = QLabel(self.t_Configuration)
        self.l_Transcoder.setObjectName(u"l_Transcoder")

        self.gl_Configuration.addWidget(self.l_Transcoder, 2, 0, 1, 1)

        self.cb_Transcoder = QComboBox(self.t_Configuration)
        self.cb_Transcoder.addItem("")
        self.cb_Transcoder.addItem("")
        self.cb_Transcoder.addItem("")
        self.cb_Transcoder.setObjectName(u"cb_Transcoder")
        sizePolicy3.setHeightForWidth(self.cb_Transcoder.sizePolicy().hasHeightForWidth())
        self.cb_Transcoder.setSizePolicy(sizePolicy3)

        self.gl_Configuration.addWidget(self.cb_Transcoder, 2, 1, 1, 1)

        self.sw_Transcoder = QStackedWidget(self.t_Configuration)
        self.sw_Transcoder.setObjectName(u"sw_Transcoder")
        sizePolicy4.setHeightForWidth(self.sw_Transcoder.sizePolicy().hasHeightForWidth())
        self.sw_Transcoder.setSizePolicy(sizePolicy4)
        self.w_RawTranscoder = QWidget()
        self.w_RawTranscoder.setObjectName(u"w_RawTranscoder")
        self.gl_RawTranscoder = QGridLayout(self.w_RawTranscoder)
        self.gl_RawTranscoder.setObjectName(u"gl_RawTranscoder")
        self.tbl_RawTranscoder = QTableWidget(self.w_RawTranscoder)
        if (self.tbl_RawTranscoder.columnCount() < 11):
            self.tbl_RawTranscoder.setColumnCount(11)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(4, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(5, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(6, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(7, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(8, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(9, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tbl_RawTranscoder.setHorizontalHeaderItem(10, __qtablewidgetitem14)
        self.tbl_RawTranscoder.setObjectName(u"tbl_RawTranscoder")
        self.tbl_RawTranscoder.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_RawTranscoder.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tbl_RawTranscoder.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.tbl_RawTranscoder.setRowCount(0)
        self.tbl_RawTranscoder.setColumnCount(11)
        self.tbl_RawTranscoder.horizontalHeader().setVisible(True)
        self.tbl_RawTranscoder.horizontalHeader().setStretchLastSection(True)

        self.gl_RawTranscoder.addWidget(self.tbl_RawTranscoder, 0, 0, 1, 1)

        self.sw_Transcoder.addWidget(self.w_RawTranscoder)
        self.w_ProcessedTranscoder = QWidget()
        self.w_ProcessedTranscoder.setObjectName(u"w_ProcessedTranscoder")
        self.gl_ProcessedTranscoder = QGridLayout(self.w_ProcessedTranscoder)
        self.gl_ProcessedTranscoder.setObjectName(u"gl_ProcessedTranscoder")
        self.tbl_ProcessedTranscoder = QTableWidget(self.w_ProcessedTranscoder)
        if (self.tbl_ProcessedTranscoder.columnCount() < 6):
            self.tbl_ProcessedTranscoder.setColumnCount(6)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tbl_ProcessedTranscoder.setHorizontalHeaderItem(0, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tbl_ProcessedTranscoder.setHorizontalHeaderItem(1, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tbl_ProcessedTranscoder.setHorizontalHeaderItem(2, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tbl_ProcessedTranscoder.setHorizontalHeaderItem(3, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tbl_ProcessedTranscoder.setHorizontalHeaderItem(4, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tbl_ProcessedTranscoder.setHorizontalHeaderItem(5, __qtablewidgetitem20)
        self.tbl_ProcessedTranscoder.setObjectName(u"tbl_ProcessedTranscoder")
        self.tbl_ProcessedTranscoder.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_ProcessedTranscoder.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tbl_ProcessedTranscoder.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.tbl_ProcessedTranscoder.setRowCount(0)
        self.tbl_ProcessedTranscoder.setColumnCount(6)
        self.tbl_ProcessedTranscoder.horizontalHeader().setVisible(True)
        self.tbl_ProcessedTranscoder.horizontalHeader().setStretchLastSection(True)

        self.gl_ProcessedTranscoder.addWidget(self.tbl_ProcessedTranscoder, 0, 0, 1, 1)

        self.sw_Transcoder.addWidget(self.w_ProcessedTranscoder)
        self.w_SummaryTranscoder = QWidget()
        self.w_SummaryTranscoder.setObjectName(u"w_SummaryTranscoder")
        self.gl_SummaryTranscoder = QGridLayout(self.w_SummaryTranscoder)
        self.gl_SummaryTranscoder.setObjectName(u"gl_SummaryTranscoder")
        self.tbl_SummaryTranscoder = QTableWidget(self.w_SummaryTranscoder)
        if (self.tbl_SummaryTranscoder.columnCount() < 6):
            self.tbl_SummaryTranscoder.setColumnCount(6)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tbl_SummaryTranscoder.setHorizontalHeaderItem(0, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tbl_SummaryTranscoder.setHorizontalHeaderItem(1, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tbl_SummaryTranscoder.setHorizontalHeaderItem(2, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tbl_SummaryTranscoder.setHorizontalHeaderItem(3, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tbl_SummaryTranscoder.setHorizontalHeaderItem(4, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.tbl_SummaryTranscoder.setHorizontalHeaderItem(5, __qtablewidgetitem26)
        self.tbl_SummaryTranscoder.setObjectName(u"tbl_SummaryTranscoder")
        self.tbl_SummaryTranscoder.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_SummaryTranscoder.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tbl_SummaryTranscoder.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.tbl_SummaryTranscoder.setRowCount(0)
        self.tbl_SummaryTranscoder.setColumnCount(6)
        self.tbl_SummaryTranscoder.horizontalHeader().setVisible(True)
        self.tbl_SummaryTranscoder.horizontalHeader().setStretchLastSection(True)

        self.gl_SummaryTranscoder.addWidget(self.tbl_SummaryTranscoder, 0, 0, 1, 1)

        self.sw_Transcoder.addWidget(self.w_SummaryTranscoder)

        self.gl_Configuration.addWidget(self.sw_Transcoder, 3, 0, 1, 5)

        self.tw_Main.addTab(self.t_Configuration, "")
        self.t_Output = QWidget()
        self.t_Output.setObjectName(u"t_Output")
        self.gl_Output = QGridLayout(self.t_Output)
        self.gl_Output.setObjectName(u"gl_Output")
        self.tree_Output = QTreeWidget(self.t_Output)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_Output.setHeaderItem(__qtreewidgetitem)
        self.tree_Output.setObjectName(u"tree_Output")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.tree_Output.sizePolicy().hasHeightForWidth())
        self.tree_Output.setSizePolicy(sizePolicy5)
        self.tree_Output.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_Output.setColumnCount(1)
        self.tree_Output.header().setVisible(False)

        self.gl_Output.addWidget(self.tree_Output, 0, 0, 1, 3)

        self.sw_Output = QStackedWidget(self.t_Output)
        self.sw_Output.setObjectName(u"sw_Output")
        sizePolicy4.setHeightForWidth(self.sw_Output.sizePolicy().hasHeightForWidth())
        self.sw_Output.setSizePolicy(sizePolicy4)

        self.gl_Output.addWidget(self.sw_Output, 0, 3, 2, 1)

        self.pgb_Output = QProgressBar(self.t_Output)
        self.pgb_Output.setObjectName(u"pgb_Output")
        self.pgb_Output.setValue(0)

        self.gl_Output.addWidget(self.pgb_Output, 1, 0, 1, 1)

        self.pb_Cancel = QPushButton(self.t_Output)
        self.pb_Cancel.setObjectName(u"pb_Cancel")

        self.gl_Output.addWidget(self.pb_Cancel, 1, 1, 1, 1)

        self.pb_Run = QPushButton(self.t_Output)
        self.pb_Run.setObjectName(u"pb_Run")

        self.gl_Output.addWidget(self.pb_Run, 1, 2, 1, 1)

        self.tw_Main.addTab(self.t_Output, "")
        MainWindow.setCentralWidget(self.tw_Main)
        self.mb_Main = QMenuBar(MainWindow)
        self.mb_Main.setObjectName(u"mb_Main")
        self.mb_Main.setGeometry(QRect(0, 0, 800, 24))
        self.m_File = QMenu(self.mb_Main)
        self.m_File.setObjectName(u"m_File")
        self.m_Help = QMenu(self.mb_Main)
        self.m_Help.setObjectName(u"m_Help")
        MainWindow.setMenuBar(self.mb_Main)
        QWidget.setTabOrder(self.tbl_Files, self.cb_Instrument)
        QWidget.setTabOrder(self.cb_Instrument, self.cb_Experiment)

        self.mb_Main.addAction(self.m_File.menuAction())
        self.mb_Main.addAction(self.m_Help.menuAction())
        self.m_File.addAction(self.a_OpenDirectory)
        self.m_File.addAction(self.a_OpenCsvs)
        self.m_Help.addAction(self.a_Documentation)
        self.m_Help.addSeparator()
        self.m_Help.addAction(self.a_Version)

        self.retranslateUi(MainWindow)

        self.tw_Main.setCurrentIndex(0)
        self.sw_Configuration.setCurrentIndex(-1)
        self.sw_Transcoder.setCurrentIndex(0)
        self.sw_Output.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MechAnalyser", None))
        self.a_OpenDirectory.setText(QCoreApplication.translate("MainWindow", u"Open directory...", None))
        self.a_OpenCsvs.setText(QCoreApplication.translate("MainWindow", u"Open CSVs...", None))
        self.a_Documentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
        self.a_Version.setText(QCoreApplication.translate("MainWindow", u"Version", None))
#if QT_CONFIG(tooltip)
        self.pb_SaveAnalysis.setToolTip(QCoreApplication.translate("MainWindow", u"Select the directory to which all analysis outputs will be saved.  By default, the analysis corresponding to the input CSVs will be saved in the same directory as the CSVs.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_SaveAnalysis.setText(QCoreApplication.translate("MainWindow", u"Save analysis to...", None))
#if QT_CONFIG(tooltip)
        self.tb_SaveAnalysis.setToolTip(QCoreApplication.translate("MainWindow", u"Directory to which all analysis outputs will be saved.  If it is blank, the analysis corresponding to the input CSVs will be saved in the same directory as the CSVs.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pb_SaveCollation.setToolTip(QCoreApplication.translate("MainWindow", u"Select the file to which the collated raw data and summaries will be saved.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_SaveCollation.setText(QCoreApplication.translate("MainWindow", u"Save collation to...", None))
#if QT_CONFIG(tooltip)
        self.tb_SaveCollation.setToolTip(QCoreApplication.translate("MainWindow", u"File to which the collated raw data and summaries will be saved.", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem = self.tbl_Files.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Input .csv", None));
        ___qtablewidgetitem1 = self.tbl_Files.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Output .xlsx", None));
        ___qtablewidgetitem2 = self.tbl_Files.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Group name", None));
        ___qtablewidgetitem3 = self.tbl_Files.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Sample name", None));
        self.pb_Clear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
#if QT_CONFIG(tooltip)
        self.pb_EditOutput.setToolTip(QCoreApplication.translate("MainWindow", u"Edit the output filename of the Excel file to which the analysis will be written.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_EditOutput.setText(QCoreApplication.translate("MainWindow", u"Edit output...", None))
#if QT_CONFIG(tooltip)
        self.pb_EditGroup.setToolTip(QCoreApplication.translate("MainWindow", u"Edit the group to which the sample belongs.  The summaries of all samples in the same group will be collated into the same sheet within the collated Excel spreadsheet.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_EditGroup.setText(QCoreApplication.translate("MainWindow", u"Edit group...", None))
#if QT_CONFIG(tooltip)
        self.pb_EditSample.setToolTip(QCoreApplication.translate("MainWindow", u"Edit the name of the sample.  If multiple samples are selected, then the given sample name will be applied to each with a numerical suffix to uniquely identify each.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_EditSample.setText(QCoreApplication.translate("MainWindow", u"Edit sample...", None))
        self.tw_Main.setTabText(self.tw_Main.indexOf(self.t_Files), QCoreApplication.translate("MainWindow", u"Files", None))
        self.l_Instrument.setText(QCoreApplication.translate("MainWindow", u"Instrument:", None))
        self.l_Experiment.setText(QCoreApplication.translate("MainWindow", u"Experiment:", None))
#if QT_CONFIG(tooltip)
        self.l_Transcoder.setToolTip(QCoreApplication.translate("MainWindow", u"Configure the transcoder settings for the raw data input, raw data output, processed data output, and summary data output", None))
#endif // QT_CONFIG(tooltip)
        self.l_Transcoder.setText(QCoreApplication.translate("MainWindow", u"Transcoder:", None))
        self.cb_Transcoder.setItemText(0, QCoreApplication.translate("MainWindow", u"Raw", None))
        self.cb_Transcoder.setItemText(1, QCoreApplication.translate("MainWindow", u"Processed", None))
        self.cb_Transcoder.setItemText(2, QCoreApplication.translate("MainWindow", u"Summary", None))

#if QT_CONFIG(tooltip)
        self.w_RawTranscoder.setToolTip(QCoreApplication.translate("MainWindow", u"Configure the raw data input and output transcoder settings", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem4 = self.tbl_RawTranscoder.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Name", None));
        ___qtablewidgetitem5 = self.tbl_RawTranscoder.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Input Included", None));
        ___qtablewidgetitem6 = self.tbl_RawTranscoder.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Input Name", None));
        ___qtablewidgetitem7 = self.tbl_RawTranscoder.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Input Units", None));
        ___qtablewidgetitem8 = self.tbl_RawTranscoder.horizontalHeaderItem(4)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Input Row", None));
        ___qtablewidgetitem9 = self.tbl_RawTranscoder.horizontalHeaderItem(5)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"Input Column", None));
        ___qtablewidgetitem10 = self.tbl_RawTranscoder.horizontalHeaderItem(6)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"Output Included", None));
        ___qtablewidgetitem11 = self.tbl_RawTranscoder.horizontalHeaderItem(7)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"Output Name", None));
        ___qtablewidgetitem12 = self.tbl_RawTranscoder.horizontalHeaderItem(8)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"Output Units", None));
        ___qtablewidgetitem13 = self.tbl_RawTranscoder.horizontalHeaderItem(9)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"Output Column", None));
        ___qtablewidgetitem14 = self.tbl_RawTranscoder.horizontalHeaderItem(10)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"Collate", None));
#if QT_CONFIG(tooltip)
        self.w_ProcessedTranscoder.setToolTip(QCoreApplication.translate("MainWindow", u"Configure the processed data output transcoder settings", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem15 = self.tbl_ProcessedTranscoder.horizontalHeaderItem(0)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"Name", None));
        ___qtablewidgetitem16 = self.tbl_ProcessedTranscoder.horizontalHeaderItem(1)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"Output Included", None));
        ___qtablewidgetitem17 = self.tbl_ProcessedTranscoder.horizontalHeaderItem(2)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"Output Name", None));
        ___qtablewidgetitem18 = self.tbl_ProcessedTranscoder.horizontalHeaderItem(3)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"Units", None));
        ___qtablewidgetitem19 = self.tbl_ProcessedTranscoder.horizontalHeaderItem(4)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"Column", None));
        ___qtablewidgetitem20 = self.tbl_ProcessedTranscoder.horizontalHeaderItem(5)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"Collate", None));
#if QT_CONFIG(tooltip)
        self.w_SummaryTranscoder.setToolTip(QCoreApplication.translate("MainWindow", u"Configure the summary data output transcoder settings", None))
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem21 = self.tbl_SummaryTranscoder.horizontalHeaderItem(0)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"Name", None));
        ___qtablewidgetitem22 = self.tbl_SummaryTranscoder.horizontalHeaderItem(1)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"Output Included", None));
        ___qtablewidgetitem23 = self.tbl_SummaryTranscoder.horizontalHeaderItem(2)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"Output Name", None));
        ___qtablewidgetitem24 = self.tbl_SummaryTranscoder.horizontalHeaderItem(3)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainWindow", u"Units", None));
        ___qtablewidgetitem25 = self.tbl_SummaryTranscoder.horizontalHeaderItem(4)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainWindow", u"Column", None));
        ___qtablewidgetitem26 = self.tbl_SummaryTranscoder.horizontalHeaderItem(5)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("MainWindow", u"Collate", None));
        self.tw_Main.setTabText(self.tw_Main.indexOf(self.t_Configuration), QCoreApplication.translate("MainWindow", u"Configuration", None))
#if QT_CONFIG(tooltip)
        self.pb_Cancel.setToolTip(QCoreApplication.translate("MainWindow", u"Cancel the running analysis and collation.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_Cancel.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.pb_Run.setToolTip(QCoreApplication.translate("MainWindow", u"Run the analysis on all samples and collate the raw data and summaries of each.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_Run.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.tw_Main.setTabText(self.tw_Main.indexOf(self.t_Output), QCoreApplication.translate("MainWindow", u"Output", None))
        self.m_File.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.m_Help.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

