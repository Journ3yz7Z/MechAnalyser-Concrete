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
    QLabel, QSizePolicy, QSpacerItem, QSpinBox,
    QWidget)

class Ui_w_Microindentation(object):
    def setupUi(self, w_Microindentation):
        if not w_Microindentation.objectName():
            w_Microindentation.setObjectName(u"w_Microindentation")
        w_Microindentation.resize(612, 363)
        self.gl_Microindentation = QGridLayout(w_Microindentation)
        self.gl_Microindentation.setObjectName(u"gl_Microindentation")
        self.l_Cycles = QLabel(w_Microindentation)
        self.l_Cycles.setObjectName(u"l_Cycles")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.l_Cycles.sizePolicy().hasHeightForWidth())
        self.l_Cycles.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_Cycles, 0, 0, 1, 1)

        self.sb_Cycles = QSpinBox(w_Microindentation)
        self.sb_Cycles.setObjectName(u"sb_Cycles")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sb_Cycles.sizePolicy().hasHeightForWidth())
        self.sb_Cycles.setSizePolicy(sizePolicy1)
        self.sb_Cycles.setMaximum(999)

        self.gl_Microindentation.addWidget(self.sb_Cycles, 0, 1, 1, 1)

        self.s_Horizontal = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gl_Microindentation.addItem(self.s_Horizontal, 0, 2, 10, 1)

        self.l_SamplesToSkip = QLabel(w_Microindentation)
        self.l_SamplesToSkip.setObjectName(u"l_SamplesToSkip")
        sizePolicy.setHeightForWidth(self.l_SamplesToSkip.sizePolicy().hasHeightForWidth())
        self.l_SamplesToSkip.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_SamplesToSkip, 1, 0, 1, 1)

        self.sb_SamplesToSkip = QSpinBox(w_Microindentation)
        self.sb_SamplesToSkip.setObjectName(u"sb_SamplesToSkip")
        sizePolicy1.setHeightForWidth(self.sb_SamplesToSkip.sizePolicy().hasHeightForWidth())
        self.sb_SamplesToSkip.setSizePolicy(sizePolicy1)
        self.sb_SamplesToSkip.setMaximum(999)

        self.gl_Microindentation.addWidget(self.sb_SamplesToSkip, 1, 1, 1, 1)

        self.l_IndenterRadius = QLabel(w_Microindentation)
        self.l_IndenterRadius.setObjectName(u"l_IndenterRadius")
        sizePolicy.setHeightForWidth(self.l_IndenterRadius.sizePolicy().hasHeightForWidth())
        self.l_IndenterRadius.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_IndenterRadius, 2, 0, 1, 1)

        self.sb_IndenterRadius = QDoubleSpinBox(w_Microindentation)
        self.sb_IndenterRadius.setObjectName(u"sb_IndenterRadius")
        sizePolicy1.setHeightForWidth(self.sb_IndenterRadius.sizePolicy().hasHeightForWidth())
        self.sb_IndenterRadius.setSizePolicy(sizePolicy1)
        self.sb_IndenterRadius.setMaximum(10000.000000000000000)

        self.gl_Microindentation.addWidget(self.sb_IndenterRadius, 2, 1, 1, 1)

        self.l_PoissonsRatio = QLabel(w_Microindentation)
        self.l_PoissonsRatio.setObjectName(u"l_PoissonsRatio")
        sizePolicy.setHeightForWidth(self.l_PoissonsRatio.sizePolicy().hasHeightForWidth())
        self.l_PoissonsRatio.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_PoissonsRatio, 3, 0, 1, 1)

        self.sb_PoissonsRatio = QDoubleSpinBox(w_Microindentation)
        self.sb_PoissonsRatio.setObjectName(u"sb_PoissonsRatio")
        sizePolicy1.setHeightForWidth(self.sb_PoissonsRatio.sizePolicy().hasHeightForWidth())
        self.sb_PoissonsRatio.setSizePolicy(sizePolicy1)
        self.sb_PoissonsRatio.setDecimals(4)
        self.sb_PoissonsRatio.setMaximum(0.500000000000000)
        self.sb_PoissonsRatio.setSingleStep(0.001000000000000)

        self.gl_Microindentation.addWidget(self.sb_PoissonsRatio, 3, 1, 1, 1)

        self.l_DeltaRThreshold = QLabel(w_Microindentation)
        self.l_DeltaRThreshold.setObjectName(u"l_DeltaRThreshold")
        sizePolicy.setHeightForWidth(self.l_DeltaRThreshold.sizePolicy().hasHeightForWidth())
        self.l_DeltaRThreshold.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_DeltaRThreshold, 4, 0, 1, 1)

        self.sb_DeltaRThreshold = QDoubleSpinBox(w_Microindentation)
        self.sb_DeltaRThreshold.setObjectName(u"sb_DeltaRThreshold")
        sizePolicy1.setHeightForWidth(self.sb_DeltaRThreshold.sizePolicy().hasHeightForWidth())
        self.sb_DeltaRThreshold.setSizePolicy(sizePolicy1)
        self.sb_DeltaRThreshold.setMaximum(1.000000000000000)
        self.sb_DeltaRThreshold.setSingleStep(0.010000000000000)

        self.gl_Microindentation.addWidget(self.sb_DeltaRThreshold, 4, 1, 1, 1)

        self.cb_RegressionOffsets = QCheckBox(w_Microindentation)
        self.cb_RegressionOffsets.setObjectName(u"cb_RegressionOffsets")
        sizePolicy.setHeightForWidth(self.cb_RegressionOffsets.sizePolicy().hasHeightForWidth())
        self.cb_RegressionOffsets.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.cb_RegressionOffsets, 5, 0, 1, 1)

        self.cb_OffsetBounds = QCheckBox(w_Microindentation)
        self.cb_OffsetBounds.setObjectName(u"cb_OffsetBounds")
        sizePolicy.setHeightForWidth(self.cb_OffsetBounds.sizePolicy().hasHeightForWidth())
        self.cb_OffsetBounds.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.cb_OffsetBounds, 6, 0, 1, 1)

        self.l_OffsetTipDisplacement = QLabel(w_Microindentation)
        self.l_OffsetTipDisplacement.setObjectName(u"l_OffsetTipDisplacement")
        sizePolicy.setHeightForWidth(self.l_OffsetTipDisplacement.sizePolicy().hasHeightForWidth())
        self.l_OffsetTipDisplacement.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_OffsetTipDisplacement, 7, 0, 1, 1)

        self.sb_OffsetTipDisplacement = QDoubleSpinBox(w_Microindentation)
        self.sb_OffsetTipDisplacement.setObjectName(u"sb_OffsetTipDisplacement")
        self.sb_OffsetTipDisplacement.setMaximum(1000.000000000000000)

        self.gl_Microindentation.addWidget(self.sb_OffsetTipDisplacement, 7, 1, 1, 1)

        self.l_OffsetForce = QLabel(w_Microindentation)
        self.l_OffsetForce.setObjectName(u"l_OffsetForce")
        sizePolicy.setHeightForWidth(self.l_OffsetForce.sizePolicy().hasHeightForWidth())
        self.l_OffsetForce.setSizePolicy(sizePolicy)

        self.gl_Microindentation.addWidget(self.l_OffsetForce, 8, 0, 1, 1)

        self.sb_OffsetForce = QDoubleSpinBox(w_Microindentation)
        self.sb_OffsetForce.setObjectName(u"sb_OffsetForce")
        self.sb_OffsetForce.setMaximum(1000000.000000000000000)

        self.gl_Microindentation.addWidget(self.sb_OffsetForce, 8, 1, 1, 1)

        self.s_Vertical = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gl_Microindentation.addItem(self.s_Vertical, 9, 0, 1, 2)


        self.retranslateUi(w_Microindentation)

        QMetaObject.connectSlotsByName(w_Microindentation)
    # setupUi

    def retranslateUi(self, w_Microindentation):
#if QT_CONFIG(tooltip)
        self.l_Cycles.setToolTip(QCoreApplication.translate("w_Microindentation", u"Number of compression/recover cycles in the experiment", None))
#endif // QT_CONFIG(tooltip)
        self.l_Cycles.setText(QCoreApplication.translate("w_Microindentation", u"Cycles", None))
#if QT_CONFIG(tooltip)
        self.sb_Cycles.setToolTip(QCoreApplication.translate("w_Microindentation", u"Number of compression/recover cycles in the experiment", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.l_SamplesToSkip.setToolTip(QCoreApplication.translate("w_Microindentation", u"Number of samples at the beginning of the sample data to skip", None))
#endif // QT_CONFIG(tooltip)
        self.l_SamplesToSkip.setText(QCoreApplication.translate("w_Microindentation", u"Samples to skip", None))
#if QT_CONFIG(tooltip)
        self.l_IndenterRadius.setToolTip(QCoreApplication.translate("w_Microindentation", u"Radius of the spherical indenter.  This is the value R in the equation F = 4/3 * E / (1 - v\u00b2) * sqrt(R(\u03b4 - a)\u00b3) + b", None))
#endif // QT_CONFIG(tooltip)
        self.l_IndenterRadius.setText(QCoreApplication.translate("w_Microindentation", u"Indenter radius (R)", None))
#if QT_CONFIG(tooltip)
        self.sb_IndenterRadius.setToolTip(QCoreApplication.translate("w_Microindentation", u"Radius of the spherical indenter.  This is the value R in the equation F = 4/3 * E / (1 - v\u00b2) * sqrt(R(\u03b4 - a)\u00b3) + b", None))
#endif // QT_CONFIG(tooltip)
        self.sb_IndenterRadius.setSuffix(QCoreApplication.translate("w_Microindentation", u"\u00b5m", None))
#if QT_CONFIG(tooltip)
        self.l_PoissonsRatio.setToolTip(QCoreApplication.translate("w_Microindentation", u"Poisson's ratio of the sample.  This is the value of v in the equation F = 4/3 * E / (1 - v\u00b2) * sqrt(Rh\u00b3).  See Bas, Onur, et al. \"Rational design and fabrication of multiphasic soft network composites for tissue engineering articular cartilage: A numerical model-based approach.\" Chemical Engineering Journal 340 (2018): 15-23", None))
#endif // QT_CONFIG(tooltip)
        self.l_PoissonsRatio.setText(QCoreApplication.translate("w_Microindentation", u"Poisson's ratio (v)", None))
#if QT_CONFIG(tooltip)
        self.sb_PoissonsRatio.setToolTip(QCoreApplication.translate("w_Microindentation", u"Poisson's ratio of the sample.  This is the value of v in the equation F = 4/3 * E / (1 - v\u00b2) * sqrt(Rh\u00b3).  See Bas, Onur, et al. \"Rational design and fabrication of multiphasic soft network composites for tissue engineering articular cartilage: A numerical model-based approach.\" Chemical Engineering Journal 340 (2018): 15-23", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.l_DeltaRThreshold.setToolTip(QCoreApplication.translate("w_Microindentation", u"Threshold for the ratio of the indentation depth to the radius of the indenter.  If the ratio is greater than this value, then the Hertz model is not a valid approximation of the indentation response", None))
#endif // QT_CONFIG(tooltip)
        self.l_DeltaRThreshold.setText(QCoreApplication.translate("w_Microindentation", u"\u03b4/R threshold", None))
#if QT_CONFIG(tooltip)
        self.sb_DeltaRThreshold.setToolTip(QCoreApplication.translate("w_Microindentation", u"Threshold for the ratio of the indentation depth to the radius of the indenter.  If the ratio is greater than this value, then the Hertz model is not a valid approximation of the indentation response", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.cb_RegressionOffsets.setToolTip(QCoreApplication.translate("w_Microindentation", u"If unchecked, the experiment is assumed to have been perfectly prepared, calibrated, and configured, and therefore the offsets between the experiment outputs and the values can be ignored in the equation relating indentation depth to indentation force", None))
#endif // QT_CONFIG(tooltip)
        self.cb_RegressionOffsets.setText(QCoreApplication.translate("w_Microindentation", u"Regression offsets", None))
#if QT_CONFIG(tooltip)
        self.cb_OffsetBounds.setToolTip(QCoreApplication.translate("w_Microindentation", u"If unchecked, parameter offsets are unbounded and can take whatever value required to minimise the regression error", None))
#endif // QT_CONFIG(tooltip)
        self.cb_OffsetBounds.setText(QCoreApplication.translate("w_Microindentation", u"Offset bounds", None))
#if QT_CONFIG(tooltip)
        self.l_OffsetTipDisplacement.setToolTip(QCoreApplication.translate("w_Microindentation", u"Offset that relates the tip displacement and indentation depth.  It is the parameter a in the equation F = 4 / 3 * E / (1 - v\u00b2) * sqrt(R(\u03b4 - a)\u00b3) + b", None))
#endif // QT_CONFIG(tooltip)
        self.l_OffsetTipDisplacement.setText(QCoreApplication.translate("w_Microindentation", u"Tip Displacement (a)", None))
#if QT_CONFIG(tooltip)
        self.sb_OffsetTipDisplacement.setToolTip(QCoreApplication.translate("w_Microindentation", u"Offset that relates the tip displacement and indentation depth.  It is the parameter a in the equation F = 4 / 3 * E / (1 - v\u00b2) * sqrt(R(\u03b4 - a)\u00b3) + b", None))
#endif // QT_CONFIG(tooltip)
        self.sb_OffsetTipDisplacement.setSuffix(QCoreApplication.translate("w_Microindentation", u"\u00b5m", None))
#if QT_CONFIG(tooltip)
        self.l_OffsetForce.setToolTip(QCoreApplication.translate("w_Microindentation", u"Offset that relates the measured force and indentation force.  It is the parameter b in the equation F = 4 / 3 * E / (1 - v\u00b2) * sqrt(R(\u03b4 - a)\u00b3) + b", None))
#endif // QT_CONFIG(tooltip)
        self.l_OffsetForce.setText(QCoreApplication.translate("w_Microindentation", u"Force (b)", None))
#if QT_CONFIG(tooltip)
        self.sb_OffsetForce.setToolTip(QCoreApplication.translate("w_Microindentation", u"Offset that relates the measured force and indentation force.  It is the parameter b in the equation F = 4 / 3 * E / (1 - v\u00b2) * sqrt(R(\u03b4 - a)\u00b3) + b", None))
#endif // QT_CONFIG(tooltip)
        self.sb_OffsetForce.setSuffix(QCoreApplication.translate("w_Microindentation", u"\u00b5N", None))
        pass
    # retranslateUi

