from PyQt5.QtWidgets import QLabel, QSpinBox
from .base import BaseBlock

class SumBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("SUM", x, y, width=60, height=60, block_id=block_id)
        self.num_inputs = 2
        self.setup_ports(self.num_inputs)

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("Number of Inputs:"))
        spin = QSpinBox()
        spin.setRange(1, 10)
        spin.setValue(self.num_inputs)
        layout.addWidget(spin)
        return {"num_inputs": spin}

    def extract_block_specific_values(self, fields):
        return {"num_inputs": fields["num_inputs"].value()}

    def apply_config(self, values):
        super().apply_config(values)
        self.num_inputs = values.get("num_inputs", self.num_inputs)
        self.setup_ports(self.num_inputs)

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"num_inputs": self.num_inputs})
        return cfg
