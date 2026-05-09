from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QVBoxLayout, QCheckBox, QHBoxLayout, QWidget
from .base import BaseBlock

class SignalBlockMixin:
    """Mixin para compartir la logica de señales entre Input y Output"""
    
    def get_signal_types(self, is_input=True):
        # Lista completa segun INPUTS.txt
        all_types = [
            "CON", "ICON", "CHRICN", "MBASE", "ZSORCE", "XTRAN", "GENTAP",
            "STATE", "VAR", "VOLT", "CURNT", "BSFREQ", "ANGLE", "PELEC",
            "QELEC", "ETERM", "EFD", "PMECH", "SPEED", "XADIFD", "ECOMP",
            "VOTHSG", "VUEL", "VOEL", "ISORCE", "TPLOAD", "QPLOAD", "VREF", "SETVAL"
        ]
        return all_types

    def get_category(self, stype):
        # Categorizacion segun INPUTS.txt y requerimientos del usuario
        by_bus_only = ["VOLT", "CURNT", "BSFREQ"]
        by_machine = [
            "MBASE", "ZSORCE", "XTRAN", "GENTAP", "ANGLE", "PELEC", "QELEC",
            "ETERM", "EFD", "PMECH", "SPEED", "XADIFD", "ECOMP", "VOTHSG",
            "VUEL", "VOEL", "ISORCE", "VREF"
        ]
        by_load = ["TPLOAD", "QPLOAD"]
        
        if stype in by_bus_only:
            return "BUS_ONLY"
        elif stype in by_machine or stype in by_load:
            return "MACHINE" # Usamos la misma logica para Load (Bus+ID) por ahora
        else:
            return "INDEX_ONLY"

    def update_signal_title(self, prefix):
        text = f"{prefix}: {self.signal_type}\n"
        cat = self.get_category(self.signal_type)
        
        if self.use_id_mode:
            if cat == "BUS_ONLY":
                text += f"Bus: {self.bus_num}"
            elif cat == "MACHINE":
                text += f"Bus:{self.bus_num} ID:{self.machine_id}"
            else:
                text += f"Idx: {self.index_val}"
        else:
            text += f"Idx: {self.index_val}"
        
        self.title.setPlainText(text)
        self.title.setPos(self.width / 2 - self.title.boundingRect().width() / 2, 
                         self.rect().height() / 2 - self.title.boundingRect().height() / 2)

    def create_signal_fields(self, layout, is_input=True):
        layout.addWidget(QLabel("Signal Source:" if is_input else "Target Variable:"))
        combo = QComboBox()
        combo.addItems(self.get_signal_types(is_input))
        combo.setCurrentText(self.signal_type)
        layout.addWidget(combo)

        id_mode_cb = QCheckBox("Use Machine/Bus ID instead of Index")
        id_mode_cb.setChecked(self.use_id_mode)
        layout.addWidget(id_mode_cb)

        # Contenedor para Indice
        self.idx_widget = QWidget()
        idx_layout = QHBoxLayout(self.idx_widget)
        idx_layout.setContentsMargins(0, 0, 0, 0)
        idx_layout.addWidget(QLabel("Array Index:"))
        idx_edit = QLineEdit(self.index_val)
        idx_layout.addWidget(idx_edit)
        layout.addWidget(self.idx_widget)

        # Contenedor para ID (Maquin/Bus)
        self.id_container = QWidget()
        id_layout = QVBoxLayout(self.id_container)
        id_layout.setContentsMargins(0, 0, 0, 0)
        
        # Fila 1: Machine/Bus Num
        row1_layout = QHBoxLayout()
        self.id_label = QLabel("Machine Num:")
        row1_layout.addWidget(self.id_label)
        id_main_edit = QLineEdit(self.machine_num if self.get_category(self.signal_type) == "MACHINE" else self.bus_num)
        row1_layout.addWidget(id_main_edit)
        id_layout.addLayout(row1_layout)

        # Fila 2: ID
        self.row2_widget = QWidget()
        row2_layout = QHBoxLayout(self.row2_widget)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.addWidget(QLabel("ID:"))
        id_sub_edit = QLineEdit(self.machine_id)
        row2_layout.addWidget(id_sub_edit)
        id_layout.addWidget(self.row2_widget)
        
        layout.addWidget(self.id_container)

        def update_visibility():
            stype = combo.currentText()
            cat = self.get_category(stype)
            is_id = id_mode_cb.isChecked()
            
            # Solo permitir modo ID para categorias que no sean INDEX_ONLY
            if cat == "INDEX_ONLY":
                id_mode_cb.setEnabled(False)
                id_mode_cb.setChecked(False)
                is_id = False
            else:
                id_mode_cb.setEnabled(True)

            self.idx_widget.setVisible(not is_id)
            self.id_container.setVisible(is_id)
            
            if is_id:
                if cat == "BUS_ONLY":
                    self.id_label.setText("Bus Num:")
                    self.row2_widget.setVisible(False)
                elif cat == "MACHINE":
                    self.id_label.setText("Bus Num:" if stype == "ANGLE" or stype in ["GENTAP", "STATE", "VAR"] else "Bus Num:")
                    # En sistemas de potencia, machine index suele ser Bus + ID
                    self.id_label.setText("Bus Num:")
                    self.row2_widget.setVisible(True)

        id_mode_cb.toggled.connect(update_visibility)
        combo.currentTextChanged.connect(update_visibility)
        update_visibility()

        return {
            "type": combo, "id_mode": id_mode_cb, "idx_edit": idx_edit,
            "id_main_edit": id_main_edit, "id_sub_edit": id_sub_edit
        }

class InputBlock(BaseBlock, SignalBlockMixin):
    def __init__(self, x, y):
        super().__init__("INPUT", x, y, width=140, height=60)
        self.signal_type = "CON"
        self.use_id_mode = False
        self.index_val = "1"
        self.machine_num = "1"
        self.machine_id = "1"
        self.bus_num = "1"
        self.disable_windup_config = True
        self.setup_ports(0)
        self.update_title()

    def update_title(self):
        self.update_signal_title("IN")

    def create_config_fields(self, layout):
        return self.create_signal_fields(layout, is_input=True)

    def extract_config_values(self, fields):
        return {
            "type": fields["type"].currentText(),
            "id_mode": fields["id_mode"].isChecked(),
            "index": fields["idx_edit"].text(),
            "id_main": fields["id_main_edit"].text(),
            "id_sub": fields["id_sub_edit"].text()
        }

    def apply_config(self, values):
        super().apply_config(values)
        self.signal_type = values.get("type", "CON")
        self.use_id_mode = values.get("id_mode", False)
        cat = self.get_category(self.signal_type)
        if self.use_id_mode:
            if cat == "BUS_ONLY":
                self.bus_num = values.get("id_main", "1")
            elif cat == "MACHINE":
                self.bus_num = values.get("id_main", "1")
                self.machine_id = values.get("id_sub", "1")
        else:
            self.index_val = values.get("index", "1")
        self.update_title()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            "type": self.signal_type, "id_mode": self.use_id_mode, "index": self.index_val,
            "machine_num": self.machine_num, "machine_id": self.machine_id, "bus_num": self.bus_num
        })
        return cfg

class OutputBlock(BaseBlock, SignalBlockMixin):
    def __init__(self, x, y):
        super().__init__("OUTPUT", x, y, width=140, height=60)
        self.signal_type = "VAR"
        self.use_id_mode = False
        self.index_val = "1"
        self.machine_num = "1"
        self.machine_id = "1"
        self.bus_num = "1"
        self.disable_windup_config = True
        self.setup_ports(1, has_output=False)
        self.update_title()

    def update_title(self):
        self.update_signal_title("OUT")

    def create_config_fields(self, layout):
        return self.create_signal_fields(layout, is_input=False)

    def extract_config_values(self, fields):
        return {
            "type": fields["type"].currentText(),
            "id_mode": fields["id_mode"].isChecked(),
            "index": fields["idx_edit"].text(),
            "id_main": fields["id_main_edit"].text(),
            "id_sub": fields["id_sub_edit"].text()
        }

    def apply_config(self, values):
        super().apply_config(values)
        self.signal_type = values.get("type", "VAR")
        self.use_id_mode = values.get("id_mode", False)
        cat = self.get_category(self.signal_type)
        if self.use_id_mode:
            if cat == "BUS_ONLY":
                self.bus_num = values.get("id_main", "1")
            elif cat == "MACHINE":
                self.bus_num = values.get("id_main", "1")
                self.machine_id = values.get("id_sub", "1")
        else:
            self.index_val = values.get("index", "1")
        self.update_title()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            "type": self.signal_type, "id_mode": self.use_id_mode, "index": self.index_val,
            "machine_num": self.machine_num, "machine_id": self.machine_id, "bus_num": self.bus_num
        })
        return cfg
