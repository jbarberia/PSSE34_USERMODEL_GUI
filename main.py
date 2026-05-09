import sys
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QMainWindow,
)


class Port(QGraphicsEllipseItem):
    def __init__(self, parent, x, y, port_type):
        super().__init__(-5, -5, 10, 10, parent)
        self.port_type = port_type  # "input" or "output"

        if port_type == "input":
            self.setBrush(Qt.green)
        else:
            self.setBrush(Qt.red)

        self.setPos(x, y)
        self.connections = []

    def center_in_scene(self):
        return self.mapToScene(self.rect().center())


class Connection(QGraphicsPathItem):
    def __init__(self, port1, port2=None):
        super().__init__()
        self.port1 = port1
        self.port2 = port2

        self.setFlags(
            QGraphicsPathItem.ItemIsSelectable
        )

        pen = QPen(Qt.blue, 2)
        self.setPen(pen)

        if port1 and port2:
            self.update_path()
            # No los agregamos aquí si es temporal, solo si port2 existe
            port1.connections.append(self)
            port2.connections.append(self)

    def paint(self, painter, option, widget):
        if self.isSelected():
            pen = QPen(Qt.yellow, 3, Qt.SolidLine)
        else:
            pen = QPen(Qt.blue, 2)
        
        self.setPen(pen)
        super().paint(painter, option, widget)

    def remove(self):
        if self.port1:
            if self in self.port1.connections:
                self.port1.connections.remove(self)
        if self.port2:
            if self in self.port2.connections:
                self.port2.connections.remove(self)
        if self.scene():
            self.scene().removeItem(self)

    def update_path(self, pos2=None):
        p1 = self.port1.center_in_scene()
        if pos2:
            p2 = pos2
        else:
            p2 = self.port2.center_in_scene()

        path = QPainterPath()
        path.moveTo(p1)

        dx = (p2.x() - p1.x()) * 0.5

        path.cubicTo(
            p1.x() + dx,
            p1.y(),
            p2.x() - dx,
            p2.y(),
            p2.x(),
            p2.y(),
        )

        self.setPath(path)


class Block(QGraphicsRectItem):
    def __init__(self, name, x, y):
        super().__init__(0, 0, 120, 60)

        self.setBrush(Qt.lightGray)

        self.setFlags(
            QGraphicsRectItem.ItemIsMovable
            | QGraphicsRectItem.ItemIsSelectable
            | QGraphicsRectItem.ItemSendsGeometryChanges
        )

        self.title = QGraphicsTextItem(name, self)
        self.title.setPos(35, 20)

        # puerto entrada (verde)
        self.input_port = Port(self, 0, 30, "input")

        # puerto salida (rojo)
        self.output_port = Port(self, 120, 30, "output")

        self.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for conn in self.input_port.connections:
                conn.update_path()

            for conn in self.output_port.connections:
                conn.update_path()

        return super().itemChange(change, value)


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
                elif isinstance(item, Block):
                    # Al borrar un bloque, borrar sus conexiones
                    for conn in item.input_port.connections[:]:
                        conn.remove()
                    for conn in item.output_port.connections[:]:
                        conn.remove()
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
            # Buscar el puerto debajo del cursor ignorando la conexión temporal
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
                
                # Completar la conexión
                self.temp_connection.port2 = port
                port.connections.append(self.temp_connection)
                self.start_port.connections.append(self.temp_connection)
                self.temp_connection.update_path()
            else:
                # Cancelar conexión temporal
                self.scene().removeItem(self.temp_connection)
            
            self.temp_connection = None
            self.start_port = None

        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Control Block Editor")
        self.resize(1000, 600)

        scene = QGraphicsScene()

        view = GraphicsView(scene)

        self.setCentralWidget(view)

        # bloques ejemplo
        block1 = Block("GAIN", 100, 100)
        block2 = Block("INTEGRATOR", 400, 250)
        block3 = Block("SUM", 700, 150)

        scene.addItem(block1)
        scene.addItem(block2)
        scene.addItem(block3)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())
