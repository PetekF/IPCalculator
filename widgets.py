from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLineEdit
from shiboken6 import isValid

import core
from core import networkBitsToOctetValue


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Calculator")
        centralWidget = QtWidgets.QWidget()

        layout = QtWidgets.QGridLayout(centralWidget)
        topLeft = Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop
        bottomLeft= Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom
        topRight = Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop
        bottomRight = Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignBottom

        layout.addWidget(AddressConverterGroup(), 0, 0, topRight)
        layout.addWidget(NetworkInfoGroup(), 0, 1, topLeft)

        self.setCentralWidget(centralWidget)

def QLineEditAsIpAddress():
    line = QtWidgets.QLineEdit()

    line.setReadOnly(True)
    line.setMinimumWidth(100)
    line.setMaximumWidth(120)
    line.setAlignment(Qt.AlignmentFlag.AlignRight)
    line.setPlaceholderText('0.0.0.0')

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

        self.ipAddress = IPv4()

        boxLayout.addWidget(QtWidgets.QLabel("IP Address:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(self.ipAddress, 0, 1, Qt.AlignmentFlag.AlignLeft)

        self.subnetMask = SubnetMask()

        boxLayout.addWidget(QtWidgets.QLabel("Subnet Mask:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(self.subnetMask, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.networkAddress = QLineEditAsIpAddress()
        boxLayout.addWidget(QtWidgets.QLabel("Network Address:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(self.networkAddress, 2, 1, Qt.AlignmentFlag.AlignLeft)

        self.broadcastAddress = QLineEditAsIpAddress()
        boxLayout.addWidget(QtWidgets.QLabel("Broadcast Address:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(self.broadcastAddress, 3, 1, Qt.AlignmentFlag.AlignLeft)


        self.minAddress = QLineEditAsIpAddress()
        self.maxAddress = QLineEditAsIpAddress()

        rangeLayout = QtWidgets.QHBoxLayout()
        rangeLayout.addWidget(self.minAddress)
        rangeLayout.addWidget(QtWidgets.QLabel("-"))
        rangeLayout.addWidget(self.maxAddress)

        addressRange = QtWidgets.QWidget()
        addressRange.setLayout(rangeLayout)

        boxLayout.addWidget(QtWidgets.QLabel("Useful Address Range:"), 4, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(addressRange, 4, 1, Qt.AlignmentFlag.AlignLeft)

        btn = QtWidgets.QPushButton("Calculate")
        btn.setStyleSheet("background-color: darkcyan")
        boxLayout.addWidget(btn, 5, 0, 1, 2)

        btn.clicked.connect(lambda: self.onButtonClicked())

    def onButtonClicked(self):
        # TODO: Add some validation
        ip = [int(self.ipAddress.getOctet(1)), int(self.ipAddress.getOctet(2)), int(self.ipAddress.getOctet(3)), int(self.ipAddress.getOctet(4))]
        subnet = [int(self.subnetMask.fullMask.getOctet(1)), int(self.subnetMask.fullMask.getOctet(2)), int(self.subnetMask.fullMask.getOctet(3)), int(self.subnetMask.fullMask.getOctet(4))]

        networkAddress = core._calculateNetworkAddress(ip, subnet)
        broadcastAddress = core._calculateBroadcastAddress(ip, subnet)
        minAddress, maxAddress = core._firstAndLastUsefulAddress(ip, subnet)

        for i in range(4):
            networkAddress[i] = format(networkAddress[i], 'd')
            broadcastAddress[i] = format(broadcastAddress[i], 'd')
            minAddress[i] = format(minAddress[i], 'd')
            maxAddress[i] = format(maxAddress[i], 'd')

        self.networkAddress.setText('.'.join(networkAddress))
        self.broadcastAddress.setText('.'.join(broadcastAddress))
        self.minAddress.setText('.'.join(minAddress))
        self.maxAddress.setText('.'.join(maxAddress))

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
        self.setInputMask('999')
        self.setText('000')
        # self.setValidator(QtGui.QIntValidator(0, 255, self))

class IPv4BinaryOctet(IPv4Octet):
    def __init__(self):
        super().__init__()
        self.binaryMode = True
        # self.defaultValue = '00000000'

        self.setMaxLength(8)
        self.setMinimumWidth(70)
        self.setMaximumWidth(70)
        self.setAlignment(QtCore.Qt.AlignRight)
        # self.setPlaceholderText('00000000')
        self.setInputMask('BBBBBBBB')
        self.setText('00000000')
        # self.setValidator(QtGui.QIntValidator())

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

def QLineEditAsShortSubnetMask():
    line = QtWidgets.QLineEdit()

    line.setMinimumWidth(20)
    line.setMaximumWidth(30)

    line.setInputMask('/#9')
    line.setText('0')

    return line

class SubnetMask(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.fullMask = IPv4()
        self.fullMask.addOctetChangedHandler(self.onOctetChanged)

        self.shortMask = QLineEditAsShortSubnetMask()
        self.shortMask.textEdited.connect(lambda: self.onShortMaskChanged(self.shortMask.text()[1:]))

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.fullMask)
        layout.addWidget(self.shortMask)

    #TODO: Move calculations from this mehod to 'core'
    def onOctetChanged(self, octetPosition, octet, isBinary = False):
        isValid = True
        networkBits = 0

        prevOctetValue = 255 #Fake initial value to make the loop work
        for i in range(1, 5):
            currentOctet = self.fullMask.getOctet(i)
            currentOctetValue = int(currentOctet, 10)
            currentOctetNetworkBits = core.networkBitsInOctetValue(currentOctetValue)

            if currentOctetNetworkBits == -1 or currentOctetNetworkBits > 0 and prevOctetValue != 255:
                isValid = False
                break

            networkBits += currentOctetNetworkBits
            prevOctetValue = currentOctetValue

        if isValid:
            self.shortMask.setText(str(networkBits))
        else:
            self.shortMask.setText(str(-1))

    #TODO: Move calculations from this mehod to 'core'
    def onShortMaskChanged(self, mask):
        try:
            maskValue = int(mask, 10)
        except ValueError:
            maskValue = 0

        if maskValue >= 0 and maskValue <= 32:
            fullOctets = int(maskValue / 8)
            lastOcetBits = maskValue % 8

            for i in range(fullOctets):
                self.fullMask.setOctet(i + 1, '255')

            self.fullMask.setOctet(fullOctets + 1, str(core.networkBitsToOctetValue(lastOcetBits)))

            emptyOctets = 4 - fullOctets + 1
            for i in range(emptyOctets):
                self.fullMask.setOctet(fullOctets + 1 + i + 1, '0')
        else:
            for i in range(4):
                self.fullMask.setOctet(i + 1, '0')