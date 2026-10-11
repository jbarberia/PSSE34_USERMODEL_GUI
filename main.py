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
    QComboBox,
)
from PyQt5.QtCore import Qt

from app.views import GraphicsView, CodePreviewWidget, AllocationTableWidget
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
from app.codegen import generate_code, MODEL_TYPES


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = DiagramController()
        self.setWindowTitle("Control Block Editor - PSS/E Dynamics Models")
        self.resize(1300, 800)

        self.model_name = self.controller.model.model_name
        self.model_type = self.controller.model.model_type
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
        self.init_docks()

    def init_menu(self):
        menubar = self.menuBar()

        # --- Menu Archivo ---
        file_menu = menubar.addMenu("&Archivo")
        file_menu.addAction("&Abrir Diagrama...").triggered.connect(self.on_open)
        file_menu.addAction("&Guardar Diagrama").triggered.connect(self.on_save)
        file_menu.addSeparator()
        file_menu.addAction("&Generar Código Fortran").triggered.connect(self.on_generate_code)
        file_menu.addSeparator()
        file_menu.addAction("&Salir").triggered.connect(self.close)

        # --- Menu Bloques ---
        block_menu = menubar.addMenu("&Bloques")
        signal_menu = block_menu.addMenu("Señales")
        signal_menu.addAction("Agregar INPUT").triggered.connect(lambda: self.add_new_block("INPUT"))
        signal_menu.addAction("Agregar OUTPUT").triggered.connect(lambda: self.add_new_block("OUTPUT"))
        block_menu.addSeparator()
        block_menu.addAction("Agregar GAIN").triggered.connect(lambda: self.add_new_block("GAIN"))
        block_menu.addAction("Agregar SUM").triggered.connect(lambda: self.add_new_block("SUM"))
        control_menu = block_menu.addMenu("Control")
        control_menu.addAction("Agregar INTEGRATOR").triggered.connect(lambda: self.add_new_block("INTEGRATOR"))
        control_menu.addAction("Agregar LAG 1").triggered.connect(lambda: self.add_new_block("LAG 1"))
        control_menu.addAction("Agregar WASHOUT").triggered.connect(lambda: self.add_new_block("WASHOUT"))
        control_menu.addAction("Agregar LEAD LAG").triggered.connect(lambda: self.add_new_block("LEAD LAG"))
        control_menu.addAction("Agregar PI").triggered.connect(lambda: self.add_new_block("PI"))
        control_menu.addAction("Agregar PID").triggered.connect(lambda: self.add_new_block("PID"))

        # --- Menu Paneles / Vistas ---
        view_menu = menubar.addMenu("&Ver")
        self.action_show_props = view_menu.addAction("Panel de Propiedades")
        self.action_show_props.setCheckable(True)
        self.action_show_props.setChecked(True)
        self.action_show_props.triggered.connect(lambda c: self.dock_properties.setVisible(c))

        self.action_show_preview = view_menu.addAction("Vista Previa de Código Fortran")
        self.action_show_preview.setCheckable(True)
        self.action_show_preview.setChecked(False)
        self.action_show_preview.triggered.connect(lambda c: self.dock_code_preview.setVisible(c))

        self.action_show_table = view_menu.addAction("Tabla de Asignaciones (CON/STATE/VAR)")
        self.action_show_table.setCheckable(True)
        self.action_show_table.setChecked(False)
        self.action_show_table.triggered.connect(lambda c: self.dock_allocations.setVisible(c))

    def init_properties_panel(self):
        self.dock_properties = QDockWidget("Propiedades", self)
        self.dock_properties.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        main_container = QWidget()
        self.main_layout = QVBoxLayout(main_container)

        # --- SECCIÓN GLOBAL ---
        global_group = QWidget()
        global_layout = QVBoxLayout(global_group)
        global_layout.addWidget(QLabel("<b>Configuración Global</b>"))
        form = QFormLayout()
        self.subroutine_edit = QLineEdit(self.model_name)
        self.subroutine_edit.textChanged.connect(self.on_model_name_changed)
        form.addRow("Nombre de Subrutina:", self.subroutine_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(list(MODEL_TYPES.keys()))
        self.type_combo.setCurrentText(self.model_type)
        self.type_combo.currentTextChanged.connect(self.on_model_type_changed)
        form.addRow("Tipo de Modelo PSS/E:", self.type_combo)

        global_layout.addLayout(form)
        self.main_layout.addWidget(global_group)

        self.main_layout.addWidget(QFrame(frameShape=QFrame.HLine, frameShadow=QFrame.Sunken))

        # --- SECCIÓN DE BLOQUE SELECCIONADO ---
        self.block_group = QWidget()
        self.block_layout = QVBoxLayout(self.block_group)
        self.main_layout.addWidget(self.block_group)
        self.block_group.hide()

        self.main_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(main_container)
        self.dock_properties.setWidget(scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_properties)

        self.dock_properties.visibilityChanged.connect(
            lambda v: self.action_show_props.setChecked(v)
        )

    def init_docks(self):
        # Dock de Vista Previa de Código
        self.dock_code_preview = QDockWidget("Vista Previa Fortran", self)
        self.dock_code_preview.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        self.code_preview = CodePreviewWidget(self)
        self.dock_code_preview.setWidget(self.code_preview)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_code_preview)
        self.dock_code_preview.hide()
        self.dock_code_preview.visibilityChanged.connect(
            lambda v: self.action_show_preview.setChecked(v)
        )

        # Dock de Tabla de Asignaciones
        self.dock_allocations = QDockWidget("Tabla de Asignaciones PSS/E", self)
        self.dock_allocations.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        self.table_allocations = AllocationTableWidget(
            on_change_callback=self.on_allocations_table_updated, parent=self
        )
        self.dock_allocations.setWidget(self.table_allocations)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_allocations)
        self.dock_allocations.hide()
        self.dock_allocations.visibilityChanged.connect(
            lambda v: self.action_show_table.setChecked(v)
        )

    def on_model_name_changed(self, text):
        self.model_name = text.strip() or "USUARIO"
        self.controller.set_model_name(self.model_name)

    def on_model_type_changed(self, text):
        self.model_type = text
        self.controller.set_model_type(self.model_type)

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
        layout.addWidget(QLabel(f"<b>Bloque: {block.block_name}</b>"))

        self.current_prop_fields = block.build_config_ui(layout)

        apply_btn = QPushButton("Aplicar Cambios")
        apply_btn.clicked.connect(self.apply_block_properties)
        layout.addWidget(apply_btn)
        self.block_group.show()

    def apply_block_properties(self):
        if self.current_selected_block:
            values = self.current_selected_block.extract_config_values(self.current_prop_fields)
            new_id = values.get('block_id')
            old_id = self.current_selected_block.block_id

            # Comprobar colisión de ID si cambió
            if new_id != old_id and not self.controller.is_id_available(new_id):
                QMessageBox.warning(
                    self, "ID Duplicado", f"El ID '{new_id}' ya está en uso. Por favor elija uno único."
                )
                return

            if new_id != old_id:
                self.controller.remove_block(old_id)
                self.current_selected_block.apply_config(values)
                self.controller.add_block(
                    self.current_selected_block.block_name,
                    self.current_selected_block.x(),
                    self.current_selected_block.y(),
                    block_id=new_id,
                )
            else:
                self.current_selected_block.apply_config(values)

            self.controller.update_block_config(
                self.current_selected_block.block_id, self.current_selected_block.get_config()
            )
            self.scene.update()
            self.update_live_code_and_allocations()

    def add_new_block(self, b_type, x=50, y=50, block_id=None, config=None):
        if not block_id:
            count = self.block_counts.get(b_type, 0) + 1
            clean_type = b_type.replace(" ", "")
            block_id = f"{clean_type}{count}"

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

            self.controller.add_block(b_type, x, y, block_id=block_id)
            if config:
                self.controller.update_block_config(block_id, config)

            return block
        return None

    def on_save(self):
        self.sync_model_from_scene()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Diagrama", "", "JSON Files (*.json)")
        if file_path:
            self.controller.save_to_file(file_path)

    def sync_model_from_scene(self):
        """
        Sincroniza los bloques y conexiones de la escena gráfica con el modelo del DiagramController.
        """
        self.controller.clear()
        self.controller.set_model_name(self.model_name)
        self.controller.set_model_type(self.model_type)

        items = self.scene.items()
        blocks = [item for item in items if isinstance(item, BaseBlock)]

        for b in blocks:
            self.controller.add_block(b.block_name, b.x(), b.y(), block_id=b.block_id)
            self.controller.update_block_config(b.block_id, b.get_config())

        for item in items:
            if isinstance(item, Connection) and item.port1 and item.port2:
                from_b, to_b = item.port1.parentItem(), item.port2.parentItem()
                if isinstance(from_b, BaseBlock) and isinstance(to_b, BaseBlock):
                    if item.port2 in to_b.input_ports:
                        port_index = to_b.input_ports.index(item.port2)
                        self.controller.add_connection(from_b.block_id, to_b.block_id, port_index)

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Diagrama", "", "JSON Files (*.json)")
        if file_path:
            model = self.controller.load_from_file(file_path)
            self.scene.clear()
            self.block_counts = {}
            self.model_name = model.model_name
            self.model_type = model.model_type
            self.subroutine_edit.setText(self.model_name)
            self.type_combo.setCurrentText(self.model_type)

            id_to_block = {}
            for b_id, b_model in model.blocks.items():
                block = self.add_new_block(
                    b_model.type, b_model.x, b_model.y, block_id=b_model.block_id, config=b_model.config
                )
                if block:
                    id_to_block[b_id] = block

            for c_model in model.connections:
                from_b = id_to_block.get(c_model.from_block)
                to_b = id_to_block.get(c_model.to_block)
                if from_b and to_b and c_model.to_port_index < len(to_b.input_ports):
                    conn = Connection(from_b.output_port, to_b.input_ports[c_model.to_port_index])
                    self.scene.addItem(conn)

            self.update_live_code_and_allocations()

    def update_live_code_and_allocations(self):
        """Genera el código y actualiza la vista previa y tabla si los paneles están visibles."""
        try:
            self.sync_model_from_scene()
            diagram_data = self.controller.get_diagram_data()
            if diagram_data["blocks"]:
                code = generate_code(diagram_data)
                self.code_preview.set_code(code)
                self._sync_allocations_from_diagram(diagram_data)
        except Exception:
            pass

    def _sync_allocations_from_diagram(self, diagram_data):
        """Extrae automáticamente variables CON, STATE y VAR de los bloques del diagrama."""
        data_list = []
        state_blocks = ["INTEGRATOR", "PI", "LAG 1", "WASHOUT", "LEAD LAG", "PID"]

        for b in diagram_data.get("blocks", []):
            b_type = b.get("type")
            b_id = b.get("id")
            cfg = b.get("config", {})

            # CONSTANTES (CON)
            if b_type == "GAIN":
                data_list.append({"type": "CON", "name": f"{b_id}_GAIN", "val": cfg.get("gain", "1.0"), "desc": "Ganancia"})
            elif b_type == "INTEGRATOR":
                data_list.append({"type": "CON", "name": f"{b_id}_TI", "val": cfg.get("ti", "1.0"), "desc": "Constante de tiempo integración"})
            elif b_type in ["LAG 1", "WASHOUT"]:
                data_list.append({"type": "CON", "name": f"{b_id}_KI", "val": cfg.get("ki", "1.0"), "desc": "Ganancia"})
                data_list.append({"type": "CON", "name": f"{b_id}_TI", "val": cfg.get("ti", "1.0"), "desc": "Constante de tiempo"})
            elif b_type == "LEAD LAG":
                data_list.append({"type": "CON", "name": f"{b_id}_KI", "val": cfg.get("ki", "1.0"), "desc": "Ganancia"})
                data_list.append({"type": "CON", "name": f"{b_id}_T1", "val": cfg.get("t1", "1.0"), "desc": "Tiempo adelanto (T1)"})
                data_list.append({"type": "CON", "name": f"{b_id}_T2", "val": cfg.get("t2", "1.0"), "desc": "Tiempo atraso (T2)"})
            elif b_type == "PI":
                data_list.append({"type": "CON", "name": f"{b_id}_KP", "val": cfg.get("kp", "1.0"), "desc": "Ganancia proporcional"})
                data_list.append({"type": "CON", "name": f"{b_id}_KI", "val": cfg.get("ki", "1.0"), "desc": "Ganancia integral"})
            elif b_type == "PID":
                data_list.append({"type": "CON", "name": f"{b_id}_KP", "val": cfg.get("kp", "1.0"), "desc": "Ganancia proporcional"})
                data_list.append({"type": "CON", "name": f"{b_id}_KI", "val": cfg.get("ki", "1.0"), "desc": "Ganancia integral"})
                data_list.append({"type": "CON", "name": f"{b_id}_KD", "val": cfg.get("kd", "1.0"), "desc": "Ganancia derivativa"})
                data_list.append({"type": "CON", "name": f"{b_id}_TD", "val": cfg.get("td", "0.1"), "desc": "Filtro derivativo"})

            # ESTADOS (STATE)
            if b_type in state_blocks:
                data_list.append({"type": "STATE", "name": f"STATE_{b_id}", "val": "0.0", "desc": f"Variable de estado de {b_id}"})

            # VARIABLES (VAR)
            if b_type == "OUTPUT":
                data_list.append({"type": "VAR", "name": f"VAR_{b_id}", "val": "0.0", "desc": f"Salida modelo ({cfg.get('type', 'VAR')})"})

        self.table_allocations.set_data(data_list)

    def on_allocations_table_updated(self):
        """Callback ejecutado cuando la tabla de asignaciones sufre un cambio manual."""
        pass

    def on_generate_code(self):
        self.sync_model_from_scene()
        diagram_data = self.controller.get_diagram_data()
        if not diagram_data["blocks"]:
            QMessageBox.warning(self, "Diagrama Vacío", "No hay bloques en el diagrama para generar código.")
            return

        code = generate_code(diagram_data)
        self.code_preview.set_code(code)
        self.dock_code_preview.show()
        self.action_show_preview.setChecked(True)
        QMessageBox.information(
            self,
            "Código Generado con Éxito",
            f"Se ha generado la subrutina '{self.model_name}.f90'.\nPuede verla y exportarla en el panel de Vista Previa.",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
