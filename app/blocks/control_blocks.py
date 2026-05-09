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
    
    def create_fortran_code_mode_3(self):
        return f"VOUT_{self.block_id} = INT_MODE2({self.ti}, VINP_{self.block_id}, 1.0)"

class FirstOrderLagBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("LAG 1", x, y, width=120, height=60, block_id=block_id)
        self.ki = "1.0"
        self.ti = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("   Ki\n--------\n 1 + sTi")
        self.set_subtitle_text(f"LAG 1: KI={self.ki} TI={self.ti}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KI (Gain):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        layout.addWidget(QLabel("TI (s):"))
        ti_edit = QLineEdit(self.ti)
        layout.addWidget(ti_edit)
        return {"ki": ki_edit, "ti": ti_edit}

    def extract_block_specific_values(self, fields):
        return {"ki": fields["ki"].text(), "ti": fields["ti"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ki = values.get("ki", self.ki)
        self.ti = values.get("ti", self.ti)
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ki": self.ki, "ti": self.ti})
        return cfg

class WashoutBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("WASHOUT", x, y, width=140, height=60, block_id=block_id)
        self.ki = "1.0"
        self.ti = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("  Ki * sTi\n----------\n 1 + sTi")
        self.set_subtitle_text(f"WASHOUT: KI={self.ki} TI={self.ti}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KI (Gain):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        layout.addWidget(QLabel("TI (s):"))
        ti_edit = QLineEdit(self.ti)
        layout.addWidget(ti_edit)
        return {"ki": ki_edit, "ti": ti_edit}

    def extract_block_specific_values(self, fields):
        return {"ki": fields["ki"].text(), "ti": fields["ti"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ki = values.get("ki", self.ki)
        self.ti = values.get("ti", self.ti)
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ki": self.ki, "ti": self.ti})
        return cfg

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
