import sys
from PySide6 import QtWidgets
import widgets

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    window = widgets.MainWindow()
    window.show()

    sys.exit(app.exec())