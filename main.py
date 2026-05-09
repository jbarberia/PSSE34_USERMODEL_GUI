import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QMainWindow
from app.view import GraphicsView
from app.blocks import GainBlock, IntegratorBlock, SumBlock

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Block Editor")
        self.resize(1000, 600)

        self.scene = QGraphicsScene()
        self.view = GraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.init_menu()

        # Bloques de ejemplo
        self.add_gain(100, 100)
        self.add_integrator(400, 250)
        self.add_sum(700, 150)

    def init_menu(self):
        menubar = self.menuBar()
        block_menu = menubar.addMenu("&Blocks")

        block_menu.addAction("Add &GAIN").triggered.connect(lambda: self.add_gain(50, 50))
        block_menu.addAction("Add &INTEGRATOR").triggered.connect(lambda: self.add_integrator(50, 50))
        block_menu.addAction("Add &SUM").triggered.connect(lambda: self.add_sum(50, 50))

    def add_gain(self, x, y):
        block = GainBlock(x, y)
        self.scene.addItem(block)
        return block

    def add_integrator(self, x, y):
        block = IntegratorBlock(x, y)
        self.scene.addItem(block)
        return block

    def add_sum(self, x, y):
        block = SumBlock(x, y)
        self.scene.addItem(block)
        return block

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
