from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class IntegratorBlock(BaseBlock):
    def __init__(self, x, y):
        super().__init__("INTEGRATOR", x, y, width=140, height=60)
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

    def get_config(self):
        return {"initial_condition": self.initial_condition}
