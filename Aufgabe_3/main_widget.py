import vtk
import QVTKRenderWindowInteractor as QVTK
from PySide6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QDialog, QLabel, QPushButton, QSlider, QVBoxLayout
from PySide6.QtCore import Qt
import mbsModel

class Widget(QVTK.QVTKRenderWindowInteractor):
    def __init__(self):
        super().__init__()

        self.myModel = mbsModel.mbsModel() # Modell anlegen
        self.renderer = vtk.vtkRenderer() # Renderer anlegen
        self.renderer.SetBackground(1.0, 1.0, 1.0) # standardmäßig weißer Hintergrund
        self.GetRenderWindow().AddRenderer(self.renderer) # Renderer dem Window hinzufügen

        self.text_actor = vtk.vtkTextActor() # Text Actor anlegen
        self.text_actor.SetPosition(10, 10)  # Position: links unten
        self.text_actor.GetTextProperty().SetFontSize(14) # Schriftgröße
        self.text_actor.GetTextProperty().SetColor(0, 0, 0)  # standardmäßig schwarzer Text
        self.renderer.AddActor2D(self.text_actor) # dem Renderer den Text Actor hinzufügen


    def getModel(self):
        # Übergabe des mbsModel (verwendet in main_window)
        return self.myModel

    def update_renderer(self, model):
        # Renderer aktualisieren
        model.showModel(self.renderer)  # Zeigt das neue Modell an
        self.renderer.ResetCamera()  # Kamera zurücksetzen
        self.GetRenderWindow().Render()  # Rendern des aktualisierten Fensters


    def update_text_actor(self, interactor_type):
        # Steuerungstext ändern
        DEFAULT_TEXT = ("DEFAULT Steuerung:\n" "- Linke Maustaste: Rotieren\n" "- Rechte Maustaste: Zoom\n" "- Shift + Linke Maustaste: Verschieben")
        TRACKBALL_TEXT = ("TRACKBALL Steuerung:\n""- Linke Maustaste: Rotieren\n""- Rechte Maustaste: Zoom\n""- Shift + Linke Maustaste: Verschieben")
        
        if interactor_type == "trackball":
            # wenn Interactor Typ Trackball, dann entsprechender Text
            self.text_actor.SetInput(TRACKBALL_TEXT)
        elif interactor_type == "default":
            # wenn Interactor Typ Default, dann entsprechender Text
            self.text_actor.SetInput(DEFAULT_TEXT)
        else:
            # im Startfall bzw. Initialisierungsfall nichts anzeigen
            self.text_actor.SetInput("")  
        self.GetRenderWindow().Render()  # Neu rendern


    def GetRenderer(self):
        # Renderer zurückgeben
        return self.renderer


    def create_structure_tree_dock(self):
        # Dock und Baum anlegen

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["File Name"])

        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu) # Kontextmenü aktivieren
        self.treeWidget.customContextMenuRequested.connect(self.show_context_menu)

        self.treeDockWidget = QDockWidget("Model Tree", self) # Dockwidget für den Strukturbaum erstellen
        self.treeDockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.treeDockWidget.setWidget(self.treeWidget) # tree-widget in das Dock Widget setzen

        self.update_structure_tree()  # Strukturbaum updaten
        return self.treeDockWidget
    

    def show_context_menu(self, position):
        # Kontextmenü anzeigen

        selected_item = self.treeWidget.itemAt(position)
        if selected_item is None or selected_item.parent() is None:
            return  # Nur auf Kind-Elementen aktiv

        context_menu = QMenu()
        change_transparency_action = context_menu.addAction("Transparenz ändern")
        action = context_menu.exec(self.treeWidget.mapToGlobal(position))

        if action == change_transparency_action:
            self.change_transparency(selected_item)


    def change_transparency(self, item):
        # Transparenzdialog mit Schieberegler

        body_name = item.text(0) # geklicktes Objekt
        body_obj = next((obj for obj in self.myModel.get_mbsObjectList() if obj.parameter.get("name", {}).get("value") == body_name), None)
        # schauen, ob es das Objekt wirklich gibt
        if body_obj is None:
            QMessageBox.warning(self, "Fehler", f"Objekt '{body_name}' nicht gefunden.")
            return

        # Dialog für Transparenz erstellen
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Transparenz für '{body_name}' ändern")
        layout = QVBoxLayout(dialog)

        label = QLabel("0 = sichtbar ----------------- 1 = unsichtbar:")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)  # Bereich von 0 bis 100
        slider.setValue(int(100 * (1 - body_obj.actors[0].GetProperty().GetOpacity())))  # Aktuellen Wert setzen

        apply_button = QPushButton("Übernehmen")
        apply_button.clicked.connect(lambda: self.apply_transparency(body_obj, slider.value() / 100, dialog))

        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(apply_button)
        dialog.setLayout(layout)
        dialog.exec()


    def apply_transparency(self, body_obj, transparency, dialog):
        # eingestellte Transparenz rendern

        for actor in body_obj.actors:
            actor.GetProperty().SetOpacity(1.0 - transparency)
        self.GetRenderWindow().Render()  # Neu rendern
        dialog.accept()


    def set_all_objects_visible(self):
        # Transparenz aller Objekte zurücksetzen

        for body_obj in self.myModel.get_mbsObjectList():
            for actor in body_obj.actors:
                actor.GetProperty().SetOpacity(1.0)  # Voll sichtbar
        self.GetRenderWindow().Render()


    def update_structure_tree(self, file_name="File Name"):
        # Strukturbaum updaten

        self.treeWidget.clear() # alten Baum löschen
        self.treeWidget.setHeaderLabels([file_name]) # Filename als Überschrift nehmen

        # Überschriften der verschiedenen Objekttypen
        self.rootBody = QTreeWidgetItem(["Bodies"])
        self.treeWidget.addTopLevelItem(self.rootBody)
        self.rootConstraint = QTreeWidgetItem(["Constraints"])
        self.treeWidget.addTopLevelItem(self.rootConstraint)
        self.rootForces = QTreeWidgetItem(["Forces"])
        self.treeWidget.addTopLevelItem(self.rootForces)
        self.rootMeasures = QTreeWidgetItem(["Measures"])
        self.treeWidget.addTopLevelItem(self.rootMeasures)

        # Objekte durschauen und deren Namen in der richtigen Überschrift auflisten
        for obj in self.myModel.get_mbsObjectList():
            name = obj.parameter["name"]["value"] if "name" in obj.parameter else "Unbekannter Name"
            if obj.getType() == "Body":
                self.childBody = QTreeWidgetItem([name])
                self.rootBody.addChild(self.childBody)
            elif obj.getType() == "Constraint":
                self.childConstraint = QTreeWidgetItem([name])
                self.rootConstraint.addChild(self.childConstraint)
            elif obj.getType() == "Force":
                self.childForce = QTreeWidgetItem([name])
                self.rootForces.addChild(self.childForce)
            elif obj.getType() == "Measure":
                self.childMeasure = QTreeWidgetItem([name])
                self.rootMeasures.addChild(self.childMeasure)

        self.treeWidget.expandAll() # Baum aufklappen