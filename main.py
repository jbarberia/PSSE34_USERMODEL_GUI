import sys
import json
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QMainWindow,
    QMessageBox,
    QFileDialog,
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QFormLayout,
    QPushButton,
    QScrollArea,
    QFrame,
)
from PyQt5.QtCore import Qt
from app.view import GraphicsView
from app.blocks import (
    GainBlock,
    IntegratorBlock,
    SumBlock,
    BaseBlock,
    FirstOrderLagBlock,
    WashoutBlock,
    LeadLagBlock,
    PIBlock,
    PIDBlock,
    InputBlock,
    OutputBlock,
)
from app.core import Connection
from app.codegen import generate_code


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Block Editor")
        self.resize(1300, 800)

        self.model_name = "USUARIO"
        self.current_selected_block = None

        # Contador para IDs automáticos
        self.block_counts = {}

        self.scene = QGraphicsScene()
        self.view = GraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.view.selectionChangedSignal.connect(self.on_selection_changed)

        self.block_factory = {
            "GAIN": GainBlock,
            "INTEGRATOR": IntegratorBlock,
            "SUM": SumBlock,
            "LAG 1": FirstOrderLagBlock,
            "WASHOUT": WashoutBlock,
            "LEAD LAG": LeadLagBlock,
            "PI": PIBlock,
            "PID": PIDBlock,
            "INPUT": InputBlock,
            "OUTPUT": OutputBlock,
        }

        self.init_menu()
        self.init_properties_panel()

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&Save").triggered.connect(self.on_save)
        file_menu.addAction("&Open").triggered.connect(self.on_open)
        file_menu.addAction("&Generate Code").triggered.connect(self.on_generate_code)

        block_menu = menubar.addMenu("&Blocks")
        signal_menu = block_menu.addMenu("Signals")
        signal_menu.addAction("Add INPUT").triggered.connect(lambda: self.add_new_block("INPUT"))
        signal_menu.addAction("Add OUTPUT").triggered.connect(lambda: self.add_new_block("OUTPUT"))
        block_menu.addSeparator()
        block_menu.addAction("Add GAIN").triggered.connect(lambda: self.add_new_block("GAIN"))
        block_menu.addAction("Add SUM").triggered.connect(lambda: self.add_new_block("SUM"))
        control_menu = block_menu.addMenu("Control")
        control_menu.addAction("Add INTEGRATOR").triggered.connect(lambda: self.add_new_block("INTEGRATOR"))
        control_menu.addAction("Add LAG 1").triggered.connect(lambda: self.add_new_block("LAG 1"))
        control_menu.addAction("Add WASHOUT").triggered.connect(lambda: self.add_new_block("WASHOUT"))
        control_menu.addAction("Add LEAD LAG").triggered.connect(lambda: self.add_new_block("LEAD LAG"))
        control_menu.addAction("Add PI").triggered.connect(lambda: self.add_new_block("PI"))
        control_menu.addAction("Add PID").triggered.connect(lambda: self.add_new_block("PID"))

    def init_properties_panel(self):
        self.dock = QDockWidget("Properties", self)
        self.dock.setAllowedAreas(Qt.RightDockWidgetArea)

        main_container = QWidget()
        self.main_layout = QVBoxLayout(main_container)

        # --- GLOBAL SECTION ---
        global_group = QWidget()
        global_layout = QVBoxLayout(global_group)
        global_layout.addWidget(QLabel("<b>Global Settings</b>"))
        form = QFormLayout()
        self.subroutine_edit = QLineEdit(self.model_name)
        self.subroutine_edit.textChanged.connect(self.on_model_name_changed)
        form.addRow("Subroutine Name:", self.subroutine_edit)
        global_layout.addLayout(form)
        self.main_layout.addWidget(global_group)

        self.main_layout.addWidget(QFrame(frameShape=QFrame.HLine, frameShadow=QFrame.Sunken))

        # --- BLOCK SECTION ---
        self.block_group = QWidget()
        self.block_layout = QVBoxLayout(self.block_group)
        self.main_layout.addWidget(self.block_group)
        self.block_group.hide()

        self.main_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(main_container)
        self.dock.setWidget(scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def on_model_name_changed(self, text):
        self.model_name = text.strip() or "USUARIO"

    def on_selection_changed(self):
        try:
            selected = self.scene.selectedItems()
            if len(selected) == 1 and isinstance(selected[0], BaseBlock):
                self.show_block_properties(selected[0])
            else:
                self.block_group.hide()
                self.current_selected_block = None
        except RuntimeError:
            pass

    def show_block_properties(self, block):
        while self.block_layout.count():
            item = self.block_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.current_selected_block = block
        layout = self.block_layout
        layout.addWidget(QLabel(f"<b>Block: {block.block_name}</b>"))

        # Usar la misma función que el diálogo
        self.current_prop_fields = block.build_config_ui(layout)

        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_block_properties)
        layout.addWidget(apply_btn)
        self.block_group.show()

    def apply_block_properties(self):
        if self.current_selected_block:
            values = self.current_selected_block.extract_config_values(self.current_prop_fields)
            self.current_selected_block.apply_config(values)
            self.scene.update()

    def add_new_block(self, b_type, x=50, y=50, block_id=None):
        if not block_id:
            count = self.block_counts.get(b_type, 0) + 1
            self.block_counts[b_type] = count
            # Limpiar nombre para ID (quitar espacios)
            clean_type = b_type.replace(" ", "")
            block_id = f"{clean_type}{count}"

        block_class = self.block_factory.get(b_type)
        if block_class:
            block = block_class(x, y, block_id=block_id)
            self.scene.addItem(block)
            return block
        return None

    def serialize_diagram(self):
        blocks_data = []
        connections_data = []
        block_to_id = {}
        items = self.scene.items()
        for item in items:
            if isinstance(item, BaseBlock):
                # Usar el ID gráfico en lugar de la memoria para persistencia
                block_to_id[item] = item.block_id
                blocks_data.append(
                    {"item": item, "id": item.block_id, "type": item.block_name, "x": item.x(), "y": item.y(), "config": item.get_config()}
                )
        for item in items:
            if isinstance(item, Connection) and item.port1 and item.port2:
                from_b, to_b = item.port1.parentItem(), item.port2.parentItem()
                if from_b in block_to_id and to_b in block_to_id:
                    port_index = to_b.input_ports.index(item.port2)
                    connections_data.append({"from_block": block_to_id[from_b], "to_block": block_to_id[to_b], "to_port_index": port_index})
        return {"model_name": self.model_name, "blocks": blocks_data, "connections": connections_data}

    def on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Diagram", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.serialize_diagram(), f, indent=4)

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Diagram", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.scene.clear()
            self.block_counts = {}
            self.model_name = data.get("model_name", "USUARIO")
            self.subroutine_edit.setText(self.model_name)

            id_to_block = {}
            for b_data in data["blocks"]:
                block = self.add_new_block(b_data["type"], b_data["x"], b_data["y"], block_id=b_data["id"])
                if block:
                    block.apply_config(b_data["config"])
                    id_to_block[b_data["id"]] = block
            for c_data in data["connections"]:
                from_b, to_b = id_to_block.get(c_data["from_block"]), id_to_block.get(c_data["to_block"])
                if from_b and to_b:
                    self.scene.addItem(Connection(from_b.output_port, to_b.input_ports[c_data["to_port_index"]]))

    def on_generate_code(self):
        generate_code(self.serialize_diagram())
        QMessageBox.information(self, "Success", f"Code generated as subroutine '{self.model_name}.f90'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
