from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class LeadLagBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("LEAD LAG", x, y, width=180, height=70, block_id=block_id)
        self.ki = "1.0"
        self.t1 = "1.0"
        self.t2 = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText(" Ki * (1 + sT1)\n--------------\n   (1 + sT2)")
        self.set_subtitle_text(f"LEAD LAG: KI={self.ki} T1={self.t1} T2={self.t2}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KI (Gain):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        layout.addWidget(QLabel("T1 (s):"))
        t1_edit = QLineEdit(self.t1)
        layout.addWidget(t1_edit)
        layout.addWidget(QLabel("T2 (s):"))
        t2_edit = QLineEdit(self.t2)
        layout.addWidget(t2_edit)
        return {"ki": ki_edit, "t1": t1_edit, "t2": t2_edit}

    def extract_block_specific_values(self, fields):
        return {"ki": fields["ki"].text(), "t1": fields["t1"].text(), "t2": fields["t2"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ki = values.get("ki", self.ki)
        self.t1 = values.get("t1", self.t1)
        self.t2 = values.get("t2", self.t2)
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ki": self.ki, "t1": self.t1, "t2": self.t2})
        return cfg

    @staticmethod
    def get_mode1_code(cfg, out_var, target_in_var, k_idx):
        ki = cfg.get('ki', '1.0')
        t1 = cfg.get('t1', '1.0')
        t2 = cfg.get('t2', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if target_in_var:
            if prefix == "NW":
                l_min = cfg.get('limit_min', '-999.0')
                l_max = cfg.get('limit_max', '999.0')
                return [f"{target_in_var} = {prefix}LEADLAG_MODE1({ki}, {t1}, {t2}, {l_max}, {l_min}, {out_var}, {k_idx}, IERR)"]
            else:
                return [f"{target_in_var} = LEADLAG_MODE1({ki}, {t1}, {t2}, {out_var}, {k_idx}, IERR)"]
        return []

    @staticmethod
    def get_mode2_code(cfg, in_vars, out_var, k_idx):
        ki = cfg.get('ki', '1.0')
        t1 = cfg.get('t1', '1.0')
        t2 = cfg.get('t2', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if prefix == "NW":
            l_min = cfg.get('limit_min', '-999.0')
            l_max = cfg.get('limit_max', '999.0')
            return [f"{out_var} = {prefix}LEADLAG_MODE2({ki}, {t1}, {t2}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = LEADLAG_MODE2({ki}, {t1}, {t2}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode3_code(cfg, in_vars, out_var, k_idx):
        ki = cfg.get('ki', '1.0')
        t1 = cfg.get('t1', '1.0')
        t2 = cfg.get('t2', '1.0')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if prefix == "NW":
            l_min = cfg.get('limit_min', '-999.0')
            l_max = cfg.get('limit_max', '999.0')
            return [f"{out_var} = {prefix}LEADLAG_MODE3({ki}, {t1}, {t2}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = LEADLAG_MODE3({ki}, {t1}, {t2}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode8_code(cfg, j_idx):
        return [
            f"CON_DSCRPT(J+{j_idx}) = '{cfg.get('block_id')} KI'",
            f"CON_DSCRPT(J+{j_idx+1}) = '{cfg.get('block_id')} T1'",
            f"CON_DSCRPT(J+{j_idx+2}) = '{cfg.get('block_id')} T2'"
        ]
