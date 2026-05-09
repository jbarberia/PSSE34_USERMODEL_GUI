from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView
from .core import Port, Connection
from .blocks.base import BaseBlock

class GraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.temp_connection = None
        self.start_port = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.scene().selectedItems():
                if isinstance(item, Connection):
                    item.remove()
                elif isinstance(item, BaseBlock):
                    for port in item.input_ports:
                        port.remove_all_connections()
                    if item.output_port:
                        item.output_port.remove_all_connections()
                    self.scene().removeItem(item)
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, Port) and item.port_type == "output":
            self.start_port = item
            self.temp_connection = Connection(self.start_port)
            self.scene().addItem(self.temp_connection)
            self.temp_connection.update_path(self.mapToScene(event.pos()))
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_connection:
            self.temp_connection.update_path(self.mapToScene(event.pos()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_connection:
            scene_pos = self.mapToScene(event.pos())
            items = self.scene().items(scene_pos)
            port = None
            for item in items:
                if isinstance(item, Port):
                    port = item
                    break
            
            if (port and 
                port.port_type == "input" and 
                port.parentItem() != self.start_port.parentItem()):
                
                self.temp_connection.port2 = port
                port.connections.append(self.temp_connection)
                self.start_port.connections.append(self.temp_connection)
                self.temp_connection.update_path()
            else:
                self.scene().removeItem(self.temp_connection)
            
            self.temp_connection = None
            self.start_port = None

        super().mouseReleaseEvent(event)
