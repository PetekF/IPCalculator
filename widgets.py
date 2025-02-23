import math

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
import core

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
        layout.addWidget(NetworkSizeFinderGroup(), 1, 0, topRight)

        self.setCentralWidget(centralWidget)


def QLineEditAsIpAddress():
    line = QtWidgets.QLineEdit()

    line.setReadOnly(True)
    line.setMinimumWidth(100)
    line.setMaximumWidth(120)
    line.setAlignment(Qt.AlignmentFlag.AlignRight)
    line.setPlaceholderText('0.0.0.0')

    return line

class NetworkSizeFinderGroup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        groupbox = QtWidgets.QGroupBox("Network Size")
        layout.addWidget(groupbox)

        gridLayout = QtWidgets.QGridLayout()
        groupbox.setLayout(gridLayout)

        self.cbAddressClass = QtWidgets.QComboBox()
        self.cbAddressClass.addItem('A')
        self.cbAddressClass.addItem('B')
        self.cbAddressClass.addItem('C')

        gridLayout.addWidget(QtWidgets.QLabel('Address class:'),  0, 0, Qt.AlignmentFlag.AlignRight)
        gridLayout.addWidget(self.cbAddressClass, 0, 1, Qt.AlignmentFlag.AlignLeft)

        self.txtDevicesNum = QtWidgets.QLineEdit()
        self.txtDevicesNum.setValidator(QtGui.QIntValidator())

        gridLayout.addWidget(QtWidgets.QLabel('Number of devices:'), 1, 0, Qt.AlignmentFlag.AlignRight)
        gridLayout.addWidget(self.txtDevicesNum, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.txtNetworkAddress = QLineEditAsIpAddress()
        self.txtSubnetMask = QLineEditAsShortSubnetMask()
        self.txtSubnetMask.setEnabled(False)

        gridLayout.addWidget(QtWidgets.QLabel("Network Address:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        gridLayout.addWidget(self.txtNetworkAddress, 2, 1, Qt.AlignmentFlag.AlignLeft)
        gridLayout.addWidget(self.txtSubnetMask, 2, 2, Qt.AlignmentFlag.AlignLeft)

        btn = QtWidgets.QPushButton("Calculate")
        btn.setStyleSheet("background-color: darkcyan")
        gridLayout.addWidget(btn, 3, 0, 1, 2)

        btn.clicked.connect(lambda: self.onButtonClicked())

    def onButtonClicked(self):
        self.txtNetworkAddress.clear()
        self.txtSubnetMask.clear()

        if (self.txtDevicesNum.text() == ''):
            return

        addressClass = self.cbAddressClass.currentText()
        hostsNum = int(self.txtDevicesNum.text())

        networkAddress = ""
        maxHostBits = 0
        if addressClass == 'A':
            networkAddress = "10.0.0.0"
            maxHostBits = 24
        elif addressClass == 'B':
            networkAddress = "172.16.0.0"
            maxHostBits = 16
        elif addressClass == 'C':
            networkAddress = "192.168.0.0"
            maxHostBits = 8

        maxHosts = pow(2, maxHostBits)

        if (hostsNum > maxHosts):
            return # cannot fit hosts in this address class

        hostBits = 0
        for i in range(1, maxHostBits + 1):
            if pow(2, i) - 2 >= hostsNum :
                hostBits = i
                break

        if hostBits < 2:
            return #No avaliable addreses left besides network and broadcast

        networkBits = 32 - hostBits

        self.txtNetworkAddress.setText(networkAddress)
        self.txtSubnetMask.setText(str(networkBits))



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
        self.addressRangeQuantity = QtWidgets.QLabel()

        rangeLayout = QtWidgets.QHBoxLayout()
        rangeLayout.addWidget(self.minAddress)
        rangeLayout.addWidget(QtWidgets.QLabel("-"))
        rangeLayout.addWidget(self.maxAddress)
        rangeLayout.addWidget(QtWidgets.QLabel("("))
        rangeLayout.addWidget(self.addressRangeQuantity)
        rangeLayout.addWidget(QtWidgets.QLabel(")"))

        addressRange = QtWidgets.QWidget()
        addressRange.setLayout(rangeLayout)

        boxLayout.addWidget(QtWidgets.QLabel("Useful Address Range:"), 4, 0, Qt.AlignmentFlag.AlignRight)
        boxLayout.addWidget(addressRange, 4, 1, Qt.AlignmentFlag.AlignLeft)

        btn = QtWidgets.QPushButton("Calculate")
        btn.setStyleSheet("background-color: darkcyan")
        boxLayout.addWidget(btn, 5, 0, 1, 2)

        btn.clicked.connect(lambda: self.onButtonClicked())

    def onButtonClicked(self):

        ip = self.ipAddress.getIpAddress()
        subnet = self.subnetMask.getMask()

        networkAddress = core.calculateNetworkAddress(ip, subnet)
        broadcastAddress = core.calculateBroadcastAddress(ip, subnet)
        minAddress, maxAddress = core.calculateFirstAndLastAddress(networkAddress, broadcastAddress)
        addresses = core.calculateAddressRange(minAddress, maxAddress)

        for i in range(4):
            networkAddress[i] = format(networkAddress[i], 'd')
            broadcastAddress[i] = format(broadcastAddress[i], 'd')
            minAddress[i] = format(minAddress[i], 'd')
            maxAddress[i] = format(maxAddress[i], 'd')

        self.networkAddress.setText('.'.join(networkAddress))
        self.broadcastAddress.setText('.'.join(broadcastAddress))
        self.minAddress.setText('.'.join(minAddress))
        self.maxAddress.setText('.'.join(maxAddress))

        self.addressRangeQuantity.setText(str(addresses))

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
        # self.ipWidget.addOctetChangedHandler(self.onOctetChanged)
        self.ipWidget.addOctetValueChangedHandler(self.onDecOctetValueChanged)

        self.ipBinaryWidget = IPv4(binaryMode=True)
        # self.ipBinaryWidget.addOctetChangedHandler(self.onOctetChanged)
        self.ipBinaryWidget.addOctetValueChangedHandler(self.onBinOctetValueChanged)

        convertIcon = QtWidgets.QLabel()
        convertIcon.setText('<-\n->')

        hBox.addWidget(self.ipWidget)
        hBox.addWidget(convertIcon)
        hBox.addWidget(self.ipBinaryWidget)

    def onDecOctetValueChanged(self, octetOrdinal, octetValue):
        self.ipBinaryWidget.setOctetValue(octetOrdinal, octetValue)

    def onBinOctetValueChanged(self, octetOrdinal, octetValue):
        self.ipWidget.setOctetValue(octetOrdinal, octetValue)

class IPv4Octet(QtWidgets.QLineEdit):
    @classmethod
    def decimal(cls):
        return IPv4DecimalOctet()

    @classmethod
    def binary(cls):
        return IPv4BinaryOctet()

    valueChanged = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        self.binaryMode = False
        self.defaultValue = 0 # Set this from child class

        self.textEdited.connect(lambda: self.onTextEdited())

    def onTextEdited(self):
        parsed = core.parseOctet(self.text(), self.binaryMode)
        self.valueChanged.emit(parsed)

    def getValue(self) -> int:
        parsed = core.parseOctet(self.text(), self.binaryMode)
        return parsed

    def setValue(self, value:int, notify = False):
        serialized = core.serializeOctet(value, self.binaryMode)
        self.setText(serialized)

        if notify:
            self.valueChanged.emit(value)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()

            if core.parseOctet(text, self.binaryMode) != -1:
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

        self.setMaxLength(3)
        self.setMaximumWidth(30)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setInputMask('999')
        self.setText('000')

class IPv4BinaryOctet(IPv4Octet):
    def __init__(self):
        super().__init__()
        self.binaryMode = True

        self.setMaxLength(8)
        self.setMinimumWidth(70)
        self.setMaximumWidth(70)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setInputMask('BBBBBBBB')
        self.setText('00000000')

class IPv4(QtWidgets.QWidget):
    def __init__(self, binaryMode = False):
        super().__init__()

        self.binaryMode = binaryMode
        self.octetChangedHandlers = []

        self.octets = []

        self.octets.append(IPv4Octet.binary() if binaryMode else IPv4Octet.decimal())
        self.octets.append(IPv4Octet.binary() if binaryMode else IPv4Octet.decimal())
        self.octets.append(IPv4Octet.binary() if binaryMode else IPv4Octet.decimal())
        self.octets.append(IPv4Octet.binary() if binaryMode else IPv4Octet.decimal())

        self.octets[0].valueChanged.connect(lambda val: self.onOctetValueChanged(0, val))
        self.octets[1].valueChanged.connect(lambda val: self.onOctetValueChanged(1, val))
        self.octets[2].valueChanged.connect(lambda val: self.onOctetValueChanged(2, val))
        self.octets[3].valueChanged.connect(lambda val: self.onOctetValueChanged(3, val))

        self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.addWidget(self.octets[0])
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.octets[1])
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.octets[2])
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.octets[3])

    def getIpAddress(self) -> []:
        return [
            self.octets[0].getValue(),
            self.octets[1].getValue(),
            self.octets[2].getValue(),
            self.octets[3].getValue()
        ]

    def setIpAddress(self, ipAddress:[]):
        for i in range(4):
            self.octets[i].setValue(ipAddress[i])

    def getOctetValue(self, octetOrdinal:int) -> int:
        return self.octets[octetOrdinal - 1].getValue()

    def setOctetValue(self, octetOrdinal: int, value:int):
        self.octets[octetOrdinal - 1].setValue(value)

    def onOctetValueChanged(self, octetIndex, value):
        for h in self.octetChangedHandlers:
            h(octetIndex + 1, value)

    def addOctetValueChangedHandler(self, handler):
        self.octetChangedHandlers.append(handler)

    def removeOctetValueChangedHandler(self, handler):
        self.octetChangedHandlers.remove(handler)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            parsedIp = core.parseIpAddress(text, self.binaryMode)
            if len(parsedIp) == 4:
                self.octets[0].setValue(parsedIp[0], True)
                self.octets[1].setValue(parsedIp[1], True)
                self.octets[2].setValue(parsedIp[2], True)
                self.octets[3].setValue(parsedIp[3], True)
        elif event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_C:
            oct1 = core.serializeOctet(self.octets[0].getValue(), self.binaryMode)
            oct2 = core.serializeOctet(self.octets[1].getValue(), self.binaryMode)
            oct3 = core.serializeOctet(self.octets[2].getValue(), self.binaryMode)
            oct4 = core.serializeOctet(self.octets[3].getValue(), self.binaryMode)

            ip = [oct1, oct2, oct3, oct4]
            text = '.'.join(ip)
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
        self.fullMask.addOctetValueChangedHandler(self.onOctetChanged)

        self.shortMask = QLineEditAsShortSubnetMask()
        self.shortMask.textEdited.connect(lambda: self.onShortMaskChanged(self.shortMask.text()[1:]))

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.fullMask)
        layout.addWidget(self.shortMask)

    def getMask(self) -> []:
        return self.fullMask.getIpAddress()

    def onOctetChanged(self, octetOrdinal, octetValue):
        if core.isValidSubnetMask(self.fullMask.getIpAddress()):
            networkBits = core.networkBitsInSubnetMask(self.fullMask.getIpAddress())
            self.shortMask.setText(str(networkBits))
        else:
            self.shortMask.setText(str(0))

    def onShortMaskChanged(self, mask):
        subnetMask = core.calculateSubnetMaskFromShortMask(int(mask))

        if len(subnetMask) == 0:
            self.fullMask.setIpAddress([0, 0, 0, 0])
        else:
            self.fullMask.setIpAddress(subnetMask)