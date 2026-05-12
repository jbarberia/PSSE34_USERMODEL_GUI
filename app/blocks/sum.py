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
    def get_fortran_code(cfg, mode, in_vars, out_var, k_idx, target_in_var=None):
        num_inputs = cfg.get('num_inputs', 2)
        code_lines = []
        if mode == 1:
            if target_in_var:
                # Ambiguous for multiple inputs, assume main path is port 0
                active_others = [in_vars[i] for i in range(1, num_inputs) if in_vars[i] != "0.0"]
                rhs_others = " + ".join(active_others) if active_others else "0.0"
                code_lines.append(f"{target_in_var} = {out_var} - ({rhs_others})")
        elif mode in [2, 3]:
            active_inputs = [in_vars[i] for i in range(num_inputs) if in_vars[i] != "0.0"]
            rhs = " + ".join(active_inputs) if active_inputs else "0.0"
            code_lines.append(f"{out_var} = {rhs}")
        
        code_lines.extend(BaseBlock.get_fortran_code(cfg, mode, in_vars, out_var, k_idx, target_in_var))
        return code_lines
