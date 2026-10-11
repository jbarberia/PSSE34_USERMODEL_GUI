from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class PIDBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("PID", x, y, width=240, height=80, block_id=block_id)
        self.kp = "1.0"
        self.ki = "1.0"
        self.kd = "1.0"
        self.td = "0.1"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("           Ki      sKd\n Kp + --- + --------\n           s     1 + sTd")
        self.set_subtitle_text(f"PID: KP={self.kp} KI={self.ki} KD={self.kd} TD={self.td}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KP:"))
        kp_edit = QLineEdit(self.kp)
        layout.addWidget(kp_edit)
        layout.addWidget(QLabel("KI:"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        layout.addWidget(QLabel("KD:"))
        kd_edit = QLineEdit(self.kd)
        layout.addWidget(kd_edit)
        layout.addWidget(QLabel("TD (Filter s):"))
        td_edit = QLineEdit(self.td)
        layout.addWidget(td_edit)
        return {"kp": kp_edit, "ki": ki_edit, "kd": kd_edit, "td": td_edit}

    def extract_block_specific_values(self, fields):
        return {
            "kp": fields["kp"].text(),
            "ki": fields["ki"].text(),
            "kd": fields["kd"].text(),
            "td": fields["td"].text()
        }

    def apply_config(self, values):
        super().apply_config(values)
        self.kp = values.get("kp", self.kp)
        self.ki = values.get("ki", self.ki)
        self.kd = values.get("kd", self.kd)
        self.td = values.get("td", self.td)
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"kp": self.kp, "ki": self.ki, "kd": self.kd, "td": self.td})
        return cfg

    @staticmethod
    def get_mode1_code(cfg, out_var, target_in_var, k_idx):
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        kd = cfg.get('kd', '1.0')
        td = cfg.get('td', '0.1')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if target_in_var:
            if prefix == "NW":
                l_min = cfg.get('limit_min', '-999.0')
                l_max = cfg.get('limit_max', '999.0')
                return [f"{target_in_var} = {prefix}PID_MODE1({kp}, {ki}, {kd}, {td}, {l_max}, {l_min}, {out_var}, {k_idx}, IERR)"]
            else:
                return [f"{target_in_var} = PID_MODE1({kp}, {ki}, {kd}, {td}, {out_var}, {k_idx}, IERR)"]
        return []

    @staticmethod
    def get_mode2_code(cfg, in_vars, out_var, k_idx):
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        kd = cfg.get('kd', '1.0')
        td = cfg.get('td', '0.1')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if prefix == "NW":
            l_min = cfg.get('limit_min', '-999.0')
            l_max = cfg.get('limit_max', '999.0')
            return [f"{out_var} = {prefix}PID_MODE2({kp}, {ki}, {kd}, {td}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = PID_MODE2({kp}, {ki}, {kd}, {td}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode3_code(cfg, in_vars, out_var, k_idx):
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        kd = cfg.get('kd', '1.0')
        td = cfg.get('td', '0.1')
        prefix = "NW" if cfg.get("limit_enabled") and cfg.get("limit_type") == "Non-Windup" else ""
        if prefix == "NW":
            l_min = cfg.get('limit_min', '-999.0')
            l_max = cfg.get('limit_max', '999.0')
            return [f"{out_var} = {prefix}PID_MODE3({kp}, {ki}, {kd}, {td}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})"]
        else:
            return [f"{out_var} = PID_MODE3({kp}, {ki}, {kd}, {td}, {in_vars[0]}, {k_idx})"] + BaseBlock.get_limits_code(cfg, out_var)

    @staticmethod
    def get_mode8_code(cfg, j_idx):
        return [
            f"CON_DSCRPT(J+{j_idx}) = '{cfg.get('block_id')} KP'",
            f"CON_DSCRPT(J+{j_idx+1}) = '{cfg.get('block_id')} KI'",
            f"CON_DSCRPT(J+{j_idx+2}) = '{cfg.get('block_id')} KD'",
            f"CON_DSCRPT(J+{j_idx+3}) = '{cfg.get('block_id')} TD'"
        ]
