# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'view.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QTextBrowser, QWidget)

class Ui_w_Stepwise(object):
    def setupUi(self, w_Stepwise):
        if not w_Stepwise.objectName():
            w_Stepwise.setObjectName(u"w_Stepwise")
        w_Stepwise.resize(572, 153)
        self.gl_Stepwise = QGridLayout(w_Stepwise)
        self.gl_Stepwise.setObjectName(u"gl_Stepwise")
        self.l_RelaxationStrains = QLabel(w_Stepwise)
        self.l_RelaxationStrains.setObjectName(u"l_RelaxationStrains")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.l_RelaxationStrains.sizePolicy().hasHeightForWidth())
        self.l_RelaxationStrains.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.l_RelaxationStrains, 0, 0, 1, 1)

        self.sb_RelaxationStrainsIntervals = QSpinBox(w_Stepwise)
        self.sb_RelaxationStrainsIntervals.setObjectName(u"sb_RelaxationStrainsIntervals")

        self.gl_Stepwise.addWidget(self.sb_RelaxationStrainsIntervals, 0, 1, 1, 1)

        self.l_RelaxationStrainsText = QLabel(w_Stepwise)
        self.l_RelaxationStrainsText.setObjectName(u"l_RelaxationStrainsText")
        sizePolicy.setHeightForWidth(self.l_RelaxationStrainsText.sizePolicy().hasHeightForWidth())
        self.l_RelaxationStrainsText.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.l_RelaxationStrainsText, 0, 2, 1, 1)

        self.sb_RelaxationStrainsStart = QDoubleSpinBox(w_Stepwise)
        self.sb_RelaxationStrainsStart.setObjectName(u"sb_RelaxationStrainsStart")
        self.sb_RelaxationStrainsStart.setDecimals(1)

        self.gl_Stepwise.addWidget(self.sb_RelaxationStrainsStart, 0, 3, 1, 1)

        self.s_Horizontal = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gl_Stepwise.addItem(self.s_Horizontal, 0, 4, 9, 1)

        self.l_Epsilon = QLabel(w_Stepwise)
        self.l_Epsilon.setObjectName(u"l_Epsilon")
        sizePolicy.setHeightForWidth(self.l_Epsilon.sizePolicy().hasHeightForWidth())
        self.l_Epsilon.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.l_Epsilon, 1, 0, 1, 1)

        self.sb_Epsilon = QDoubleSpinBox(w_Stepwise)
        self.sb_Epsilon.setObjectName(u"sb_Epsilon")
        self.sb_Epsilon.setMaximum(1.000000000000000)

        self.gl_Stepwise.addWidget(self.sb_Epsilon, 1, 1, 1, 1)

        self.cb_RegressionPoints = QCheckBox(w_Stepwise)
        self.cb_RegressionPoints.setObjectName(u"cb_RegressionPoints")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cb_RegressionPoints.sizePolicy().hasHeightForWidth())
        self.cb_RegressionPoints.setSizePolicy(sizePolicy1)

        self.gl_Stepwise.addWidget(self.cb_RegressionPoints, 2, 0, 1, 1)

        self.sb_RegressionPoints = QSpinBox(w_Stepwise)
        self.sb_RegressionPoints.setObjectName(u"sb_RegressionPoints")
        self.sb_RegressionPoints.setMaximum(100000)

        self.gl_Stepwise.addWidget(self.sb_RegressionPoints, 2, 1, 1, 1)

        self.s_VerticalProperties = QSpacerItem(0, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gl_Stepwise.addItem(self.s_VerticalProperties, 3, 0, 1, 4)

        self.cb_Properties = QCheckBox(w_Stepwise)
        self.cb_Properties.setObjectName(u"cb_Properties")
        sizePolicy.setHeightForWidth(self.cb_Properties.sizePolicy().hasHeightForWidth())
        self.cb_Properties.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.cb_Properties, 4, 0, 1, 1)

        self.l_Area = QLabel(w_Stepwise)
        self.l_Area.setObjectName(u"l_Area")
        sizePolicy.setHeightForWidth(self.l_Area.sizePolicy().hasHeightForWidth())
        self.l_Area.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.l_Area, 5, 0, 1, 1)

        self.sb_Area = QDoubleSpinBox(w_Stepwise)
        self.sb_Area.setObjectName(u"sb_Area")
        self.sb_Area.setDecimals(2)
        self.sb_Area.setMaximum(999999.989999999990687)
        self.sb_Area.setValue(0.000000000000000)

        self.gl_Stepwise.addWidget(self.sb_Area, 5, 1, 1, 1)

        self.cb_Area = QCheckBox(w_Stepwise)
        self.cb_Area.setObjectName(u"cb_Area")
        sizePolicy1.setHeightForWidth(self.cb_Area.sizePolicy().hasHeightForWidth())
        self.cb_Area.setSizePolicy(sizePolicy1)

        self.gl_Stepwise.addWidget(self.cb_Area, 5, 2, 1, 2)

        self.l_Length = QLabel(w_Stepwise)
        self.l_Length.setObjectName(u"l_Length")
        sizePolicy.setHeightForWidth(self.l_Length.sizePolicy().hasHeightForWidth())
        self.l_Length.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.l_Length, 6, 0, 1, 1)

        self.sb_Length = QDoubleSpinBox(w_Stepwise)
        self.sb_Length.setObjectName(u"sb_Length")
        self.sb_Length.setDecimals(2)
        self.sb_Length.setMaximum(999.990000000000009)
        self.sb_Length.setValue(0.000000000000000)

        self.gl_Stepwise.addWidget(self.sb_Length, 6, 1, 1, 1)

        self.cb_Length = QCheckBox(w_Stepwise)
        self.cb_Length.setObjectName(u"cb_Length")
        sizePolicy1.setHeightForWidth(self.cb_Length.sizePolicy().hasHeightForWidth())
        self.cb_Length.setSizePolicy(sizePolicy1)

        self.gl_Stepwise.addWidget(self.cb_Length, 6, 2, 1, 2)

        self.pb_ReadProperties = QPushButton(w_Stepwise)
        self.pb_ReadProperties.setObjectName(u"pb_ReadProperties")
        sizePolicy.setHeightForWidth(self.pb_ReadProperties.sizePolicy().hasHeightForWidth())
        self.pb_ReadProperties.setSizePolicy(sizePolicy)

        self.gl_Stepwise.addWidget(self.pb_ReadProperties, 7, 0, 1, 1)

        self.tb_ReadProperties = QTextBrowser(w_Stepwise)
        self.tb_ReadProperties.setObjectName(u"tb_ReadProperties")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tb_ReadProperties.sizePolicy().hasHeightForWidth())
        self.tb_ReadProperties.setSizePolicy(sizePolicy2)

        self.gl_Stepwise.addWidget(self.tb_ReadProperties, 7, 1, 1, 3)

        self.s_Vertical = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gl_Stepwise.addItem(self.s_Vertical, 8, 0, 1, 4)


        self.retranslateUi(w_Stepwise)

        QMetaObject.connectSlotsByName(w_Stepwise)
    # setupUi

    def retranslateUi(self, w_Stepwise):
#if QT_CONFIG(tooltip)
        self.l_RelaxationStrains.setToolTip(QCoreApplication.translate("w_Stepwise", u"The strains at which the sample has been configured to relax", None))
#endif // QT_CONFIG(tooltip)
        self.l_RelaxationStrains.setText(QCoreApplication.translate("w_Stepwise", u"Relaxation strains", None))
#if QT_CONFIG(tooltip)
        self.sb_RelaxationStrainsIntervals.setToolTip(QCoreApplication.translate("w_Stepwise", u"The number of intervals at which the sample has been configured to relax.  This in combination with the step size gives the relaxation strains.  For instance, if the step size is 5%, and the number of intervals is 6, then the experiment will relax the sample at 5%, 10%, 15%, 20%, 25%, 30%.", None))
#endif // QT_CONFIG(tooltip)
        self.l_RelaxationStrainsText.setText(QCoreApplication.translate("w_Stepwise", u"intervals, with step size", None))
#if QT_CONFIG(tooltip)
        self.sb_RelaxationStrainsStart.setToolTip(QCoreApplication.translate("w_Stepwise", u"The step between consecutive strains at which the sample has been configured to relax.  This in combination with the number of intervals gives the relaxation strains.  For instance, if the step size is 5%, and the number of intervals is 6, then the experiment will relax the sample at 5%, 10%, 15%, 20%, 25%, 30%.", None))
#endif // QT_CONFIG(tooltip)
        self.sb_RelaxationStrainsStart.setSuffix(QCoreApplication.translate("w_Stepwise", u"%", None))
#if QT_CONFIG(tooltip)
        self.l_Epsilon.setToolTip(QCoreApplication.translate("w_Stepwise", u"Allowable percentage tolerance on the strain for creating the dataset at the required relaxation strain", None))
#endif // QT_CONFIG(tooltip)
        self.l_Epsilon.setText(QCoreApplication.translate("w_Stepwise", u"Epsilon", None))
#if QT_CONFIG(tooltip)
        self.sb_Epsilon.setToolTip(QCoreApplication.translate("w_Stepwise", u"Allowable percentage tolerance on the strain for creating the dataset at the required relaxation strain", None))
#endif // QT_CONFIG(tooltip)
        self.sb_Epsilon.setSuffix(QCoreApplication.translate("w_Stepwise", u"%", None))
#if QT_CONFIG(tooltip)
        self.cb_RegressionPoints.setToolTip(QCoreApplication.translate("w_Stepwise", u"If unchecked, all datapoints will be used in the regression analysis", None))
#endif // QT_CONFIG(tooltip)
        self.cb_RegressionPoints.setText(QCoreApplication.translate("w_Stepwise", u"Regression points", None))
#if QT_CONFIG(tooltip)
        self.sb_RegressionPoints.setToolTip(QCoreApplication.translate("w_Stepwise", u"Number of data points to include in the regression analysis", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.cb_Properties.setToolTip(QCoreApplication.translate("w_Stepwise", u"The physical properties of the experiment samples.  If checked, the selected properties will be read from the file", None))
#endif // QT_CONFIG(tooltip)
        self.cb_Properties.setText(QCoreApplication.translate("w_Stepwise", u"Physical properties", None))
#if QT_CONFIG(tooltip)
        self.l_Area.setToolTip(QCoreApplication.translate("w_Stepwise", u"The cross-sectional area of the samples.  It is A in the equation \u03c3 = F / A", None))
#endif // QT_CONFIG(tooltip)
        self.l_Area.setText(QCoreApplication.translate("w_Stepwise", u"Cross-sectional area", None))
#if QT_CONFIG(tooltip)
        self.sb_Area.setToolTip(QCoreApplication.translate("w_Stepwise", u"The cross-sectional area of every sample.  It is A in the equation \u03c3 = F / A", None))
#endif // QT_CONFIG(tooltip)
        self.sb_Area.setSuffix(QCoreApplication.translate("w_Stepwise", u"mm\u00b2", None))
#if QT_CONFIG(tooltip)
        self.cb_Area.setToolTip(QCoreApplication.translate("w_Stepwise", u"If checked, the cross-sectional area will be read in from the file on a sample-by-sample basis.  Otherwise, the specified cross-sectional area will be used by all samples", None))
#endif // QT_CONFIG(tooltip)
        self.cb_Area.setText(QCoreApplication.translate("w_Stepwise", u"Read from file", None))
#if QT_CONFIG(tooltip)
        self.l_Length.setToolTip(QCoreApplication.translate("w_Stepwise", u"The initial length of the samples.  It is l0 in the equation \u03b5 = d / l0", None))
#endif // QT_CONFIG(tooltip)
        self.l_Length.setText(QCoreApplication.translate("w_Stepwise", u"Initial length", None))
#if QT_CONFIG(tooltip)
        self.sb_Length.setToolTip(QCoreApplication.translate("w_Stepwise", u"The initial length of every sample.  It is l in the equation \u03b5 = d / l0", None))
#endif // QT_CONFIG(tooltip)
        self.sb_Length.setSuffix(QCoreApplication.translate("w_Stepwise", u"mm", None))
#if QT_CONFIG(tooltip)
        self.cb_Length.setToolTip(QCoreApplication.translate("w_Stepwise", u"If checked, the initial length will be read in from the file on a sample-by-sample basis.  Otherwise, the specified initial length will be used by all samples", None))
#endif // QT_CONFIG(tooltip)
        self.cb_Length.setText(QCoreApplication.translate("w_Stepwise", u"Read from file", None))
#if QT_CONFIG(tooltip)
        self.pb_ReadProperties.setToolTip(QCoreApplication.translate("w_Stepwise", u"Select the file from which the physical sample properties will be read.", None))
#endif // QT_CONFIG(tooltip)
        self.pb_ReadProperties.setText(QCoreApplication.translate("w_Stepwise", u"Read from...", None))
#if QT_CONFIG(tooltip)
        self.tb_ReadProperties.setToolTip(QCoreApplication.translate("w_Stepwise", u"File from which the physical sample properties will be read.", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

