from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPolygonF
from PyQt5.QtWidgets import QLabel, QLineEdit
from .base import BaseBlock

class GainBlock(BaseBlock):
    def __init__(self, x, y, block_id=None):
        super().__init__("GAIN", x, y, width=80, height=80, block_id=block_id)
        self.gain_value = "1.0"
        self.title.setPlainText(self.gain_value)
        self.setup_ports(1)

    def paint(self, painter, option, widget):
        painter.setRenderHint(painter.Antialiasing)
        if self.isSelected():
            pen = QPen(Qt.black, 2, Qt.DashLine)
        else:
            pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        painter.setBrush(self.brush())
        rect = self.rect()
        triangle = QPolygonF([
            rect.topLeft(),
            rect.bottomLeft(),
            QPointF(rect.right(), rect.top() + rect.height()/2)
        ])
        painter.drawPolygon(triangle)

        if self.limit_enabled:
            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.drawLine(rect.bottomLeft(), rect.topRight())
            old_font = painter.font()
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(rect.adjusted(5, 2, 0, 0), Qt.AlignLeft | Qt.AlignTop, str(self.limit_max))
            painter.drawText(rect.adjusted(0, 0, -5, -2), Qt.AlignRight | Qt.AlignBottom, str(self.limit_min))
            painter.setFont(old_font)

    def create_config_fields(self, layout):
        layout.addWidget(QLabel("Gain Value:"))
        gain_edit = QLineEdit(self.gain_value)
        layout.addWidget(gain_edit)
        return {"gain": gain_edit}

    def extract_block_specific_values(self, fields):
        return {"gain": fields["gain"].text()}

    def apply_config(self, values):
        super().apply_config(values)
        self.gain_value = values.get("gain", self.gain_value)
        self.title.setPlainText(self.gain_value)
        self.center_text()

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"gain": self.gain_value})
        return cfg

    @staticmethod
    def get_fortran_code(cfg, mode, in_vars, out_var, k_idx, target_in_var=None):
        gain = cfg.get('gain', '1.0')
        code_lines = []
        if mode == 1:
            if target_in_var:
                code_lines.append(f"{target_in_var} = {out_var} / {gain}")
        elif mode in [2, 3]:
            code_lines.append(f"{out_var} = {in_vars[0]} * {gain}")
        
        code_lines.extend(BaseBlock.get_fortran_code(cfg, mode, in_vars, out_var, k_idx, target_in_var))
        return code_lines
