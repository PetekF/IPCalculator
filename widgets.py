from unittest import case

from PySide6 import QtCore, QtWidgets, QtGui
import core

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Calculator")
        centralWidget = QtWidgets.QWidget()

        layout = QtWidgets.QGridLayout(centralWidget)
        topLeft = QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop

        addressConverter = AddressConverter()
        layout.addWidget(addressConverter, 0, 0, topLeft)

        self.setCentralWidget(centralWidget)

class AddressConversionPair(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        hBox = QtWidgets.QHBoxLayout(self)

        self.ipWidget = IPv4()
        self.ipWidget.addSegmentChangedHandler(self.onSegmentChanged)

        self.ipBinaryWidget = IPv4Binary()
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


# TODO: Add widget ConversionPair which will actually do the job of converting from IPv4 to IPv4Binary and vice versa.
class AddressConverter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        groupbox = QtWidgets.QGroupBox("Address Converter")
        layout.addWidget(groupbox)

        vBox = QtWidgets.QVBoxLayout()
        vBox.addStretch()
        groupbox.setLayout(vBox)

        conversionPair = AddressConversionPair()
        conversionPair2 = AddressConversionPair()
        conversionPair3 = AddressConversionPair()
        conversionPair4 = AddressConversionPair()

        vBox.addWidget(conversionPair)
        vBox.addWidget(conversionPair2)
        vBox.addWidget(conversionPair3)
        vBox.addWidget(conversionPair4)

class IPv4Segment(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        self.setMaxLength(3)
        self.setMaximumWidth(30)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setPlaceholderText('0')
        self.setValidator(QtGui.QIntValidator())

    def getValue(self):
        return self.text() if self.text() or self.text() != '' else '0'

    def setValue(self, value):
        self.setText(value)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            if core.isValidIPSegment(text):
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

class IPv4(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.segmentChangedHandlers = []

        self.seg1 = IPv4Segment()
        self.seg1.textEdited.connect( lambda : self.onSegmentChanged(1, self.seg1.getValue()))

        self.seg2 = IPv4Segment()
        self.seg2.textEdited.connect( lambda : self.onSegmentChanged(2, self.seg2.getValue()))

        self.seg3 = IPv4Segment()
        self.seg3.textEdited.connect(lambda: self.onSegmentChanged(3, self.seg3.getValue()))

        self.seg4 = IPv4Segment()
        self.seg4.textEdited.connect(lambda: self.onSegmentChanged(4, self.seg4.getValue()))

        dotSeparator1 = QtWidgets.QLabel(".")
        dotSeparator2 = QtWidgets.QLabel(".")
        dotSeparator3 = QtWidgets.QLabel(".")

        self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.addWidget(self.seg1)
        self.layout.addWidget(dotSeparator1)
        self.layout.addWidget(self.seg2)
        self.layout.addWidget(dotSeparator2)
        self.layout.addWidget(self.seg3)
        self.layout.addWidget(dotSeparator3)
        self.layout.addWidget(self.seg4)

    def getSegment(self, segmentNum):
        match segmentNum:
            case 1: return self.seg1
            case 2: return self.seg2
            case 3: return self.seg3
            case 4: return self.seg4

    def setSegment(self, segmentNum, segmentValue):
        match segmentNum:
            case 1: self.seg1.setText(segmentValue)
            case 2: self.seg2.setText(segmentValue)
            case 3: self.seg3.setText(segmentValue)
            case 4: self.seg4.setText(segmentValue)

    def onSegmentChanged(self, segmentNum, segmentValue):
        for h in self.segmentChangedHandlers:
            h(segmentNum, segmentValue, False)

    def addSegmentChangedHandler(self, handler):
        self.segmentChangedHandlers.append(handler)

    def removeSegmentChangedHandler(self, handler):
        self.segmentChangedHandlers.remove(handler)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            if core.isValidIPAddress(text):
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

class IPv4BinarySegment(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        self.setMaxLength(8)
        self.setMinimumWidth(70)
        self.setMaximumWidth(70)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setPlaceholderText('00000000')
        self.setValidator(QtGui.QIntValidator())

    def getValue(self):
        return self.text() if self.text() or self.text() != '' else '00000000'

    def setValue(self, value):
        self.setText(value)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            if core.isValidIPSegment(text, True):
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

# TODO: If IPv4Segment and IPv4BinarySegment inherit from abstract IPv4Segment then this class can be merged with IPv4
class IPv4Binary(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.segmentChangedHandlers = []

        self.seg1 = IPv4BinarySegment()
        self.seg1.textEdited.connect(lambda: self.onSegmentChanged(1, self.seg1.getValue()))

        self.seg2 = IPv4BinarySegment()
        self.seg2.textEdited.connect(lambda: self.onSegmentChanged(2, self.seg2.getValue()))

        self.seg3 = IPv4BinarySegment()
        self.seg3.textEdited.connect(lambda: self.onSegmentChanged(3, self.seg3.getValue()))

        self.seg4 = IPv4BinarySegment()
        self.seg4.textEdited.connect(lambda: self.onSegmentChanged(4, self.seg4.getValue()))

        dotSeparator1 = QtWidgets.QLabel(".")
        dotSeparator2 = QtWidgets.QLabel(".")
        dotSeparator3 = QtWidgets.QLabel(".")

        self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.addWidget(self.seg1)
        self.layout.addWidget(dotSeparator1)
        self.layout.addWidget(self.seg2)
        self.layout.addWidget(dotSeparator2)
        self.layout.addWidget(self.seg3)
        self.layout.addWidget(dotSeparator3)
        self.layout.addWidget(self.seg4)

    def getSegment(self, segmentNum):
        match segmentNum:
            case 1: return self.seg1
            case 2: return self.seg2
            case 3: return self.seg3
            case 4: return self.seg4

    def setSegment(self, segmentNum, segmentValue):
        match segmentNum:
            case 1: self.seg1.setText(segmentValue)
            case 2: self.seg2.setText(segmentValue)
            case 3: self.seg3.setText(segmentValue)
            case 4: self.seg4.setText(segmentValue)

    def onSegmentChanged(self, segmentNum, segmentValue):
        for h in self.segmentChangedHandlers:
            h(segmentNum, segmentValue, True)

    def addSegmentChangedHandler(self, handler):
        self.segmentChangedHandlers.append(handler)

    def removeSegmentChangedHandler(self, handler):
        self.segmentChangedHandlers.remove(handler)

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_V:
            text = QtGui.QGuiApplication.clipboard().text()
            if core.isValidIPAddress(text, True):
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