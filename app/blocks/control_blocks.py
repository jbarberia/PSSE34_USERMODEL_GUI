from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class IntegratorBlock(BaseBlock):
    def __init__(self, x, y):
        # Integrador simple, 100 es suficiente
        super().__init__("INTEGRATOR", x, y, width=50, height=60)
        self.ti = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("  1\n----\n sTi")
        self.set_subtitle_text(f"TI={self.ti}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("TI (s):"))
        ti_edit = QLineEdit(self.ti)
        layout.addWidget(ti_edit)
        return {"ti": ti_edit}

    def extract_config_values(self, fields):
        return {"ti": fields["ti"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ti = values.get("ti", "1.0")
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ti": self.ti})
        return cfg

class FirstOrderLagBlock(BaseBlock):
    def __init__(self, x, y):
        super().__init__("LAG 1", x, y, width=80, height=60)
        self.ki = "1.0"
        self.ti = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("   Ki\n--------\n 1 + sTi")
        self.set_subtitle_text(f"KI={self.ki}\nTI={self.ti}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KI (Gain):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        layout.addWidget(QLabel("TI (s):"))
        ti_edit = QLineEdit(self.ti)
        layout.addWidget(ti_edit)
        return {"ki": ki_edit, "ti": ti_edit}

    def extract_config_values(self, fields):
        return {"ki": fields["ki"].text(), "ti": fields["ti"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ki = values.get("ki", "1.0")
        self.ti = values.get("ti", "1.0")
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ki": self.ki, "ti": self.ti})
        return cfg

class WashoutBlock(BaseBlock):
    def __init__(self, x, y):
        # Washout: requiere unos 140 para la multiplicacion superior
        super().__init__("WASHOUT", x, y, width=100, height=60)
        self.ki = "1.0"
        self.ti = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText(" KI x sTI\n----------\n 1 + sTI")
        self.set_subtitle_text(f"KI={self.ki}\nTI={self.ti}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KI (Gain):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        layout.addWidget(QLabel("TI (s):"))
        ti_edit = QLineEdit(self.ti)
        layout.addWidget(ti_edit)
        return {"ki": ki_edit, "ti": ti_edit}

    def extract_config_values(self, fields):
        return {"ki": fields["ki"].text(), "ti": fields["ti"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ki = values.get("ki", "1.0")
        self.ti = values.get("ti", "1.0")
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ki": self.ki, "ti": self.ti})
        return cfg

class LeadLagBlock(BaseBlock):
    def __init__(self, x, y):
        # Lead Lag: ecuacion mas larga, 180 es ideal
        super().__init__("LEAD LAG", x, y, width=130, height=60)
        self.ki = "1.0"
        self.t1 = "1.0"
        self.t2 = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText(" KI x (1 + sT1)\n--------------\n   (1 + sT2)")
        self.set_subtitle_text(f"KI={self.ki}\nT1={self.t1}\nT2={self.t2}")

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

    def extract_config_values(self, fields):
        return {"ki": fields["ki"].text(), "t1": fields["t1"].text(), "t2": fields["t2"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.ki = values.get("ki", "1.0")
        self.t1 = values.get("t1", "1.0")
        self.t2 = values.get("t2", "1.0")
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"ki": self.ki, "t1": self.t1, "t2": self.t2})
        return cfg

class PIBlock(BaseBlock):
    def __init__(self, x, y):
        # PI: 120 es suficiente para Kp + Ki/s
        super().__init__("PI", x, y, width=80, height=60)
        self.kp = "1.0"
        self.ki = "1.0"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("      Ki\n Kp + ----\n       s")
        self.set_subtitle_text(f"KP={self.kp}\nKI={self.ki}")

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("KP (Prop):"))
        kp_edit = QLineEdit(self.kp)
        layout.addWidget(kp_edit)
        layout.addWidget(QLabel("KI (Integ):"))
        ki_edit = QLineEdit(self.ki)
        layout.addWidget(ki_edit)
        return {"kp": kp_edit, "ki": ki_edit}

    def extract_config_values(self, fields):
        return {"kp": fields["kp"].text(), "ki": fields["ki"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.kp = values.get("kp", "1.0")
        self.ki = values.get("ki", "1.0")
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"kp": self.kp, "ki": self.ki})
        return cfg

class PIDBlock(BaseBlock):
    def __init__(self, x, y):
        # PID: requiere mucho espacio (240) para la ecuacion extendida de filtrado
        super().__init__("PID", x, y, width=180, height=60)
        self.kp = "1.0"
        self.ki = "1.0"
        self.kd = "1.0"
        self.td = "0.1"
        self.setup_ports(1)
        self.refresh_ui()

    def refresh_ui(self):
        self.title.setPlainText("       Ki      sKd  \n" \
                                " Kp + --- + --------\n" \
                                "       s     1 + sTd")
        self.set_subtitle_text(f"KP={self.kp}\tKI={self.ki}\nKD={self.kd}\tTD={self.td}")

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

    def extract_config_values(self, fields):
        return {
            "kp": fields["kp"].text(),
            "ki": fields["ki"].text(),
            "kd": fields["kd"].text(),
            "td": fields["td"].text()
        }

    def apply_config(self, values):
        super().apply_config(values)
        self.kp = values.get("kp", "1.0")
        self.ki = values.get("ki", "1.0")
        self.kd = values.get("kd", "1.0")
        self.td = values.get("td", "0.1")
        self.refresh_ui()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"kp": self.kp, "ki": self.ki, "kd": self.kd, "td": self.td})
        return cfg
