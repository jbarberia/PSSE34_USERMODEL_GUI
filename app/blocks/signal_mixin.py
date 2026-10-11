from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QVBoxLayout, QCheckBox, QHBoxLayout, QWidget

class SignalBlockMixin:
    """Mixin para compartir la logica de señales entre Input y Output"""
    
    def get_signal_types(self, is_input=True):
        all_types = [
            "CON", "ICON", "CHRICN", "MBASE", "ZSORCE", "XTRAN", "GENTAP",
            "STATE", "VAR", "VOLT", "CURNT", "BSFREQ", "ANGLE", "PELEC",
            "QELEC", "ETERM", "EFD", "PMECH", "SPEED", "XADIFD", "ECOMP",
            "VOTHSG", "VUEL", "VOEL", "ISORCE", "TPLOAD", "QPLOAD", "VREF", "SETVAL"
        ]
        return all_types

    def get_category(self, stype):
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
            return "MACHINE"
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
        self.center_text()
        self.update_subtitle_pos()

    def create_signal_fields(self, layout, is_input=True):
        layout.addWidget(QLabel("Signal Source:" if is_input else "Target Variable:"))
        combo = QComboBox()
        combo.addItems(self.get_signal_types(is_input))
        combo.setCurrentText(self.signal_type)
        layout.addWidget(combo)

        id_mode_cb = QCheckBox("Use Machine/Bus ID instead of Index")
        id_mode_cb.setChecked(self.use_id_mode)
        layout.addWidget(id_mode_cb)

        self.idx_widget = QWidget()
        idx_layout = QHBoxLayout(self.idx_widget)
        idx_layout.setContentsMargins(0, 0, 0, 0)
        idx_layout.addWidget(QLabel("Array Index:"))
        idx_edit = QLineEdit(self.index_val)
        idx_layout.addWidget(idx_edit)
        layout.addWidget(self.idx_widget)

        self.id_container = QWidget()
        id_layout = QVBoxLayout(self.id_container)
        id_layout.setContentsMargins(0, 0, 0, 0)
        
        row1_layout = QHBoxLayout()
        self.gui_id_label = QLabel("Machine Num:")
        row1_layout.addWidget(self.gui_id_label)
        id_main_edit = QLineEdit(self.machine_num if self.get_category(self.signal_type) == "MACHINE" else self.bus_num)
        row1_layout.addWidget(id_main_edit)
        id_layout.addLayout(row1_layout)

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
                    self.gui_id_label.setText("Bus Num:")
                    self.row2_widget.setVisible(False)
                elif cat == "MACHINE":
                    self.gui_id_label.setText("Bus Num:")
                    self.row2_widget.setVisible(True)

        id_mode_cb.toggled.connect(update_visibility)
        combo.currentTextChanged.connect(update_visibility)
        update_visibility()

        return {
            "type": combo, "id_mode": id_mode_cb, "idx_edit": idx_edit,
            "id_main_edit": id_main_edit, "id_sub_edit": id_sub_edit
        }
