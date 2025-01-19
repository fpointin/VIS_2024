from pathlib import Path
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QDockWidget, QListView, QVBoxLayout, QWidget, QTreeView, QColorDialog
from PySide6.QtCore import Qt
import mbsModel
import main_widget as mwid
import vtk

class MainWindow(QMainWindow):
    DEFAULT_TEXT = (
        "DEFAULT Steuerung:\n"
        "- Linke Maustaste: Rotieren\n"
        "- Rechte Maustaste: Zoom\n"
        "- Shift + Linke Maustaste: Verschieben"
    )

    TRACKBALL_TEXT = (
        "TRACKBALL Steuerung:\n"
        "- Linke Maustaste: Rotieren\n"
        "- Rechte Maustaste: Zoom\n"
        "- Shift + Linke Maustaste: Verschieben"
    )

    WINDOW_GEOMETRY = (100, 100, 800, 600)  # x, y, Breite, Höhe

    def __init__(self, widget):
        super().__init__()

        self.setWindowTitle("3D Modell in QT mit VTK")
        self.setCentralWidget(widget)

        # Initialisiere MBS Modell
        self.myModel = mbsModel.mbsModel()

        # Menü und Aktionen erstellen
        self._create_menus()

        # Statusleiste initialisieren
        self.statusBar().showMessage("Laden Sie ein JSON oder FDD File ein, um es anzuzeigen")

        # Initialisierung vom Interactor
        self.current_interactor_style = "default"
        # Text-Actor initialisieren (kein Text standardmäßig)
        self.is_text_visible = False
        self.centralWidget().update_text_actor("")  # Kein Text beim Start

        # Strukturbaum-Dock-Widget hinzufügen
        self.structure_tree_dock = self._create_structure_tree_dock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.structure_tree_dock)

    def _create_structure_tree_dock(self):
        """Erstellt das Dock-Widget für den Strukturbaum."""
        dock_widget = QDockWidget("Strukturbaum", self)
        dock_widget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # Erstelle ein Widget für den Strukturbaum
        tree_widget = QWidget()
        layout = QVBoxLayout(tree_widget)

        # Erstelle den Baum-Modell
        self.tree_model = QStandardItemModel()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        layout.addWidget(self.tree_view)

        # Baum mit Objekten aus dem Modell füllen
        self.update_structure_tree()

        # Setze das Widget im Dock-Widget
        dock_widget.setWidget(tree_widget)

        return dock_widget
    
    def update_structure_tree(self, file_name="File Name"):
        """Aktualisiert den Strukturbaum mit den geladenen MBS-Objekten."""
        # Clear the model completely
        self.tree_model.clear()

        # Explicitly set the root item
        root_item = QStandardItem(file_name)
        root_item.setEditable(False)  # Prevent editing of the root item
        self.tree_model.appendRow(root_item)

        # Add child categories to the root item
        rigid_bodies_item = QStandardItem("Rigid Bodies")
        rigid_bodies_item.setEditable(False)

        constraints_item = QStandardItem("Constraints")
        constraints_item.setEditable(False)

        forces_item = QStandardItem("Forces")
        forces_item.setEditable(False)

        measures_item = QStandardItem("Measures")
        measures_item.setEditable(False)

        # Populate the categories with model objects
        for obj in self.myModel.get_mbsObjectList():
            obj_type, name = self.myModel.get_object_type_and_name(obj)
            item = QStandardItem(name)

            if obj_type == "Body":
                rigid_bodies_item.appendRow(item)
                rigid_bodies_item.setEditable(False)
            elif obj_type == "Constraint":
                constraints_item.appendRow(item)
                constraints_item.setEditable(False)
            elif obj_type == "Force":
                forces_item.appendRow(item)
                forces_item.setEditable(False)
            elif obj_type == "Measure":
                measures_item.appendRow(item)
                measures_item.setEditable(False)

        # Append categories to the root item
        root_item.appendRow(rigid_bodies_item)
        root_item.appendRow(constraints_item)
        root_item.appendRow(forces_item)
        root_item.appendRow(measures_item)

        # Set the model's root item (no "1" anymore)
        self.tree_view.expandAll()



    def _create_menus(self):
        """Erstellt die Menüs und fügt Aktionen hinzu."""
        menu_bar = self.menuBar()

        # Datei-Menü
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._create_action("Load from JSON", self.load_model))
        file_menu.addAction(self._create_action("Open FDD", self.import_fdd))
        file_menu.addSeparator()
        file_menu.addAction(self._create_action("Save to JSON", self.save_model))
        file_menu.addSeparator()
        file_menu.addAction(self._create_action("EXIT", self.close, QKeySequence.Quit))

        # View-Menü
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self._create_action("Fullscreen", self.toggle_fullscreen, QKeySequence("F11")))
        view_menu.addAction(self._create_action("Reset View", self.reset_view))
        view_menu.addSeparator()
        view_menu.addAction(self._create_action("Front View", self.set_front_view))
        view_menu.addAction(self._create_action("Back View", self.set_back_view))
        view_menu.addAction(self._create_action("Left View", self.set_left_view))
        view_menu.addAction(self._create_action("Right View", self.set_right_view))
        view_menu.addAction(self._create_action("Top View", self.set_top_view))
        view_menu.addAction(self._create_action("Bottom View", self.set_bottom_view))

        # Steuerung-Menü
        control_menu = menu_bar.addMenu("Control")
        control_menu.addAction(self._create_action("Switch Interactor Style", self.toggle_interactor_style))
        control_menu.addAction(self._create_action("Interaction Information Text", self.toggle_control_text))

        # Design-Menü
        design_menu = menu_bar.addMenu("Design")
        design_menu.addAction(self._create_action("Background Color", self.change_background_color))
        design_menu.addAction(self._create_action("Text Color", self.change_text_color))
        

    def _create_action(self, name, method, shortcut=None):
        """Hilfsmethode zum Erstellen von Aktionen."""
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(method)
        return action

    def toggle_control_text(self):
        """Wechselt die Sichtbarkeit des Steuerungstextes."""
        if self.is_text_visible:
            self.centralWidget().update_text_actor("")  # Text ausblenden
            self.is_text_visible = False
            self.statusBar().showMessage("Steuerungstext ausgeblendet")
        else:
            # Text basierend auf dem aktuellen Interactor Style anzeigen
            if self.current_interactor_style == "default":
                self.centralWidget().update_text_actor(self.DEFAULT_TEXT)
            elif self.current_interactor_style == "trackball":
                self.centralWidget().update_text_actor(self.TRACKBALL_TEXT)
            self.is_text_visible = True
            self.statusBar().showMessage("Steuerungstext angezeigt")

    def load_model(self):
        """Lädt ein Modell aus einer JSON-Datei."""
        filename, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if filename:
            if filename.lower().endswith(".json"):
                self.myModel.loadDatabase(Path(filename))
                self.statusBar().showMessage(f"Modell aus JSON geladen: {filename}")
                self.centralWidget().update_renderer(self.myModel)
                # Aktualisiere den Strukturbaum mit dem tatsächlichen Dateinamen
                self.update_structure_tree(file_name=Path(filename).name)
            else:
                self._show_message("Ungültiges Dateiformat", "Bitte wählen Sie eine JSON-Datei aus.")
        else:
            self.statusBar().showMessage("Modell-Laden abgebrochen")

    def save_model(self):
        """Speichert das aktuelle Modell in einer JSON-Datei."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Model File", "", "JSON Files (*.json)")
        if filename:
            self.myModel.saveDatabase(Path(filename))
            self.statusBar().showMessage(f"Modell gespeichert: {filename}")

    def import_fdd(self):
        """Importiert ein Modell aus einer FDD-Datei."""
        filename, _ = QFileDialog.getOpenFileName(self, "Import FDD File", "", "FDD Files (*.fdd)")
        if filename.lower().endswith(".fdd"):
            self.myModel.importFddFile(filename)
            self.statusBar().showMessage(f"FDD-Datei importiert: {filename}")
            self.centralWidget().update_renderer(self.myModel)
            # Aktualisiere den Strukturbaum mit dem tatsächlichen Dateinamen
            self.update_structure_tree(file_name=Path(filename).name)
        else:
            self._show_message("Ungültiges Dateiformat", "Bitte wählen Sie eine FDD-Datei aus.")

    def toggle_fullscreen(self):
        """Schaltet zwischen Vollbild und Standardgröße um."""
        if self.isFullScreen():
            self.showNormal()
            self.setGeometry(*self.WINDOW_GEOMETRY)
        else:
            self.showFullScreen()


    def toggle_interactor_style(self):
        """Wechselt zwischen dem Standard-Interactor und Trackball-Interactor."""
        render_window = self.centralWidget().GetRenderWindow()
        interactor = render_window.GetInteractor()

        if self.current_interactor_style == "default":
            trackball_style = vtk.vtkInteractorStyleTrackballCamera()
            interactor.SetInteractorStyle(trackball_style)
            self.current_interactor_style = "trackball"
            if self.is_text_visible:
                self.centralWidget().update_text_actor(self.TRACKBALL_TEXT)
            self.statusBar().showMessage("Trackball Interactor aktiviert")
        else:
            default_style = vtk.vtkInteractorStyleSwitch()
            interactor.SetInteractorStyle(default_style)
            self.current_interactor_style = "default"
            if self.is_text_visible:
                self.centralWidget().update_text_actor(self.DEFAULT_TEXT)
            self.statusBar().showMessage("Standard Interactor aktiviert")



    def reset_view(self):
        """Zentriert die Ansicht auf das Modell und setzt die Kamera zurück."""
        renderer = self.centralWidget().GetRenderer()
        camera = renderer.GetActiveCamera()
        
        # Berechne Bounding-Box des aktuellen Modells
        renderer.ResetCamera()  # Standard-Reset
        bounds = renderer.ComputeVisiblePropBounds()
        
        if bounds:
            center_x = (bounds[0] + bounds[1]) / 2.0
            center_y = (bounds[2] + bounds[3]) / 2.0
            center_z = (bounds[4] + bounds[5]) / 2.0
            camera.SetFocalPoint(center_x, center_y, center_z)
            
            # Setze Kamera-Position zurück (z. B. auf eine Distanz basierend auf Bounding-Box)
            diagonal = ((bounds[1] - bounds[0]) ** 2 + (bounds[3] - bounds[2]) ** 2 + (bounds[5] - bounds[4]) ** 2) ** 0.5
            camera.SetPosition(center_x, center_y, center_z + 2.0 * diagonal)  # Kamera etwas entfernt setzen
            camera.SetViewUp(0, 1, 0)  # Standard-Ausrichtung der Kamera

        renderer.ResetCameraClippingRange()  # Sicherstellen, dass die Clipping-Range korrekt ist
        self.centralWidget().GetRenderWindow().Render()
        self.statusBar().showMessage("Ansicht zurückgesetzt")


    def change_background_color(self):
        """Ändert die Hintergrundfarbe des Renderers."""
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = color.getRgbF()
            self.centralWidget().GetRenderer().SetBackground(r, g, b)
            self.centralWidget().GetRenderWindow().Render()

    def change_text_color(self):
        """Ändert die Farbe des Text-Actors."""
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = color.getRgbF()
            self.centralWidget().text_actor.GetTextProperty().SetColor(r, g, b)
            self.centralWidget().GetRenderWindow().Render()


    def set_front_view(self):
        self._set_camera_orientation(0, -1, 0, 0, 0, 1)
        self.statusBar().showMessage("Front-Ansicht")

    def set_back_view(self):
        self._set_camera_orientation(0, 1, 0, 0, 0, 1)
        self.statusBar().showMessage("Back-Ansicht")

    def set_left_view(self):
        self._set_camera_orientation(-1, 0, 0, 0, 0, 1)
        self.statusBar().showMessage("Left-Ansicht")

    def set_right_view(self):
        self._set_camera_orientation(1, 0, 0, 0, 0, 1)
        self.statusBar().showMessage("Right-Ansicht")

    def set_top_view(self):
        self._set_camera_orientation(0, 0, 1, 0, -1, 0)
        self.statusBar().showMessage("Top-Ansicht")

    def set_bottom_view(self):
        self._set_camera_orientation(0, 0, -1, 0, 1, 0)
        self.statusBar().showMessage("Bottom-Ansicht")

    def _set_camera_orientation(self, pos_x, pos_y, pos_z, up_x, up_y, up_z):
        """Hilfsmethode zum Einstellen der Kameraausrichtung."""
        renderer = self.centralWidget().GetRenderer()
        camera = renderer.GetActiveCamera()
        camera.SetPosition(pos_x, pos_y, pos_z)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(up_x, up_y, up_z)
        renderer.ResetCamera()
        self.centralWidget().GetRenderWindow().Render()

    def _show_message(self, title, text):
        """Zeigt eine Fehlermeldung an."""
        QMessageBox.critical(self, title, text)
