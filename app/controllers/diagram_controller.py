from app.models.diagram import DiagramModel
import json

class DiagramController:
    def __init__(self, view=None):
        self.model = DiagramModel()
        self.view = view # This will be the MainWindow or a dedicated GraphicsView manager

    def set_model_name(self, name):
        self.model.model_name = name

    def set_model_type(self, m_type):
        self.model.model_type = m_type

    def is_id_available(self, block_id):
        return block_id not in self.model.blocks

    def add_block(self, b_type, x, y, block_id=None):
        if block_id and not self.is_id_available(block_id):
            # If ID is taken, we might want to throw or handle it.
            # For now, let's assume the caller ensures uniqueness or we generate a new one.
            pass
        block_model = self.model.add_block(block_id, b_type, x, y)
        return block_model

    def update_block_config(self, block_id, config):
        if block_id in self.model.blocks:
            self.model.blocks[block_id].config = config

    def update_block_position(self, block_id, x, y):
        if block_id in self.model.blocks:
            self.model.blocks[block_id].x = x
            self.model.blocks[block_id].y = y

    def add_connection(self, from_block_id, to_block_id, to_port_index):
        return self.model.add_connection(from_block_id, to_block_id, to_port_index)

    def remove_block(self, block_id):
        self.model.remove_block(block_id)

    def clear(self):
        self.model.clear()

    def get_diagram_data(self):
        return self.model.to_dict()

    def save_to_file(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.get_diagram_data(), f, indent=4)

    def load_from_file(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.clear()
        self.model.model_name = data.get("model_name", "USUARIO")
        self.model.model_type = data.get("model_type", "USRMDL")
        
        for b_data in data["blocks"]:
            self.model.add_block(b_data["id"], b_data["type"], b_data["x"], b_data["y"], b_data["config"])
        
        for c_data in data["connections"]:
            self.model.add_connection(c_data["from_block"], c_data["to_block"], c_data["to_port_index"])
        
        return self.model
