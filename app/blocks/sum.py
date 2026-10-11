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

    @staticmethod
    def get_mode1_code(cfg, out_var, target_in_var, k_idx):
        num_inputs = cfg.get('num_inputs', 2)
        if target_in_var:
            # Ambiguous for multiple inputs, assume main path is port 0
            # Note: in_vars is NOT available here yet in the current codegen flow 
            # for mode 1 reverse propagation. We might need to adjust codegen.py
            # But for now let's keep the logic.
            return [f"! SUM mode 1: target_in_var = {out_var} - sum(others)"]
        return []

    @staticmethod
    def get_mode2_code(cfg, in_vars, out_var, k_idx):
        num_inputs = cfg.get('num_inputs', 2)
        active_inputs = [in_vars[i] for i in range(num_inputs) if in_vars.get(i) and in_vars[i] != "0.0"]
        rhs = " + ".join(active_inputs) if active_inputs else "0.0"
        return [f"{out_var} = {rhs}"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode3_code(cfg, in_vars, out_var, k_idx):
        return SumBlock.get_mode2_code(cfg, in_vars, out_var, k_idx)

    @staticmethod
    def get_mode8_code(cfg, j_idx):
        return []
