import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from main_widget import Widget

# QT-Anwendung starten
app = QApplication(sys.argv)

# Widget anlegen und dem Window übergeben
widget = Widget()
window = MainWindow(widget)
window.show()

# Anwendung beenden, wenn Fenster geschlossen wird
sys.exit(app.exec())