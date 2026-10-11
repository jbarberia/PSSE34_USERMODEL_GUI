class BlockModel:
    def __init__(self, block_id, b_type, x, y, config=None):
        self.block_id = block_id
        self.type = b_type
        self.x = x
        self.y = y
        self.config = config or {}

    def to_dict(self):
        return {
            "id": self.block_id,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "config": self.config
        }

class ConnectionModel:
    def __init__(self, from_block, to_block, to_port_index):
        self.from_block = from_block
        self.to_block = to_block
        self.to_port_index = to_port_index

    def to_dict(self):
        return {
            "from_block": self.from_block,
            "to_block": self.to_block,
            "to_port_index": self.to_port_index
        }

class DiagramModel:
    def __init__(self, model_name="USUARIO"):
        self.model_name = model_name
        self.model_type = "USRMDL"
        self.blocks = {} # ID -> BlockModel
        self.connections = []

    def add_block(self, block_id, b_type, x, y, config=None):
        block = BlockModel(block_id, b_type, x, y, config)
        self.blocks[block_id] = block
        return block

    def remove_block(self, block_id):
        if block_id in self.blocks:
            del self.blocks[block_id]
            # Also remove associated connections
            self.connections = [c for c in self.connections if c.from_block != block_id and c.to_block != block_id]

    def add_connection(self, from_block, to_block, to_port_index):
        conn = ConnectionModel(from_block, to_block, to_port_index)
        self.connections.append(conn)
        return conn

    def clear(self):
        self.blocks = {}
        self.connections = []

    def to_dict(self):
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "blocks": [b.to_dict() for b in self.blocks.values()],
            "connections": [c.to_dict() for c in self.connections]
        }
