from PySide6 import QtCore, QtWidgets, QtGui
import core

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Calculator")
        centralWidget = QtWidgets.QWidget()

        layout = QtWidgets.QGridLayout(centralWidget)
        topLeft = QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop

        addressConverter = AddressConverterGroup()
        layout.addWidget(addressConverter, 0, 0, topLeft)

        self.setCentralWidget(centralWidget)

class AddressConverter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        hBox = QtWidgets.QHBoxLayout(self)

        self.ipWidget = IPv4()
        self.ipWidget.addSegmentChangedHandler(self.onSegmentChanged)

        self.ipBinaryWidget = IPv4(binaryMode=True)
        self.ipBinaryWidget.addSegmentChangedHandler(self.onSegmentChanged)

        convertIcon = QtWidgets.QLabel()
        convertIcon.setText('<-\n->')

        hBox.addWidget(self.ipWidget)
        hBox.addWidget(convertIcon)
        hBox.addWidget(self.ipBinaryWidget)

    def onSegmentChanged(self, segmentNum, segmentValue, isBinary = False):
        if isBinary:
            otherSeg = core.convertBinarySegmentToSegment(segmentValue)
            self.ipWidget.setSegment(segmentNum, otherSeg)
        else:
            otherSeg = core.convertSegmentToBinarySegment(segmentValue)
            self.ipBinaryWidget.setSegment(segmentNum, otherSeg)

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

class IPv4Segment(QtWidgets.QLineEdit):
    @classmethod
    def decimal(cls):
        return IPv4DecimalSegment()

    @classmethod
    def binary(cls):
        return IPv4BinarySegment()

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
            if core.isValidIPSegment(text, self.binaryMode):
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

class IPv4DecimalSegment(IPv4Segment):
    def __init__(self):
        super().__init__()
        self.defaultValue = '0'

        self.setMaxLength(3)
        self.setMaximumWidth(30)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setPlaceholderText('0')
        self.setValidator(QtGui.QIntValidator())

class IPv4BinarySegment(IPv4Segment):
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
        self.segmentChangedHandlers = []

        self.seg1 = IPv4Segment.binary() if binaryMode else IPv4Segment.decimal()
        self.seg2 = IPv4Segment.binary() if binaryMode else IPv4Segment.decimal()
        self.seg3 = IPv4Segment.binary() if binaryMode else IPv4Segment.decimal()
        self.seg4 = IPv4Segment.binary() if binaryMode else IPv4Segment.decimal()

        self.seg1.textEdited.connect(lambda: self.onSegmentChanged(1, self.seg1.getValue()))
        self.seg2.textEdited.connect(lambda: self.onSegmentChanged(2, self.seg2.getValue()))
        self.seg3.textEdited.connect(lambda: self.onSegmentChanged(3, self.seg3.getValue()))
        self.seg4.textEdited.connect(lambda: self.onSegmentChanged(4, self.seg4.getValue()))

        self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.addWidget(self.seg1)
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.seg2)
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.seg3)
        self.layout.addWidget(QtWidgets.QLabel("."))
        self.layout.addWidget(self.seg4)

    def getSegment(self, segmentNum):
        match segmentNum:
            case 1: return self.seg1.getValue()
            case 2: return self.seg2.getValue()
            case 3: return self.seg3.getValue()
            case 4: return self.seg4.getValue()

    def setSegment(self, segmentNum, segmentValue):
        match segmentNum:
            case 1: self.seg1.setText(segmentValue)
            case 2: self.seg2.setText(segmentValue)
            case 3: self.seg3.setText(segmentValue)
            case 4: self.seg4.setText(segmentValue)

    def onSegmentChanged(self, segmentNum, segmentValue):
        for h in self.segmentChangedHandlers:
            h(segmentNum, segmentValue, self.binaryMode)

    def addSegmentChangedHandler(self, handler):
        self.segmentChangedHandlers.append(handler)

    def removeSegmentChangedHandler(self, handler):
        self.segmentChangedHandlers.remove(handler)

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