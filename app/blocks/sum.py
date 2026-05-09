from PyQt5.QtWidgets import QLabel, QSpinBox
from .base import BaseBlock

class SumBlock(BaseBlock):
    def __init__(self, x, y):
        # El sumador puede ser mas pequeño si tiene pocas entradas
        super().__init__("SUM", x, y, width=60, height=60)
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
