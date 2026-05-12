from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsTextItem, QDialog, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QCheckBox)
from PyQt5.QtGui import QPen, QFont
from app.models.core import Port

class ConfigDialog(QDialog):
    def __init__(self, block, parent=None):
        super().__init__(parent)
        self.block = block
        self.setWindowTitle(f"Configure {block.block_name}")
        layout = QVBoxLayout()
        
        # Usar la nueva funcion unificada de construcción de UI
        self.fields = self.block.build_config_ui(layout)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def get_values(self):
        return self.block.extract_config_values(self.fields)

class BaseBlock(QGraphicsRectItem):
    def __init__(self, name, x, y, width=120, height=60, block_id=None):
        super().__init__(0, 0, width, height)
        self.block_name = name
        self.width = width
        self.height = height
        
        # Atributos de bloque
        self.block_id = block_id if block_id else name
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
        
        self.id_label = QGraphicsTextItem(self.block_id, self)
        self.id_font = QFont("Courier New", 9, QFont.Bold)
        self.id_label.setFont(self.id_font)
        self.id_label.setDefaultTextColor(Qt.red)
        
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
            painter.drawLine(rect.bottomLeft() + QPointF(-10, 10), rect.topRight()   + QPointF(10, -10))
            painter.drawLine(rect.bottomLeft() + QPointF(-10, 10), rect.bottomLeft() + QPointF(-20, 10))
            painter.drawLine(rect.topRight() + QPointF(10, -10), rect.topRight() + QPointF(20, -10))
            

    def build_config_ui(self, layout):
        """Construye la UI de configuración de forma unificada para Dialogo y Panel Lateral"""
        fields = {}
        
        # 1. Campo ID (Siempre presente)
        layout.addWidget(QLabel("<b>Block Identification</b>"))
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Unique ID:"))
        self.id_edit = QLineEdit(self.block_id)
        id_layout.addWidget(self.id_edit)
        layout.addLayout(id_layout)
        fields['id_edit'] = self.id_edit

        # 2. Windup Limits (Opcional segun el bloque)
        if not self.disable_windup_config:
            layout.addWidget(QLabel("<b>Non-Windup Limits</b>"))
            limit_cb = QCheckBox("Enable Limit")
            limit_cb.setChecked(self.limit_enabled)
            layout.addWidget(limit_cb)
            fields['limit_cb'] = limit_cb

            limit_box = QHBoxLayout()
            min_edit = QLineEdit(str(self.limit_min))
            max_edit = QLineEdit(str(self.limit_max))
            limit_box.addWidget(QLabel("Min:"))
            limit_box.addWidget(min_edit)
            limit_box.addWidget(QLabel("Max:"))
            limit_box.addWidget(max_edit)
            layout.addLayout(limit_box)
            fields['min_edit'] = min_edit
            fields['max_edit'] = max_edit
            
            def toggle_limits(state):
                min_edit.setEnabled(state == Qt.Checked)
                max_edit.setEnabled(state == Qt.Checked)
            limit_cb.stateChanged.connect(toggle_limits)
            toggle_limits(limit_cb.checkState())

        # 3. Campos específicos del bloque
        layout.addWidget(QLabel("<b>Parameters</b>"))
        specific_fields = self.create_config_fields(layout)
        fields['specific'] = specific_fields
        
        return fields

    def extract_config_values(self, fields):
        """Extrae los valores de los campos creados en build_config_ui"""
        values = {}
        
        # ID
        values['block_id'] = fields['id_edit'].text().strip() or self.block_id
        
        # Windup
        if 'limit_cb' in fields:
            values['limit_enabled'] = fields['limit_cb'].isChecked()
            values['limit_min'] = fields['min_edit'].text()
            values['limit_max'] = fields['max_edit'].text()
        else:
            values['limit_enabled'] = False
            
        # Especificos
        spec_values = self.extract_block_specific_values(fields['specific'])
        values.update(spec_values)
        
        return values

    def extract_block_specific_values(self, fields):
        """Sobrescribir en subclases en lugar de extract_config_values directo"""
        return {}

    def setup_ports(self, num_inputs=1, has_output=True):
        for port in self.input_ports:
            port.remove_all_connections()
            if self.scene(): self.scene().removeItem(port)
        self.input_ports = []

        calculated_height = max(self.height, num_inputs * 30)
        self.setRect(0, 0, self.width, calculated_height)
        
        self.center_text()
        self.update_subtitle_pos()
        self.update_id_label_pos()

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
        tw = self.title.boundingRect().width()
        th = self.title.boundingRect().height()
        self.title.setPos(0, 0) # rect.width()/2 - tw/2, rect.height()/2 - th/2)

    def update_subtitle_pos(self):
        rect = self.rect()
        self.subtitle.setPos(0, rect.height() + 2)

    def update_id_label_pos(self):
        th = self.id_label.boundingRect().height()
        self.id_label.setPos(0, -th - 2)

    def set_subtitle_text(self, text):
        if self.limit_enabled:
            text += f" [LIM: {self.limit_min}, {self.limit_max}]"
        self.subtitle.setPlainText(text)
        self.update_subtitle_pos()

    def mouseDoubleClickEvent(self, event):
        dialog = ConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_config(dialog.get_values())
        super().mouseDoubleClickEvent(event)

    def create_config_fields(self, layout):
        return {}

    def apply_config(self, values):
        self.block_id = values.get('block_id', self.block_id)
        self.id_label.setPlainText(self.block_id)
        
        self.limit_enabled = values.get('limit_enabled', False)
        self.limit_min = values.get('limit_min', self.limit_min)
        self.limit_max = values.get('limit_max', self.limit_max)
        self.update()
        if hasattr(self, 'refresh_ui'):
            self.refresh_ui()
        elif hasattr(self, 'update_title'):
            self.update_title()

    def get_config(self):
        return {
            "block_id": self.block_id,
            "limit_enabled": self.limit_enabled,
            "limit_min": self.limit_min,
            "limit_max": self.limit_max
        }

    @staticmethod
    def get_fortran_code(cfg, mode, in_vars, out_var, k_idx, target_in_var=None):
        """
        Base implementation for Fortran code generation.
        To be overridden by subclasses.
        """
        code_lines = []
        # Common limit logic
        if cfg.get("limit_enabled") and cfg.get("type") not in ["PI"]:
            if mode in [2, 3]:
                l_min = cfg.get("limit_min", "-1.0")
                l_max = cfg.get("limit_max", "1.0")
                code_lines.append(f"{out_var} = MAX({l_min}, MIN({l_max}, {out_var}))")
        return code_lines

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for port in self.input_ports:
                for conn in port.connections: conn.update_path()
            if self.output_port:
                for conn in self.output_port.connections: conn.update_path()
        return super().itemChange(change, value)

