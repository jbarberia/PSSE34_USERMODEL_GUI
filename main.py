import sys
import json
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QMessageBox, QFileDialog
from app.view import GraphicsView
from app.blocks import (GainBlock, IntegratorBlock, SumBlock, BaseBlock,
                        FirstOrderLagBlock, WashoutBlock, LeadLagBlock, PIBlock, PIDBlock)
from app.core import Connection
from app.codegen import generate_code

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Block Editor")
        self.resize(1000, 600)

        self.scene = QGraphicsScene()
        self.view = GraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        self.block_factory = {
            "GAIN": self.add_gain,
            "INTEGRATOR": lambda x, y: self.add_block(IntegratorBlock, x, y),
            "SUM": self.add_sum,
            "LAG 1": lambda x, y: self.add_block(FirstOrderLagBlock, x, y),
            "WASHOUT": lambda x, y: self.add_block(WashoutBlock, x, y),
            "LEAD LAG": lambda x, y: self.add_block(LeadLagBlock, x, y),
            "PI": lambda x, y: self.add_block(PIBlock, x, y),
            "PID": lambda x, y: self.add_block(PIDBlock, x, y)
        }
        
        self.init_menu()

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&Save").triggered.connect(self.on_save)
        file_menu.addAction("&Open").triggered.connect(self.on_open)
        file_menu.addAction("&Generate Code").triggered.connect(self.on_generate_code)

        block_menu = menubar.addMenu("&Blocks")
        block_menu.addAction("Add GAIN").triggered.connect(lambda: self.add_gain(50, 50))
        block_menu.addAction("Add SUM").triggered.connect(lambda: self.add_sum(50, 50))
        block_menu.addSeparator()
        block_menu.addAction("Add INTEGRATOR").triggered.connect(lambda: self.add_block(IntegratorBlock, 50, 50))
        block_menu.addAction("Add LAG 1").triggered.connect(lambda: self.add_block(FirstOrderLagBlock, 50, 50))
        block_menu.addAction("Add WASHOUT").triggered.connect(lambda: self.add_block(WashoutBlock, 50, 50))
        block_menu.addAction("Add LEAD LAG").triggered.connect(lambda: self.add_block(LeadLagBlock, 50, 50))
        block_menu.addAction("Add PI").triggered.connect(lambda: self.add_block(PIBlock, 50, 50))
        block_menu.addAction("Add PID").triggered.connect(lambda: self.add_block(PIDBlock, 50, 50))

    def serialize_diagram(self):
        blocks_data = []
        connections_data = []
        block_to_id = {}
        items = self.scene.items()
        for item in items:
            if isinstance(item, BaseBlock):
                block_id = f"block_{id(item)}"
                block_to_id[item] = block_id
                blocks_data.append({
                    "id": block_id, "type": item.block_name, "x": item.x(), "y": item.y(), "config": item.get_config()
                })
        for item in items:
            if isinstance(item, Connection) and item.port1 and item.port2:
                from_block = item.port1.parentItem()
                to_block = item.port2.parentItem()
                if from_block in block_to_id and to_block in block_to_id:
                    port_index = to_block.input_ports.index(item.port2)
                    connections_data.append({
                        "from_block": block_to_id[from_block], "to_block": block_to_id[to_block], "to_port_index": port_index
                    })
        return {"blocks": blocks_data, "connections": connections_data}

    def on_save(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Diagram", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as f: json.dump(self.serialize_diagram(), f, indent=4)

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Diagram", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as f: data = json.load(f)
            self.scene.clear()
            id_to_block = {}
            for b_data in data["blocks"]:
                add_func = self.block_factory.get(b_data["type"])
                if add_func:
                    block = add_func(b_data["x"], b_data["y"])
                    block.apply_config(b_data["config"])
                    id_to_block[b_data["id"]] = block
            for c_data in data["connections"]:
                from_b, to_b = id_to_block.get(c_data["from_block"]), id_to_block.get(c_data["to_block"])
                if from_b and to_b:
                    self.scene.addItem(Connection(from_b.output_port, to_b.input_ports[c_data["to_port_index"]]))

    def on_generate_code(self):
        generate_code(self.serialize_diagram())
        QMessageBox.information(self, "Success", "Code generated in 'generated_model.txt'")

    def add_gain(self, x, y):
        block = GainBlock(x, y)
        self.scene.addItem(block)
        return block

    def add_sum(self, x, y):
        block = SumBlock(x, y)
        self.scene.addItem(block)
        return block

    def add_block(self, block_class, x, y):
        block = block_class(x, y)
        self.scene.addItem(block)
        return block

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
