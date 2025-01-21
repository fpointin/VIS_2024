import vtk
import QVTKRenderWindowInteractor as QVTK
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QDockWidget, QListView, QVBoxLayout, QWidget, QTreeView, QColorDialog
from PySide6.QtCore import Qt
import mbsModel

class Widget(QVTK.QVTKRenderWindowInteractor):
    def __init__(self):
        super().__init__()

        self.myModel = mbsModel.mbsModel()

        # Initialisiere Renderer und füge ihn zum RenderWindow hinzu
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0) # weißer Hintergrund
        self.GetRenderWindow().AddRenderer(self.renderer)

        # Text-Annotation hinzufügen
        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetPosition(10, 10)  # Position: links unten
        self.text_actor.GetTextProperty().SetFontSize(14)
        self.text_actor.GetTextProperty().SetColor(0, 0, 0)  # Schwarzer Text
        self.renderer.AddActor2D(self.text_actor)

        # # Strukturbaum-Dock-Widget hinzufügen
        # self.structure_tree_dock = self.create_structure_tree_dock()
        # self.addDockWidget(Qt.LeftDockWidgetArea, self.structure_tree_dock)

    def getModel(self):
        return self.myModel

    def update_renderer(self, model):
        """Aktualisiert den Renderer mit einem neuen Modell."""
        #self.renderer.RemoveAllViewProps()  # Entfernt alte Modelle
        model.showModel(self.renderer)  # Zeigt das neue Modell an
        self.renderer.ResetCamera()  # Kamera zurücksetzen
        self.GetRenderWindow().Render()  # Rendern des aktualisierten Fensters

    def update_text_actor(self, text):
        """Aktualisiert den Text des Text-Actors."""
        self.text_actor.SetInput(text)  # Text setzen
        self.GetRenderWindow().Render()  # Neu rendern

    def GetRenderer(self):
        return self.renderer

    def create_structure_tree_dock(self):
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