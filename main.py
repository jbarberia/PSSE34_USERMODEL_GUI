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
from app.views.view import GraphicsView
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
from app.models.core import Connection
from app.controllers.diagram_controller import DiagramController
from app.codegen import generate_code

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = DiagramController()
        self.setWindowTitle("Control Block Editor")
        self.resize(1300, 800)

        self.model_name = self.controller.model.model_name
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
        self.controller.set_model_name(self.model_name)

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
            new_id = values.get('block_id')
            old_id = self.current_selected_block.block_id
            
            # Check for ID collision if ID is changing
            if new_id != old_id and not self.controller.is_id_available(new_id):
                QMessageBox.warning(self, "ID Collision", f"The ID '{new_id}' is already in use. Please choose a unique ID.")
                return

            # If ID changed, we need to update the model reference
            if new_id != old_id:
                self.controller.remove_block(old_id)
                self.current_selected_block.apply_config(values)
                self.controller.add_block(self.current_selected_block.block_name, 
                                          self.current_selected_block.x(), 
                                          self.current_selected_block.y(), 
                                          block_id=new_id)
            else:
                self.current_selected_block.apply_config(values)
            
            self.controller.update_block_config(self.current_selected_block.block_id, self.current_selected_block.get_config())
            self.scene.update()

    def add_new_block(self, b_type, x=50, y=50, block_id=None, config=None):
        if not block_id:
            count = self.block_counts.get(b_type, 0) + 1
            clean_type = b_type.replace(" ", "")
            block_id = f"{clean_type}{count}"
            
            # Ensure generated ID is truly unique
            while not self.controller.is_id_available(block_id):
                count += 1
                block_id = f"{clean_type}{count}"
            
            self.block_counts[b_type] = count

        block_class = self.block_factory.get(b_type)
        if block_class:
            block = block_class(x, y, block_id=block_id)
            if config:
                block.apply_config(config)
            
            self.scene.addItem(block)
            
            # Sync with controller
            self.controller.add_block(b_type, x, y, block_id=block_id)
            if config:
                self.controller.update_block_config(block_id, config)
            
            return block
        return None

    def on_save(self):
        # Ensure model is up to date before saving
        self.sync_model_from_scene()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Diagram", "", "JSON Files (*.json)")
        if file_path:
            self.controller.save_to_file(file_path)

    def sync_model_from_scene(self):
        """
        Final sync before save/codegen to ensure all positions and connections are captured.
        """
        self.controller.clear()
        self.controller.set_model_name(self.model_name)
        
        items = self.scene.items()
        blocks = [item for item in items if isinstance(item, BaseBlock)]
        
        for b in blocks:
            self.controller.add_block(b.block_name, b.x(), b.y(), block_id=b.block_id)
            self.controller.update_block_config(b.block_id, b.get_config())
            
        for item in items:
            if isinstance(item, Connection) and item.port1 and item.port2:
                from_b, to_b = item.port1.parentItem(), item.port2.parentItem()
                if isinstance(from_b, BaseBlock) and isinstance(to_b, BaseBlock):
                    port_index = to_b.input_ports.index(item.port2)
                    self.controller.add_connection(from_b.block_id, to_b.block_id, port_index)

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Diagram", "", "JSON Files (*.json)")
        if file_path:
            model = self.controller.load_from_file(file_path)
            self.scene.clear()
            self.block_counts = {}
            self.model_name = model.model_name
            self.subroutine_edit.setText(self.model_name)

            id_to_block = {}
            # Rebuild blocks
            for b_id, b_model in model.blocks.items():
                # Correct block factory lookup using b_model.type which is b_type
                block = self.add_new_block(b_model.type, b_model.x, b_model.y, block_id=b_model.block_id, config=b_model.config)
                if block:
                    id_to_block[b_id] = block
            
            # Rebuild connections
            for c_model in model.connections:
                from_b = id_to_block.get(c_model.from_block)
                to_b = id_to_block.get(c_model.to_block)
                if from_b and to_b:
                    conn = Connection(from_b.output_port, to_b.input_ports[c_model.to_port_index])
                    self.scene.addItem(conn)

    def on_generate_code(self):
        self.sync_model_from_scene()
        generate_code(self.controller.get_diagram_data())
        QMessageBox.information(self, "Success", f"Code generated as subroutine '{self.model_name}.f90'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
