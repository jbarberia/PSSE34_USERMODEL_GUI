from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsTextItem, QDialog, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QCheckBox)
from PyQt5.QtGui import QPen, QFont
from ..core import Port

class ConfigDialog(QDialog):
    def __init__(self, block, parent=None):
        super().__init__(parent)
        self.block = block
        self.setWindowTitle(f"Configure {block.block_name}")
        layout = QVBoxLayout()
        
        self.show_windup = not getattr(block, 'disable_windup_config', False)
        
        if self.show_windup:
            self.limit_cb = QCheckBox("Enable Non-Windup Limit")
            self.limit_cb.setChecked(getattr(block, 'limit_enabled', False))
            layout.addWidget(self.limit_cb)

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

        self.fields = self.block.create_config_fields(layout)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def get_values(self):
        values = self.block.extract_config_values(self.fields)
        if self.show_windup:
            values['limit_enabled'] = self.limit_cb.isChecked()
            values['limit_min'] = self.min_edit.text()
            values['limit_max'] = self.max_edit.text()
        else:
            values['limit_enabled'] = False
        return values

class BaseBlock(QGraphicsRectItem):
    def __init__(self, name, x, y, width=120, height=60):
        super().__init__(0, 0, width, height)
        self.block_name = name
        self.width = width
        self.height = height
        
        self.limit_enabled = False
        self.limit_min = -1.0
        self.limit_max = 1.0
        self.disable_windup_config = False
        
        self.setBrush(Qt.lightGray)
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemSendsGeometryChanges
        )
        
        self.mono_font = QFont("Courier New", 10)
        self.mono_font.setFixedPitch(True)
        
        self.title = QGraphicsTextItem(name, self)
        self.title.setFont(self.mono_font)
        
        self.subtitle = QGraphicsTextItem("", self)
        self.subtitle_font = QFont("Courier New", 8)
        self.subtitle.setFont(self.subtitle_font)
        self.subtitle.setDefaultTextColor(Qt.blue)
        
        self.input_ports = []
        self.output_port = None
        self.setPos(x, y)

    def paint(self, painter, option, widget):
        if self.isSelected():
            pen = QPen(Qt.black, 2, Qt.DashLine)
        else:
            pen = QPen(Qt.black, 1)
        
        painter.setPen(pen)
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())

        if self.limit_enabled:
            rect = self.rect()
            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.drawLine(rect.bottomLeft(), rect.topRight())
            
            painter.setFont(self.subtitle_font)
            # painter.drawText(rect.adjusted(5, 2, 0, 0), Qt.AlignLeft | Qt.AlignTop, str(self.limit_max))
            # painter.drawText(rect.adjusted(0, 0, -5, -2), Qt.AlignRight | Qt.AlignBottom, str(self.limit_min))

    def setup_ports(self, num_inputs=1, has_output=True):
        for port in self.input_ports:
            port.remove_all_connections()
            if self.scene(): self.scene().removeItem(port)
        self.input_ports = []

        calculated_height = max(self.height, num_inputs * 30)
        self.setRect(0, 0, self.width, calculated_height)
        
        self.center_text()
        self.update_subtitle_pos()

        for i in range(num_inputs):
            y_pos = (i + 1) * (calculated_height / (num_inputs + 1))
            self.input_ports.append(Port(self, 0, y_pos, "input"))

        if has_output:
            if not self.output_port:
                self.output_port = Port(self, self.width, calculated_height / 2, "output")
            else:
                self.output_port.setPos(self.width, calculated_height / 2)
                for conn in self.output_port.connections: conn.update_path()
        else:
            if self.output_port:
                self.output_port.remove_all_connections()
                if self.scene(): self.scene().removeItem(self.output_port)
                self.output_port = None

    def center_text(self):
        rect = self.rect()
        # Centrado horizontal y vertical
        tw = self.title.boundingRect().width()
        th = self.title.boundingRect().height()
        self.title.setPos(0,0)
        #rect.width()/2 - tw/2, rect.height()/2 - th/2)

    def update_subtitle_pos(self):
        rect = self.rect()
        self.subtitle.setPos(0, rect.height() + 2)

    def set_subtitle_text(self, text):
        # Si hay windup, agregarlo al final del texto en una linea nueva o al lado
        if self.limit_enabled:
            text += f"\nLOLIM={self.limit_min}"
            text += f"\nHILIM={self.limit_max}"            
        self.subtitle.setPlainText(text)
        self.update_subtitle_pos()

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
        self.update()
        # Llamar a refresh_ui o similar si existe para actualizar subtitulo
        if hasattr(self, 'refresh_ui'):
            self.refresh_ui()

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
