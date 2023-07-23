from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDockWidget, QSizePolicy, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from qgis.core import QgsMapLayer, QgsProject, QgsRectangle
from qgis.gui import *

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import QEvent

from qgis.PyQt.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QAction, QToolBar

def getAllVisibleLayers():
    project = QgsProject.instance()
    layer_tree = project.layerTreeRoot()
    layer_list = layer_tree.findLayers()
    visible_layers = []
    for layer in layer_list:
        if layer.isVisible():
            visible_layers.append(layer.layer())
    return visible_layers

class MinimapDock(QDockWidget):

    def __init__(self, iface):
        super().__init__()

        # Set some properties for the dock widget
        self.setWindowTitle("Minimap")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(Qt.white)
        self.setFixedSize(400, 300)
        self.iface = iface

        # Create a widget to hold the contents of the dock widget
        self.contents = QWidget()
        self.layout = QVBoxLayout()
        self.contents.setLayout(self.layout)

        main_canvas = self.iface.mapCanvas()
        crs = main_canvas.mapSettings().destinationCrs()

        self.canvas.setDestinationCrs(crs)
        layers = getAllVisibleLayers()
        active_layer = self.iface.activeLayer()
        if active_layer is not None:
            self.canvas.setExtent(active_layer.extent())
        self.canvas.setLayers(layers)
    
        # Add the widget to the dock
        self.setWidget(self.canvas)


        self.actionZoomIn = QAction(QIcon(':/images/actions/zoom-in.png'), "Zoom in", self)
        self.actionZoomOut = QAction(QIcon(':/images/actions/zoom-out.png'), "Zoom out", self)
        self.actionPan = QAction(QIcon(':/images/actions/pan.png'), "Pan", self)
        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)
        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionPan.triggered.connect(self.pan)
        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolZoomOut.setAction(self.actionZoomOut)
        self.pan()

        


    def zoomIn(self):
        self.canvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        self.canvas.setMapTool(self.toolPan)
    def mist(self, tett=False):
        pass
    
class MinimapPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.layers = getAllVisibleLayers()
        self.my_dock = None

    def initGui(self):
        # Create a new dock widget instance
        self.my_dock = MinimapDock(self.iface)

        # Add the dock widget to the interface
        # Create a new toolbar instance
        self.toolbar = QToolBar("Minimap toolbar")

        # Add a button to the toolbar
        self.action = QAction(QIcon("icon.png"), "Turn on minimap", self.toolbar)
        self.action.setCheckable(True)
        self.toolbar.addAction(self.action)

        self.refresh_action = QAction(QIcon("icon.png"),'Refresh', self.toolbar)
        self.toolbar.addAction(self.refresh_action)

        # Add the toolbar to the interface
        self.iface.addToolBar(self.toolbar)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.my_dock)

        self.action.toggled.connect(self.on_button_toggled)
        self.refresh_action.triggered.connect(self.refresh)

        self.toolbar.show()

    def unload(self):
        self.my_dock.deleteLater()
        self.iface.removeDockWidget(self.my_dock)
        self.iface.removePluginMenu("My Dock", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeToolBarIcon(self.refresh_action)

        self.toolbar.deleteLater()
        self.iface.mainWindow().removeToolBar(self.toolbar)

    def on_button_toggled(self, checked):
        if checked:
            self.my_dock.show()
        else:
            self.my_dock.hide()
    
    def refresh(self):
        self.my_dock.canvas.refresh()
        layers = getAllVisibleLayers()
        main_canvas = self.iface.mapCanvas()
        crs = main_canvas.mapSettings().destinationCrs()
        self.my_dock.canvas.setDestinationCrs(crs)
        self.my_dock.canvas.setLayers(layers)
        active_layer = self.iface.activeLayer()