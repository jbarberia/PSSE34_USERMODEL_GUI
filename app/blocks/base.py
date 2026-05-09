from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QDialog, QVBoxLayout, QLabel, QPushButton
from ..core import Port

class ConfigDialog(QDialog):
    def __init__(self, block, parent=None):
        super().__init__(parent)
        self.block = block
        self.setWindowTitle(f"Configure {block.block_name}")
        layout = QVBoxLayout()
        self.fields = self.block.create_config_fields(layout)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def get_values(self):
        return self.block.extract_config_values(self.fields)

class BaseBlock(QGraphicsRectItem):
    def __init__(self, name, x, y, width=120, height=60):
        super().__init__(0, 0, width, height)
        self.block_name = name
        self.width = width
        self.height = height
        
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

        # Usar la altura base definida por el bloque, a menos que necesitemos mas espacio para puertos
        calculated_height = max(self.height, num_inputs * 30)
        self.setRect(0, 0, self.width, calculated_height)
        
        # Centrar titulo en el rectangulo
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
        layout.addWidget(QLabel(f"Settings for {self.block_name}"))
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
