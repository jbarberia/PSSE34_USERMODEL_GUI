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
    def __init__(self, parent, x, y):
        super().__init__(-5, -5, 10, 10, parent)

        self.setBrush(Qt.black)
        self.setPos(x, y)

        self.connections = []

    def center_in_scene(self):
        return self.mapToScene(self.rect().center())


class Connection(QGraphicsPathItem):
    def __init__(self, port1, port2):
        super().__init__()

        self.port1 = port1
        self.port2 = port2

        pen = QPen(Qt.blue, 2)
        self.setPen(pen)

        self.update_path()

        port1.connections.append(self)
        port2.connections.append(self)

    def update_path(self):
        p1 = self.port1.center_in_scene()
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

        # puerto entrada
        self.input_port = Port(self, 0, 30)

        # puerto salida
        self.output_port = Port(self, 120, 30)

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

        # self.setRenderHint(self.renderHints())

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())

        if isinstance(item, Port):
            self.start_port = item

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())

        if isinstance(item, Port):
            if self.start_port and item != self.start_port:
                conn = Connection(self.start_port, item)
                self.scene().addItem(conn)

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
