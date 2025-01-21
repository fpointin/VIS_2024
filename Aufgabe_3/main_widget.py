import vtk
import QVTKRenderWindowInteractor as QVTK
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QTreeView
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
        # Strukturbaum mit Dock Widget erstellen 

        dock_widget = QDockWidget("Strukturbaum", self) # anlegen des Docks
        dock_widget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable) # Dock verschiebbar machen
        
        tree_widget = QWidget() # Strukturbaum ist ein QWidget
        layout = QVBoxLayout(tree_widget) # layout ist ein QVBoxLayout

        self.tree_model = QStandardItemModel() # Anlegen des Strukturbaums als StandardItemModel
        self.tree_view = QTreeView() # Anlegen des Tree-Views

        self.tree_view.setModel(self.tree_model) # StandardItemModel in tree-view übergeben
        layout.addWidget(self.tree_view) # den tree-view ins Layout geben
        self.update_structure_tree() # Strukturbaum updaten 
        dock_widget.setWidget(tree_widget) # den Strukturbaum ins Dock setzen

        return dock_widget
    

    def update_structure_tree(self, file_name="File Name"):
        # Strukturbaum updaten

        self.tree_model.clear() # Modellbaum löschen

        root_item = QStandardItem(file_name) # Dateinamen als Überschrift setzen
        root_item.setEditable(False)  
        self.tree_model.appendRow(root_item) # Die Überschrift als StandardItem dem tree-model anhängen

        # Überschriften für die jeweiligen Objekt-Arten
        rigid_bodies_item = QStandardItem("Rigid Bodies")
        rigid_bodies_item.setEditable(False)
        constraints_item = QStandardItem("Constraints")
        constraints_item.setEditable(False)
        forces_item = QStandardItem("Forces")
        forces_item.setEditable(False)
        measures_item = QStandardItem("Measures")
        measures_item.setEditable(False)

        # Objekte durschauen und deren Namen in der richtigen Überschrift auflisten
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

        # die gelesenen Objekte (Überschrift + einzelne Objekte) zum Root-Item (Dateiname/Überschrift) hinzufügen
        root_item.appendRow(rigid_bodies_item)
        root_item.appendRow(constraints_item)
        root_item.appendRow(forces_item)
        root_item.appendRow(measures_item)

        self.tree_view.expandAll() # Baum aufklappen