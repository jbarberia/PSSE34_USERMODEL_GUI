import math
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem

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

    def remove_all_connections(self):
        for conn in self.connections[:]:
            conn.remove()


class Connection(QGraphicsPathItem):
    def __init__(self, port1, port2=None):
        super().__init__()
        self.port1 = port1
        self.port2 = port2

        self.setFlags(QGraphicsPathItem.ItemIsSelectable)
        pen = QPen(Qt.blue, 2)
        self.setPen(pen)

        if port1 and port2:
            self.update_path()
            port1.connections.append(self)
            port2.connections.append(self)

    def paint(self, painter, option, widget):
        if self.isSelected():
            pen = QPen(Qt.yellow, 3, Qt.SolidLine)
        else:
            pen = QPen(Qt.blue, 2)
        
        painter.setPen(pen)
        painter.drawPath(self.path())

        # Dibujar flecha al final de la linea
        path = self.path()
        percent = 1.0
        point = path.pointAtPercent(percent)
        angle = path.angleAtPercent(percent) # Grados en sentido antihorario desde eje X

        # Convertir a radianes y ajustar para el sistema de coordenadas de Qt (Y hacia abajo)
        rad = math.radians(-angle)

        arrow_size = 10
        # Puntos de la cabeza de la flecha
        p1 = point + QPointF(math.cos(rad + 3.5) * arrow_size, math.sin(rad + 3.5) * arrow_size)
        p2 = point + QPointF(math.cos(rad - 3.5) * arrow_size, math.sin(rad - 3.5) * arrow_size)

        arrow_head = QPolygonF([point, p1, p2])
        painter.setBrush(pen.color())
        painter.drawPolygon(arrow_head)

    def remove(self):
        if self.port1 and self in self.port1.connections:
            self.port1.connections.remove(self)
        if self.port2 and self in self.port2.connections:
            self.port2.connections.remove(self)
        if self.scene():
            self.scene().removeItem(self)

    def update_path(self, pos2=None):
        p1 = self.port1.center_in_scene()
        p2 = pos2 if pos2 else self.port2.center_in_scene()

        path = QPainterPath()
        path.moveTo(p1)
        dx = (p2.x() - p1.x()) * 0.5
        path.cubicTo(p1.x() + dx, p1.y(), p2.x() - dx, p2.y(), p2.x(), p2.y())
        self.setPath(path)
