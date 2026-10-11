from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class IntegratorBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("INTEGRATOR", x, y, width=100, height=60, block_id=block_id)
        self.ti = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("  1\n----\n sTi")
        self.set_subtitle_text(f"INTEGRATOR: TI={self.ti}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("TI (s):"))
        ti_edit = QLineEdit(self.ti)
        layout.addWidget(ti_edit)
        return {"ti": ti_edit}

    def extract_block_specific_values(self, fields):
        return {"ti": fields["ti"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ti = values.get("ti", self.ti)
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ti": self.ti})
        return cfg
    
    @staticmethod
    def get_mode1_code(cfg, out_var, target_in_var, k_idx):
        ti = cfg.get('ti', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if target_in_var:
            if prefix == "NW":
                l_min = cfg.get('limit_min', '-999.0')
                l_max = cfg.get('limit_max', '999.0')
                return [f"{target_in_var} = {prefix}INT_MODE1({ti}, {l_max}, {l_min}, {out_var}, {k_idx})"]
            else:
                return [f"{target_in_var} = {prefix}INT_MODE1({ti}, {out_var}, {k_idx})"]
        return []

    @staticmethod
    def get_mode2_code(cfg, in_vars, out_var, k_idx):
        ti = cfg.get('ti', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if prefix == "NW":
            l_min = cfg.get('limit_min', '-999.0')
            l_max = cfg.get('limit_max', '999.0')
            return [f"{out_var} = {prefix}INT_MODE2({ti}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = {prefix}INT_MODE2({ti}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode3_code(cfg, in_vars, out_var, k_idx):
        ti = cfg.get('ti', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if prefix == "NW":
            l_min = cfg.get('limit_min', '-999.0')
            l_max = cfg.get('limit_max', '999.0')
            return [f"{out_var} = {prefix}INT_MODE3({ti}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = {prefix}INT_MODE3({ti}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode8_code(cfg, j_idx):
        return [f"CON_DSCRPT(J+{j_idx}) = '{cfg.get('block_id')} TI'"]
