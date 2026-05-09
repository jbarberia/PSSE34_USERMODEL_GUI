from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QDialog, QVBoxLayout, QLabel, QSpinBox, QPushButton, QLineEdit
from src.core import Port

class ConfigDialog(QDialog):
    def __init__(self, block, parent=None):
        super().__init__(parent)
        self.block = block
        self.setWindowTitle(f"Configure {block.block_name}")
        layout = QVBoxLayout()
        
        # Cada bloque añade sus propios campos
        self.fields = self.block.create_config_fields(layout)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def get_values(self):
        # Cada bloque sabe extraer sus valores
        return self.block.extract_config_values(self.fields)

class BaseBlock(QGraphicsRectItem):
    def __init__(self, name, x, y):
        super().__init__(0, 0, 120, 60)
        self.block_name = name
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

    def setup_ports(self, num_inputs=1):
        for port in self.input_ports:
            port.remove_all_connections()
            if self.scene(): self.scene().removeItem(port)
        self.input_ports = []

        height = max(60, num_inputs * 30)
        self.setRect(0, 0, 120, height)
        self.title.setPos(35, height / 2 - 10)

        for i in range(num_inputs):
            y_pos = (i + 1) * (height / (num_inputs + 1))
            self.input_ports.append(Port(self, 0, y_pos, "input"))

        if not self.output_port:
            self.output_port = Port(self, 120, height / 2, "output")
        else:
            self.output_port.setPos(120, height / 2)
            for conn in self.output_port.connections: conn.update_path()

    def mouseDoubleClickEvent(self, event):
        dialog = ConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_config(dialog.get_values())
        super().mouseDoubleClickEvent(event)

    def create_config_fields(self, layout):
        # Por defecto, solo una etiqueta
        layout.addWidget(QLabel(f"Generic settings for {self.block_name}"))
        return {}

    def extract_config_values(self, fields):
        return {}

    def apply_config(self, values):
        pass

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            for port in self.input_ports:
                for conn in port.connections: conn.update_path()
            if self.output_port:
                for conn in self.output_port.connections: conn.update_path()
        return super().itemChange(change, value)

class GainBlock(BaseBlock):
    def __init__(self, x, y):
        super().__init__("GAIN", x, y)
        self.gain_value = "1.0"
        self.setup_ports(1)

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("Gain Value:"))
        gain_edit = QLineEdit(self.gain_value)
        layout.addWidget(gain_edit)
        return {"gain": gain_edit}

    def extract_config_values(self, fields):
        return {"gain": fields["gain"].text()}

    def apply_config(self, values):
        self.gain_value = values.get("gain", "1.0")
        print(f"Gain changed to: {self.gain_value}")

class IntegratorBlock(BaseBlock):
    def __init__(self, x, y):
        super().__init__("INTEGRATOR", x, y)
        self.initial_condition = "0.0"
        self.setup_ports(1)

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("Initial Condition:"))
        ic_edit = QLineEdit(self.initial_condition)
        layout.addWidget(ic_edit)
        return {"ic": ic_edit}

    def extract_config_values(self, fields):
        return {"ic": fields["ic"].text()}

    def apply_config(self, values):
        self.initial_condition = values.get("ic", "0.0")
        print(f"Integrator IC changed to: {self.initial_condition}")

class SumBlock(BaseBlock):
    def __init__(self, x, y):
        super().__init__("SUM", x, y)
        self.num_inputs = 2
        self.setup_ports(self.num_inputs)

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("Number of Inputs:"))
        spin = QSpinBox()
        spin.setRange(1, 10)
        spin.setValue(self.num_inputs)
        layout.addWidget(spin)
        return {"num_inputs": spin}

    def extract_config_values(self, fields):
        return {"num_inputs": fields["num_inputs"].value()}

    def apply_config(self, values):
        self.num_inputs = values.get("num_inputs", 2)
        self.setup_ports(self.num_inputs)
