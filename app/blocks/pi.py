from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class PIBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("PI", x, y, width=120, height=60, block_id=block_id)
        self.kp = "1.0"
        self.ki = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("      Ki\n Kp + ----\n       s")
        self.set_subtitle_text(f"PI: KP={self.kp} KI={self.ki}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KP (Prop):"))
        kp_edit = QLineEdit(self.kp)
        layout.addWidget(kp_edit)
        layout.addWidget(QLabel("KI (Integ):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        return {"kp": kp_edit, "ki": ki_edit}

    def extract_block_specific_values(self, fields):
        return {"kp": fields["kp"].text(), "ki": fields["ki"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.kp = values.get("kp", self.kp)
        self.ki = values.get("ki", self.ki)
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"kp": self.kp, "ki": self.ki})
        return cfg

    @staticmethod
    def get_mode1_code(cfg, out_var, target_in_var, k_idx):
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        l_min = cfg.get('limit_min', '-999.0') if cfg.get('limit_enabled') else '-999.0'
        l_max = cfg.get('limit_max', '999.0') if cfg.get('limit_enabled') else '999.0'
        if target_in_var:
            if prefix == "NW":
                return [f"{target_in_var} = {prefix}PI_MODE1({kp}, {ki}, {l_max}, {l_min}, {out_var}, {k_idx}, IERR)"]
            else:
                # PSS/E doesnt have a simple PI_MODE1 without limits usually, 
                # but let's assume if they dont want Non-Windup they want standard windup
                return [f"{target_in_var} = PI_MODE1({kp}, {ki}, {out_var}, {k_idx}, IERR)"]
        return []

    @staticmethod
    def get_mode2_code(cfg, in_vars, out_var, k_idx):
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        l_min = cfg.get('limit_min', '-999.0') if cfg.get('limit_enabled') else '-999.0'
        l_max = cfg.get('limit_max', '999.0') if cfg.get('limit_enabled') else '999.0'
        if prefix == "NW":
            return [f"{out_var} = {prefix}PI_MODE2({kp}, {ki}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = PI_MODE2({kp}, {ki}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode3_code(cfg, in_vars, out_var, k_idx):
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        l_min = cfg.get('limit_min', '-999.0') if cfg.get('limit_enabled') else '-999.0'
        l_max = cfg.get('limit_max', '999.0') if cfg.get('limit_enabled') else '999.0'
        if prefix == "NW":
            return [f"{out_var} = {prefix}PI_MODE3({kp}, {ki}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = PI_MODE3({kp}, {ki}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode8_code(cfg, j_idx):
        return [
            f"CON_DSCRPT(J+{j_idx}) = '{cfg.get('block_id')} KP'",
            f"CON_DSCRPT(J+{j_idx+1}) = '{cfg.get('block_id')} KI'"
        ]
