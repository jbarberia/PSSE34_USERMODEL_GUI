# allocation_table.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QLabel, 
    QLineEdit, QComboBox, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt


class AllocationTableWidget(QWidget):
    def __init__(self, on_change_callback=None, parent=None):
        super().__init__(parent)
        self.on_change_callback = on_change_callback

        layout = QVBoxLayout(self)

        # Barra para agregar variables de forma manual (opcional)
        form_group = QGroupBox("Asignación Manual de Variables")
        form_layout = QHBoxLayout(form_group)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["CON", "ICON", "STATE", "VAR"])

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre (ej. TR, KA)")

        self.val_input = QLineEdit()
        self.val_input.setPlaceholderText("Valor por defecto")

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descripción / Unidades")

        self.btn_add = QPushButton("Agregar Variable")
        self.btn_add.clicked.connect(self._add_from_inputs)

        form_layout.addWidget(QLabel("Tipo:"))
        form_layout.addWidget(self.type_combo)
        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Valor:"))
        form_layout.addWidget(self.val_input)
        form_layout.addWidget(QLabel("Desc:"))
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.btn_add)

        layout.addWidget(form_group)

        # Tabla Principal
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Offset PSS/E", "Tipo", "Nombre", "Valor Defecto", "Descripción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.table.cellChanged.connect(self._notify_change)
        layout.addWidget(self.table)

        # Botón para borrar
        del_layout = QHBoxLayout()
        self.btn_delete = QPushButton("Eliminar Fila Seleccionada")
        self.btn_delete.clicked.connect(self.delete_selected)
        del_layout.addStretch()
        del_layout.addWidget(self.btn_delete)
        layout.addLayout(del_layout)

    def _add_from_inputs(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Atención", "Debe ingresar un nombre.")
            return
        self.add_entry(
            self.type_combo.currentText(),
            name,
            self.val_input.text().strip() or "0.0",
            self.desc_input.text().strip()
        )
        self.name_input.clear()
        self.val_input.clear()
        self.desc_input.clear()

    def add_entry(self, var_type, name, val, desc):
        """Agrega una fila individual y recalcula offsets."""
        row = self.table.rowCount()
        self.table.blockSignals(True)
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem(var_type))
        self.table.setItem(row, 2, QTableWidgetItem(name))
        self.table.setItem(row, 3, QTableWidgetItem(str(val)))
        self.table.setItem(row, 4, QTableWidgetItem(desc))

        self.table.item(row, 0).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table.item(row, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table.blockSignals(False)

        self.recalculate_offsets()

    def set_data(self, data_list):
        """
        Carga datos masivos desde la app.
        data_list = [{'type': 'CON', 'name': 'TR', 'val': 0.02, 'desc': 'Sensing time'}, ...]
        """
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.blockSignals(False)

        for item in data_list:
            self.add_entry(item['type'], item['name'], item.get('val', '0.0'), item.get('desc', ''))

    def recalculate_offsets(self):
        """Calcula dinámicamente J+0, M+0, K+0, L+0 según las normas PSS/E"""
        self.table.blockSignals(True)
        counts = {"CON": 0, "ICON": 0, "STATE": 0, "VAR": 0}
        bases = {"CON": "J", "ICON": "M", "STATE": "K", "VAR": "L"}

        for row in range(self.table.rowCount()):
            t = self.table.item(row, 1).text()
            idx = counts.get(t, 0)
            base = bases.get(t, "X")
            self.table.item(row, 0).setText(f"{base} + {idx}")
            counts[t] += 1

        self.table.blockSignals(False)
        self._notify_change()

    def delete_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self.recalculate_offsets()

    def _notify_change(self):
        if self.on_change_callback:
            self.on_change_callback()

    def get_data(self):
        """Devuelve una lista con todas las asignaciones formateadas"""
        data = []
        for r in range(self.table.rowCount()):
            data.append({
                "offset": self.table.item(r, 0).text(),
                "type": self.table.item(r, 1).text(),
                "name": self.table.item(r, 2).text(),
                "val": self.table.item(r, 3).text(),
                "desc": self.table.item(r, 4).text()
            })
        return data
