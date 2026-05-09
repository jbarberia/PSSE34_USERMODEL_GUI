from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPolygonF
from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class GainBlock(BaseBlock):
    def __init__(self, x, y):
        # Ganancia suele ser mas pequeña o cuadrada
        super().__init__("GAIN", x, y, width=80, height=80)
        self.gain_value = "1.0"
        self.title.setPlainText(self.gain_value)
        self.setup_ports(1)

    def paint(self, painter, option, widget):
        painter.setRenderHint(painter.Antialiasing)
        
        if self.isSelected():
            pen = QPen(Qt.black, 2, Qt.DashLine)
        else:
            pen = QPen(Qt.black, 1)
            
        painter.setPen(pen)
        painter.setBrush(self.brush())
        
        rect = self.rect()
        triangle = QPolygonF([
            rect.topLeft(),
            rect.bottomLeft(),
            QPointF(rect.right(), rect.top() + rect.height()/2)
        ])
        painter.drawPolygon(triangle)

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("Gain Value:"))
        gain_edit = QLineEdit(self.gain_value)
        layout.addWidget(gain_edit)
        return {"gain": gain_edit}

    def extract_config_values(self, fields):
        return {"gain": fields["gain"].text()}

    def apply_config(self, values):
        self.gain_value = values.get("gain", "1.0")
        self.title.setPlainText(self.gain_value)
        # Re-centrar el titulo ya que el texto cambio
        self.title.setPos(self.width / 2 - self.title.boundingRect().width() / 2, 
                         self.rect().height() / 2 - self.title.boundingRect().height() / 2)
        print(f"Gain changed to: {self.gain_value}")
