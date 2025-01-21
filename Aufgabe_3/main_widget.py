import vtk
import QVTKRenderWindowInteractor as QVTK
from PySide6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem
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

        self.treeDockWidget = QDockWidget("Model Tree", self)
        self.treeDockWidget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.treeDockWidget.setWidget(self.treeWidget)

        self.update_structure_tree()  # Strukturbaum updaten
        return self.treeDockWidget
    

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
            obj_type, name = self.myModel.get_object_type_and_name(obj)
            if obj_type == "Body":
                self.childBody = QTreeWidgetItem([name])
                self.rootBody.addChild(self.childBody)
            elif obj_type == "Constraint":
                self.childConstraint = QTreeWidgetItem([name])
                self.rootConstraint.addChild(self.childConstraint)
            elif obj_type == "Force":
                self.childForce = QTreeWidgetItem([name])
                self.rootForces.addChild(self.childForce)
            elif obj_type == "Measure":
                self.childMeasure = QTreeWidgetItem([name])
                self.rootMeasures.addChild(self.childMeasure)

        self.treeWidget.expandAll() # Baum aufklappen