from .base import BaseBlock
from .signal_mixin import SignalBlockMixin

class InputBlock(BaseBlock, SignalBlockMixin):
    def __init__(self, x, y, block_id=None):
        super().__init__("INPUT", x, y, width=140, height=60, block_id=block_id)
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

    def extract_block_specific_values(self, fields):
        return {
            "type": fields["type"].currentText(),
            "id_mode": fields["id_mode"].isChecked(),
            "index": fields["idx_edit"].text(),
            "id_main": fields["id_main_edit"].text(),
            "id_sub": fields["id_sub_edit"].text()
        }

    def apply_config(self, values):
        super().apply_config(values)
        self.signal_type = values.get("type", self.signal_type)
        self.use_id_mode = values.get("id_mode", self.use_id_mode)
        cat = self.get_category(self.signal_type)
        if self.use_id_mode:
            if cat == "BUS_ONLY":
                self.bus_num = values.get("id_main", self.bus_num)
            elif cat == "MACHINE":
                self.bus_num = values.get("id_main", self.bus_num)
                self.machine_id = values.get("id_sub", self.machine_id)
        else:
            self.index_val = values.get("index", self.index_val)
        self.update_title()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            "type": self.signal_type, "id_mode": self.use_id_mode, "index": self.index_val,
            "machine_num": self.machine_num, "machine_id": self.machine_id, "bus_num": self.bus_num
        })
        return cfg

    @staticmethod
    def get_mode1_code(cfg, out_var, target_in_var, k_idx):
        return [f"! Input {cfg.get('block_id')} initialized to {out_var}"]

    @staticmethod
    def get_mode2_code(cfg, in_vars, out_var, k_idx):
        if cfg.get("id_mode"):
            return [f"{out_var} = GET_SIGNAL('{cfg.get('type')}', {cfg.get('bus_num', 0)}, '{cfg.get('machine_id', '')}')"]
        else:
            return [f"{out_var} = {cfg.get('type', 'VAR')}({cfg.get('index', 1)})"]

    @staticmethod
    def get_mode3_code(cfg, in_vars, out_var, k_idx):
        return InputBlock.get_mode2_code(cfg, in_vars, out_var, k_idx)

    @staticmethod
    def get_mode8_code(cfg, j_idx):
        return []
