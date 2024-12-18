from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

import core

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Calculator")
        centralWidget = QtWidgets.QWidget()

        layout = QtWidgets.QGridLayout(centralWidget)
        topLeft = Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop

        layout.addWidget(AddressConverterGroup(), 0, 0, topLeft)
        layout.addWidget(NetworkInfoGroup(), 1, 0, topLeft)

        self.setCentralWidget(centralWidget)

def QLineEditAsIpAddress():
    line = QtWidgets.QLineEdit()

    line.setReadOnly(True)
    line.setMinimumWidth(100)
    line.setMaximumWidth(120)
    line.setAlignment(Qt.AlignmentFlag.AlignRight)
    line.setPlaceholderText('0.0.0.0')

    return line

def QLineEditAsShortSubnetMask():
    line = QtWidgets.QLineEdit()

    line.setReadOnly(True)
    line.setMinimumWidth(20)
    line.setMaximumWidth(30)
    line.setPlaceholderText('/0')

    return line

class NetworkInfoGroup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        groupbox = QtWidgets.QGroupBox("Network Information")
        layout.addWidget(groupbox)

        boxLayout = QtWidgets.QGridLayout()
        groupbox.setLayout(boxLayout)

        boxLayout.addWidget(QtWidgets.QLabel("IP Address:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(IPv4(), 0, 1, Qt.AlignmentFlag.AlignLeft)

        subnetPairLayout = QtWidgets.QHBoxLayout()
        subnetPairLayout.addWidget(IPv4())
        subnetPairLayout.addSpacing(15)
        subnetPairLayout.addWidget(QLineEditAsShortSubnetMask())

        subnetPair = QtWidgets.QWidget()
        subnetPair.setLayout(subnetPairLayout)

        boxLayout.addWidget(QtWidgets.QLabel("Subnet Mask:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(subnetPair, 1, 1, Qt.AlignmentFlag.AlignLeft)

        boxLayout.addWidget(QtWidgets.QLabel("Network Address:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(QLineEditAsIpAddress(), 2, 1, Qt.AlignmentFlag.AlignLeft)

        boxLayout.addWidget(QtWidgets.QLabel("Broadcast Address:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(QLineEditAsIpAddress(), 3, 1, Qt.AlignmentFlag.AlignLeft)


        rangeLayout = QtWidgets.QHBoxLayout()
        rangeLayout.addWidget(QLineEditAsIpAddress())
        rangeLayout.addWidget(QtWidgets.QLabel("-"))
        rangeLayout.addWidget(QLineEditAsIpAddress())

        addressRange = QtWidgets.QWidget()
        addressRange.setLayout(rangeLayout)

        boxLayout.addWidget(QtWidgets.QLabel("Useful Address Range:"), 4, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(addressRange, 4, 1, Qt.AlignmentFlag.AlignLeft)

        btn = QtWidgets.QPushButton("Calculate")
        btn.setStyleSheet("background-color: darkcyan")
        boxLayout.addWidget(btn, 5, 0, 1, 2)


class AddressConverterGroup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        groupbox = QtWidgets.QGroupBox("Address Converter")
        layout.addWidget(groupbox)

        vBox = QtWidgets.QVBoxLayout()
        vBox.addStretch()
        groupbox.setLayout(vBox)

        vBox.addWidget(AddressConverter())
        vBox.addWidget(AddressConverter())
        vBox.addWidget(AddressConverter())
        vBox.addWidget(AddressConverter())

class AddressConverter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        hBox = QtWidgets.QHBoxLayout(self)

        self.ipWidget = IPv4()
        self.ipWidget.addOctetChangedHandler(self.onOctetChanged)

        self.ipBinaryWidget = IPv4(binaryMode=True)
        self.ipBinaryWidget.addOctetChangedHandler(self.onOctetChanged)

        convertIcon = QtWidgets.QLabel()
        convertIcon.setText('<-\n->')

        hBox.addWidget(self.ipWidget)
        hBox.addWidget(convertIcon)
        hBox.addWidget(self.ipBinaryWidget)

    def onOctetChanged(self, octetNum, octetValue, isBinary = False):
        if isBinary:
            otherSeg = core.binaryOctetToOctet(octetValue)
            self.ipWidget.setOctet(octetNum, otherSeg)
        else:
            otherSeg = core.octetToBinaryOctet(octetValue)
            self.ipBinaryWidget.setOctet(octetNum, otherSeg)

class IPv4Octet(QtWidgets.QLineEdit):
    @classmethod
    def decimal(cls):
        return IPv4DecimalOctet()

    @classmethod
    def binary(cls):
        return IPv4BinaryOctet()

    def __init__(self):
        super().__init__()
        self.binaryMode = False
        self.defaultValue = '' # Set this from child class

    def getValue(self):
        return self.text() if self.text() or self.text() != '' else self.defaultValue

    def setValue(self, value):
        self.setText(value)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            if core.isValidIPOctet(text, self.binaryMode):
                self.setText(text)
                self.textEdited.emit(self.getValue())
            else:
                self.parent().keyPressEvent(event)
        elif event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_C:
            if not self.hasSelectedText():
                self.parent().keyPressEvent(event)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

class IPv4DecimalOctet(IPv4Octet):
    def __init__(self):
        super().__init__()
        self.defaultValue = '0'

        self.setMaxLength(3)
        self.setMaximumWidth(30)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setPlaceholderText('0')
        self.setValidator(QtGui.QIntValidator())

class IPv4BinaryOctet(IPv4Octet):
    def __init__(self):
        super().__init__()
        self.binaryMode = True
        self.defaultValue = '00000000'

        self.setMaxLength(8)
        self.setMinimumWidth(70)
        self.setMaximumWidth(70)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setPlaceholderText('00000000')
        self.setValidator(QtGui.QIntValidator())

class IPv4(QtWidgets.QWidget):
    def __init__(self, binaryMode = False):
        super().__init__()

        self.binaryMode = binaryMode
        self.octetChangedHandlers = []

        self.seg1 = IPv4Octet.binary() if binaryMode else IPv4Octet.decimal()
        self.seg2 = IPv4Octet.binary() if binaryMode else IPv4Octet.decimal()
        self.seg3 = IPv4Octet.binary() if binaryMode else IPv4Octet.decimal()
        self.seg4 = IPv4Octet.binary() if binaryMode else IPv4Octet.decimal()

        self.seg1.textEdited.connect(lambda: self.onOctetChanged(1, self.seg1.getValue()))
        self.seg2.textEdited.connect(lambda: self.onOctetChanged(2, self.seg2.getValue()))
        self.seg3.textEdited.connect(lambda: self.onOctetChanged(3, self.seg3.getValue()))
        self.seg4.textEdited.connect(lambda: self.onOctetChanged(4, self.seg4.getValue()))

        self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.addWidget(self.seg1)
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.seg2)
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.seg3)
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.seg4)

    def getOctet(self, octetNum):
        match octetNum:
            case 1: return self.seg1.getValue()
            case 2: return self.seg2.getValue()
            case 3: return self.seg3.getValue()
            case 4: return self.seg4.getValue()

    def setOctet(self, octetNum, octetValue):
        match octetNum:
            case 1: self.seg1.setText(octetValue)
            case 2: self.seg2.setText(octetValue)
            case 3: self.seg3.setText(octetValue)
            case 4: self.seg4.setText(octetValue)

    def onOctetChanged(self, octetNum, octetValue):
        for h in self.octetChangedHandlers:
            h(octetNum, octetValue, self.binaryMode)

    def addOctetChangedHandler(self, handler):
        self.octetChangedHandlers.append(handler)

    def removeOctetChangedHandler(self, handler):
        self.octetChangedHandlers.remove(handler)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            if core.isValidIPAddress(text, self.binaryMode):
                tokens = text.split('.')
                self.seg1.setText(tokens[0])
                self.seg1.textEdited.emit(self.seg1.getValue())

                self.seg2.setText(tokens[1])
                self.seg2.textEdited.emit(self.seg2.getValue())

                self.seg3.setText(tokens[2])
                self.seg3.textEdited.emit(self.seg3.getValue())

                self.seg4.setText(tokens[3])
                self.seg4.textEdited.emit(self.seg4.getValue())
        elif event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_C:
            text = self.seg1.getValue() + '.' + self.seg2.getValue() + '.' + self.seg3.getValue() + '.' + self.seg4.getValue()
            QtGui.QGuiApplication.clipboard().setText(text)
        else:
            super().keyPressEvent(event)

class SubnetMask(QtWidgets.QWidget):
    validOctetValues = [255, 254, 252, 248, 240, 224, 192, 128, 0]

    # Maybe allow hiding and showing of full mask instead of having to recreate the widget
    def __init__(self, binaryMode = False):
        super().__init__()

        self.fullMask = IPv4Octet.binary() if binaryMode else IPv4Octet.decimal()
        self.shortMask = QtWidgets.QLineEdit()

        self.fullMask.addOctetChangedHandler(self.onMaskOctetChanged)

    def onMaskOctetChanged(self, octetNum, octetValue, isBinary = False):
        isValid = False
        octetNum = int(octetNum, 10)

        if octetNum in SubnetMask.validOctetValues:
            isValid = True

        previousOctets = octetNum - 1

        invalidPreviousOctets = []

        for i in range(previousOctets):
            prevOctet = self.fullMask.getOctet(i + 1)
            prevOctetNum = int(prevOctet, 10)

            if prevOctetNum != 255:
                isValid = False
                invalidPreviousOctets.append(i + 1)
        #
        # if isValid:
        #     # change short mask value
        #     x = previousOctets * 8 + octetNum
        # else:
        #     # short mask = /-1

    def invalidOctetDetected(self, octetNum):
        a = 1
        # color octet border in different color