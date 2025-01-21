from pathlib import Path
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QColorDialog
from PySide6.QtCore import Qt
import vtk

class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()

        self.setWindowTitle("3D Modell in QT mit VTK")

        # zentrales Widget setzen und Renderer initialisieren
        self.setCentralWidget(widget)
        self.centralWidget().GetRenderWindow().Render()

        # Modell kommt mit dem Widget mit
        self.myModel = widget.getModel()

        # Menü und Aktionen erstellen
        self.create_menus()

        # Statusleiste initialisieren
        self.statusBar().showMessage("Laden Sie ein JSON oder FDD File ein, um es anzuzeigen")

        # Initialisierungen
        self.current_interactor_style = "default" # Standardmäßig Default Interactor Style 
        self.is_text_visible = False # Standardmäßig kein Interactor Text

        # Strukturbaum-Dock-Widget hinzufügen
        self.structure_tree_dock = widget.create_structure_tree_dock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.structure_tree_dock)


    def create_menus(self):
        # Erstellen der Menüs und Aktionen
        menu_bar = self.menuBar()

        # Datei-Menü
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.create_action("Load from JSON", self.load_model, QKeySequence(Qt.CTRL | Qt.Key_L)))
        file_menu.addAction(self.create_action("Open FDD", self.import_fdd, QKeySequence(Qt.CTRL | Qt.Key_O)))
        file_menu.addSeparator()
        file_menu.addAction(self.create_action("Save to JSON", self.save_model,QKeySequence.Save))
        file_menu.addSeparator()
        file_menu.addAction(self.create_action("Quit", self.close, QKeySequence(Qt.CTRL | Qt.Key_Q)))
        # View-Menü
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.create_action("Fullscreen", self.toggle_fullscreen, QKeySequence("F11")))
        view_menu.addSeparator()
        view_menu.addAction(self.create_action("Front View", self.set_front_view))
        view_menu.addAction(self.create_action("Back View", self.set_back_view))
        view_menu.addAction(self.create_action("Left View", self.set_left_view))
        view_menu.addAction(self.create_action("Right View", self.set_right_view))
        view_menu.addAction(self.create_action("Top View", self.set_top_view))
        view_menu.addAction(self.create_action("Bottom View", self.set_bottom_view))
        # Steuerung-Menü
        control_menu = menu_bar.addMenu("Control")
        control_menu.addAction(self.create_action("Switch Interactor Style", self.toggle_interactor_style))
        control_menu.addAction(self.create_action("Show/Hide Interaction Information Text", self.toggle_control_text))
        # Design-Menü
        design_menu = menu_bar.addMenu("Design")
        design_menu.addAction(self.create_action("Background Color", self.change_background_color))
        design_menu.addAction(self.create_action("Text Color", self.change_text_color))

        # About-Menü
        about_menu = menu_bar.addMenu("About")
        about_menu.addAction(self.create_action("Information", self.show_about_info))


    def create_action(self, name, method, shortcut=None):
            # Hilfsfunktion zur Erstellung von Aktionen
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(method)
            return action


    def load_model(self):
        # JSON Datei Laden
        filename, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if filename:
            if filename.lower().endswith(".json"):
                self.myModel.loadDatabase(Path(filename)) # Routine aus mbsModel verwenden
                self.statusBar().showMessage(f"Modell aus JSON geladen: {filename}")
                self.centralWidget().update_renderer(self.myModel)
                # Aktualisiere den Strukturbaum mit dem tatsächlichen Dateinamen
                self.centralWidget().update_structure_tree(file_name=Path(filename).name)
            else:
                self.show_message("Ungültiges Dateiformat", "Bitte wählen Sie eine JSON-Datei aus.")
        else:
            self.statusBar().showMessage("Modell-Laden abgebrochen")


    def save_model(self):
        # aktuell geöffnetes Modell als JSON speichern
        filename, _ = QFileDialog.getSaveFileName(self, "Save Model File", "", "JSON Files (*.json)")
        if filename:
            self.myModel.saveDatabase(Path(filename)) # Routine aus mbsModel verwenden
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")


    def import_fdd(self):
        # FDD File einlesen
        filename, _ = QFileDialog.getOpenFileName(self, "Import FDD File", "", "FDD Files (*.fdd)")
        if filename.lower().endswith(".fdd"):
            self.myModel.importFddFile(filename) # Routine aus mbsModel verwenden
            self.statusBar().showMessage(f"FDD-Datei importiert: {filename}")
            self.centralWidget().update_renderer(self.myModel)
            # Aktualisiere den Strukturbaum mit dem tatsächlichen Dateinamen
            self.centralWidget().update_structure_tree(file_name=Path(filename).name)
        else:
            self.show_message("Ungültiges Dateiformat", "Bitte wählen Sie eine FDD-Datei aus.")


    def show_about_info(self):
        # Infotext
        QMessageBox.information(
            self,
            "About",
            "VIS3VO/VIS3UE Projekt\nFreedyn GUI\nFabian Pointinger\nS2310566016\nfabian.pointinger@students.fh-wels.at\n"
        )


    def toggle_control_text(self):
        # Umschalten des Steuerungstextes, je nachdem welcher Interactor ausgewählt ist
        if self.is_text_visible:
            # wenn Text ersichtlich, dann ausblenden
            self.centralWidget().update_text_actor("")  # Text ausblenden
            self.is_text_visible = False # Status setzen
            self.statusBar().showMessage("Steuerungstext ausgeblendet")
        else:
            # Text basierend auf dem aktuellen Interactor Style anzeigen
            self.centralWidget().update_text_actor(self.current_interactor_style)
            self.is_text_visible = True # Status setzen
            self.statusBar().showMessage("Steuerungstext angezeigt")


    def toggle_fullscreen(self):
        # zwischen Vollbild und Standard umschalten
        if self.isFullScreen():
            self.showNormal()
            self.setGeometry(100, 100, 800, 600) # Standardgröße hier ändern
        else:
            self.showFullScreen()


    def toggle_interactor_style(self):
        # zwischen Standard- und Trackball Interactor umschalten
        render_window = self.centralWidget().GetRenderWindow()
        interactor = render_window.GetInteractor()

        if self.current_interactor_style == "default":
            # wenn aktuell default ist, dann auf trackball umschalten
            trackball_style = vtk.vtkInteractorStyleTrackballCamera()
            interactor.SetInteractorStyle(trackball_style)
            self.current_interactor_style = "trackball"
            if self.is_text_visible:
                self.centralWidget().update_text_actor(self.current_interactor_style)
            self.statusBar().showMessage("Trackball Interactor aktiviert")
        else:
            # wenn aktuell trackball ist, dann auf default umschalten
            default_style = vtk.vtkInteractorStyleSwitch()
            interactor.SetInteractorStyle(default_style)
            self.current_interactor_style = "default"
            if self.is_text_visible:
                self.centralWidget().update_text_actor(self.current_interactor_style)
            self.statusBar().showMessage("Standard Interactor aktiviert")


    def change_background_color(self):
        # Hintergrundfarbe des Renderers ändern
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = color.getRgbF()
            self.centralWidget().GetRenderer().SetBackground(r, g, b)
            self.centralWidget().GetRenderWindow().Render()


    def change_text_color(self):
        # Textfarbe ändern
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = color.getRgbF()
            self.centralWidget().text_actor.GetTextProperty().SetColor(r, g, b)
            self.centralWidget().GetRenderWindow().Render()


    # verschiedene Ansichten
    def set_front_view(self):
        # Blickrichtung entlang der negativen Y-Achse
        self.set_camera_orientation(0, -1, 0, 0, 0, 1)
        self.statusBar().showMessage("Front-Ansicht")

    def set_back_view(self):
        # Blickrichtung entlang der positiven Y-Achse
        self.set_camera_orientation(0, 1, 0, 0, 0, 1)
        self.statusBar().showMessage("Back-Ansicht")

    def set_left_view(self):
        # Blickrichtung entlang der negativen X-Achse
        self.set_camera_orientation(-1, 0, 0, 0, 0, 1)
        self.statusBar().showMessage("Left-Ansicht")

    def set_right_view(self):
        # Blickrichtung entlang der positiven X-Achse
        self.set_camera_orientation(1, 0, 0, 0, 0, 1)
        self.statusBar().showMessage("Right-Ansicht")

    def set_top_view(self):
        # Blickrichtung entlang der negativen Z-Achse
        self.set_camera_orientation(0, 0, -1, 0, 1, 0)
        self.statusBar().showMessage("Top-Ansicht")

    def set_bottom_view(self):
        # Blickrichtung entlang der positiven Z-Achse
        self.set_camera_orientation(0, 0, 1, 0, -1, 0)
        self.statusBar().showMessage("Bottom-Ansicht")

    def set_camera_orientation(self, pos_x, pos_y, pos_z, up_x, up_y, up_z):
        # Kameraansicht Hilfsfunktion
        renderer = self.centralWidget().GetRenderer()
        camera = renderer.GetActiveCamera()
        camera.SetPosition(pos_x, pos_y, pos_z)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(up_x, up_y, up_z)
        renderer.ResetCamera()
        self.centralWidget().GetRenderWindow().Render()


    def show_message(self, title, text):
        # Fehlermeldung Ausgabe
        QMessageBox.critical(self, title, text)
