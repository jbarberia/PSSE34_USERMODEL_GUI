from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsTextItem, QDialog, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QCheckBox)
from PyQt5.QtGui import QPen, QPainter
from ..core import Port

class ConfigDialog(QDialog):
    def __init__(self, block, parent=None):
        super().__init__(parent)
        self.block = block
        self.setWindowTitle(f"Configure {block.block_name}")
        layout = QVBoxLayout()
        
        # Checkbox universal para Non-windup
        self.limit_cb = QCheckBox("Enable Non-Windup Limit")
        self.limit_cb.setChecked(getattr(block, 'limit_enabled', False))
        layout.addWidget(self.limit_cb)

        # Contenedor para limites (se habilitan/deshabilitan)
        self.limit_layout = QHBoxLayout()
        self.min_edit = QLineEdit(str(getattr(block, 'limit_min', -1.0)))
        self.max_edit = QLineEdit(str(getattr(block, 'limit_max', 1.0)))
        self.limit_layout.addWidget(QLabel("Min:"))
        self.limit_layout.addWidget(self.min_edit)
        self.limit_layout.addWidget(QLabel("Max:"))
        self.limit_layout.addWidget(self.max_edit)
        layout.addLayout(self.limit_layout)
        
        def toggle_limits(state):
            self.min_edit.setEnabled(state == Qt.Checked)
            self.max_edit.setEnabled(state == Qt.Checked)
        
        self.limit_cb.stateChanged.connect(toggle_limits)
        toggle_limits(self.limit_cb.checkState())

        layout.addSpacing(10)
        layout.addWidget(QLabel("--- Parameters ---"))

        # Cada bloque añade sus propios campos
        self.fields = self.block.create_config_fields(layout)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def get_values(self):
        values = self.block.extract_config_values(self.fields)
        values['limit_enabled'] = self.limit_cb.isChecked()
        values['limit_min'] = self.min_edit.text()
        values['limit_max'] = self.max_edit.text()
        return values

class BaseBlock(QGraphicsRectItem):
    def __init__(self, name, x, y, width=120, height=60):
        super().__init__(0, 0, width, height)
        self.block_name = name
        self.width = width
        self.height = height
        
        # Atributos de limite comunes
        self.limit_enabled = False
        self.limit_min = -1.0
        self.limit_max = 1.0
        
        self.setBrush(Qt.lightGray)
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemSendsGeometryChanges
        )
        self.title = QGraphicsTextItem(name, self)
        self.input_ports = []
        self.output_port = None
        self.setPos(x, y)

    def paint(self, painter, option, widget):
        # Dibujar el rectangulo base (o lo que defina el bloque)
        if self.isSelected():
            pen = QPen(Qt.black, 2, Qt.DashLine)
        else:
            pen = QPen(Qt.black, 1)
        
        painter.setPen(pen)
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())

        # Dibujar indicadores de limite si estan habilitados
        if self.limit_enabled:
            rect = self.rect()
            # Linea diagonal detras (de abajo-izquierda a arriba-derecha)
            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.drawLine(rect.bottomLeft(), rect.topRight())
            
            # Texto de los limites
            old_font = painter.font()
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            
            # Maximo arriba a la izquierda
            painter.drawText(rect.adjusted(5, 2, 0, 0), Qt.AlignLeft | Qt.AlignTop, str(self.limit_max))
            # Minimo abajo a la derecha
            painter.drawText(rect.adjusted(0, 0, -5, -2), Qt.AlignRight | Qt.AlignBottom, str(self.limit_min))
            
            painter.setFont(old_font)

    def setup_ports(self, num_inputs=1):
        for port in self.input_ports:
            port.remove_all_connections()
            if self.scene(): self.scene().removeItem(port)
        self.input_ports = []

        calculated_height = max(self.height, num_inputs * 30)
        self.setRect(0, 0, self.width, calculated_height)
        
        self.title.setPos(self.width / 2 - self.title.boundingRect().width() / 2, 
                         calculated_height / 2 - self.title.boundingRect().height() / 2)

        for i in range(num_inputs):
            y_pos = (i + 1) * (calculated_height / (num_inputs + 1))
            self.input_ports.append(Port(self, 0, y_pos, "input"))

        if not self.output_port:
            self.output_port = Port(self, self.width, calculated_height / 2, "output")
        else:
            self.output_port.setPos(self.width, calculated_height / 2)
            for conn in self.output_port.connections: conn.update_path()

    def mouseDoubleClickEvent(self, event):
        dialog = ConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_config(dialog.get_values())
        super().mouseDoubleClickEvent(event)

    def create_config_fields(self, layout):
        return {}

    def extract_config_values(self, fields):
        return {}

    def apply_config(self, values):
        self.limit_enabled = values.get('limit_enabled', False)
        self.limit_min = values.get('limit_min', -1.0)
        self.limit_max = values.get('limit_max', 1.0)
        # Forzar repintado para mostrar/ocultar raya diagonal
        self.update()

    def get_config(self):
        return {
            "limit_enabled": self.limit_enabled,
            "limit_min": self.limit_min,
            "limit_max": self.limit_max
        }

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for port in self.input_ports:
                for conn in port.connections: conn.update_path()
            if self.output_port:
                for conn in self.output_port.connections: conn.update_path()
        return super().itemChange(change, value)
