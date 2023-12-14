from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
import sys
from input_parser import Parser
from parking_lot import ParkingLot
import time
import asyncio



if __name__ == '__main__':
    app = QApplication(sys.argv)

    parser = Parser()
    parser.run()

    parking_lot = ParkingLot(parser)
    parking_lot.show()
    parking_lot.setWindowTitle('Valet Parking System')
    

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')

