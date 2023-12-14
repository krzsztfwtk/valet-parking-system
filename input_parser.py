from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

class Parser:
    def __init__(self):
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle('Valet Parking System')
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.parking_spots_rows_input = QLineEdit("4")
        self.parking_spots_cols_input = QLineEdit("3")
        self.agv_shuttles_input = QLineEdit("auto")
        self.agv_shuttles_input.setEnabled(False)
        self.depots_input = QLineEdit("1")
        self.depots_input.setEnabled(False)
        self.parking_spot_width_input = QLineEdit("5")
        self.parking_spot_height_input = QLineEdit("3")
        self.speed_input = QLineEdit("5")
        
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.on_submit)
        
        layout.addWidget(QLabel('Number of parking spots rows:'))
        layout.addWidget(self.parking_spots_rows_input)
        layout.addWidget(QLabel('Number of parking spots columns:'))
        layout.addWidget(self.parking_spots_cols_input)
        layout.addWidget(QLabel('Number of AGV shuttles:'))
        layout.addWidget(self.agv_shuttles_input)
        layout.addWidget(QLabel('Number of depots:'))
        layout.addWidget(self.depots_input)
        layout.addWidget(QLabel('Parking spot width [m]:'))
        layout.addWidget(self.parking_spot_width_input)
        layout.addWidget(QLabel('Parking spot height [m]:'))
        layout.addWidget(self.parking_spot_height_input)
        layout.addWidget(QLabel('AGV shuttles speed [m/s]:'))
        layout.addWidget(self.speed_input)
        layout.addWidget(self.submit_button)
        
        self.window.setLayout(layout)

    def on_submit(self):
        self.parking_spots_rows = self.parking_spots_rows_input.text()
        self.parking_spots_cols = self.parking_spots_cols_input.text()
        self.agv_shuttles = self.agv_shuttles_input.text()
        self.depots = self.depots_input.text()
        self.parking_spot_width = self.parking_spot_width_input.text()
        self.parking_spot_height = self.parking_spot_height_input.text()
        self.speed = self.speed_input.text()
        self.window.close()

    def run(self):
        self.window.show()
        self.app.exec_()
