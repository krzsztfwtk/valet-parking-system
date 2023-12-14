from asyncore import loop
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtCore import QThread, QVariantAnimation, QPointF, QPoint, QCoreApplication
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, Qt, QTimer
from parking_space import ParkingSpace, ParkingSpaceSingleton
from PyQt5.QtGui import QPainter, QFont, QColor, QPainter, QPen, QFontMetrics
from A_star import move_car_to_destination
from A_star_libs import move_car_to_destination_cpp, move_car_to_destination_rust
import time
import asyncio

class WorkerThread(QThread):
    moves_list_signal = pyqtSignal(list)
    elapsed_time_calculation_signal = pyqtSignal(float)
    elapsed_time_moving_signal = pyqtSignal(float)
    
    def __init__(self, parking_spaces, destination, car_id, parking_lot, lang, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.parking_spaces = parking_spaces
        self.destination = destination
        self.car_id = car_id
        self.parking_lot = parking_lot
        self.lang = lang
        

    def run(self):
        #try and delete declarations
        moves = []
        elapsed_time_calculation = 0.0
        elapsed_time_moving = 0.0
        print("starting calculation")
        match self.lang:
            case "python":        
                moves, elapsed_time_calculation = move_car_to_destination(self.parking_spaces, self.destination, self.car_id)
            case "cpp":        
                moves, elapsed_time_calculation = move_car_to_destination_cpp(self.parking_spaces, self.destination, self.car_id)
            case "rust":   
                moves, elapsed_time_calculation = move_car_to_destination_rust(self.parking_spaces, self.destination, self.car_id)
            case _:
                print("WRONG LANGUAGE! CHECK FOR TYPOS")
                return
        print("ending calculation")
        print(moves)

        self.moves_list_signal.emit(moves)
        self.elapsed_time_calculation_signal.emit(elapsed_time_calculation)
    
        

class Car(QGraphicsRectItem):
    next_id = 0
    # lang to be passed to Worker which does not take arguments
    lang = ""
    def __init__(self, col, row, width, height, speed, containing_parking_lot):
        self.parking_space_width = width + 10
        self.parking_space_height = height + 10

        self.col = col
        self.row = row

        start_x = col * self.parking_space_width + 5
        start_y = row * self.parking_space_height + 5

        super().__init__(start_x, start_y, width, height)

        self.singleton = ParkingSpaceSingleton()
        self.parking_spaces = self.singleton.parking_spaces

        self.setBrush(QColor('#000066'))
        self.setAcceptHoverEvents(True)
        self.speed = speed
        
        self.parking_lot = containing_parking_lot
        self.id = Car.next_id
        Car.next_id += 1

        self.is_moving = False
        
        self.lang = ""

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        
        # Initialize a QFont object for the painter
        font = QFont()
        text = str(self.id)
        rect = self.rect()
        max_height = rect.height() / 2  # Maximum height for the text
        
        # Start with a reasonably large font size for initial metrics
        font_size = 100
        font.setPointSize(font_size)
        painter.setFont(font)
        fm = QFontMetrics(font)
        
        # Decrease the font size until the text height is half the rect height or less
        while fm.height() > max_height:
            # Decrease font size
            font_size -= 1
            font.setPointSize(font_size)
            painter.setFont(font)
            fm = QFontMetrics(font)
        
        # Set the pen and draw the text
        painter.setPen(QPen(QColor('white')))
        painter.drawText(rect, Qt.AlignCenter, text)

    def hoverEnterEvent(self, event):
        if not self.is_moving:
            self.setBrush(QColor('#0000aa'))

    def hoverLeaveEvent(self, event):
        if not self.is_moving:
            self.setBrush(QColor('#000066'))

    def contextMenuEvent(self, event):
        contextMenu = QMenu()
        
        moveMenu = QMenu('Move', contextMenu)
        moveUp = QAction('↑', moveMenu)
        moveDown = QAction('↓', moveMenu)
        moveLeft = QAction('←', moveMenu)
        moveRight = QAction('→', moveMenu)
        moveToDepot = QAction("Move to depot Dijkstra's Python", contextMenu)
        moveToDestination = QAction('Move to Destination with A* Python', contextMenu)
        moveToDestinationCpp = QAction('Move to Destination with A* c++', contextMenu)
        moveToDestinationRust = QAction('Move to Destination with A* Rust', contextMenu)
        removeCar = QAction('Remove Car', contextMenu)
        
        moveUp.triggered.connect(self.move_up)
        moveDown.triggered.connect(self.move_down)
        moveLeft.triggered.connect(self.move_left)
        moveRight.triggered.connect(self.move_right)
        moveToDepot.triggered.connect(self.move_to_depot)
        moveToDestination.triggered.connect(lambda: self.move_to_destination("python"))
        moveToDestinationCpp.triggered.connect(lambda: self.move_to_destination("cpp"))
        moveToDestinationRust.triggered.connect(lambda: self.move_to_destination("rust"))
        removeCar.triggered.connect(self.remove)
        
        moveMenu.addAction(moveUp)
        moveMenu.addAction(moveDown)
        moveMenu.addAction(moveLeft)
        moveMenu.addAction(moveRight)
        
        contextMenu.addMenu(moveMenu)
        contextMenu.addAction(moveToDepot)
        contextMenu.addAction(moveToDestination)
        contextMenu.addAction(moveToDestinationCpp)
        contextMenu.addAction(moveToDestinationRust)

        contextMenu.addAction(removeCar)
        
        contextMenu.exec_(event.screenPos())
        
    def animate(self, start_space, end_space, 
                parking_space_width, parking_space_height, speed, distance):
        time = float(distance) / float(speed)
        time *= 1000
        time = int(time)

        self.col = end_space[0]
        self.row = end_space[1]

        current_x, current_y = self.x(), self.y()

        end_x = current_x + (end_space[0] - start_space[0]) * parking_space_width
        end_y = current_y + (end_space[1] - start_space[1]) * parking_space_height

        self.animation = QVariantAnimation()
        self.animation.setDuration(time)
        self.animation.setStartValue(QPointF(current_x, current_y))
        self.animation.setEndValue(QPointF(end_x, end_y))
        self.animation.valueChanged.connect(self.setPos)
        self.animation.start()
        
        #await for animation to finish
        loop = QEventLoop()

        def animation_finished():
            loop.quit()

        self.animation.finished.connect(animation_finished)

        # Start the animation
        self.animation.start()

        # Wait for the animation to finish
        loop.exec_()

    def move_up(self):
        start_space = (self.col, self.row)
        end_space = (self.col, self.row - 1)
        distance = self.parking_space_height / 50
        try:
            if self.parking_spaces[end_space[0]][end_space[1]].occupied:
                return 
        except IndexError:
            print("Can't move past the parking lot")
            return
        self.animate(start_space, 
                     end_space, 
                     self.parking_space_width,
                     self.parking_space_height, 
                     self.speed, distance)
        
        self.parking_spaces[start_space[0]][start_space[1]].occupied = False 
        self.parking_spaces[end_space[0]][end_space[1]].occupied = True 

        self.parking_spaces[start_space[0]][start_space[1]].car = None 
        self.parking_spaces[end_space[0]][end_space[1]].car = self

    def move_down(self):
        start_space = (self.col, self.row)
        end_space = (self.col, self.row + 1)
        distance = self.parking_space_height / 50
        try:
            if self.parking_spaces[end_space[0]][end_space[1]].occupied:
                return 
        except IndexError:
            print("Can't move past the parking lot")
            return

        self.animate(start_space, 
                     end_space, 
                     self.parking_space_width,
                     self.parking_space_height, 
                     self.speed, distance)
        
        self.parking_spaces[start_space[0]][start_space[1]].occupied = False 
        self.parking_spaces[end_space[0]][end_space[1]].occupied = True 

        self.parking_spaces[start_space[0]][start_space[1]].car = None 
        self.parking_spaces[end_space[0]][end_space[1]].car = self

    def move_left(self):
        start_space = (self.col, self.row)
        end_space = (self.col - 1, self.row)
        distance = self.parking_space_width / 50
        try:
            if self.parking_spaces[end_space[0]][end_space[1]].occupied:
                return 
        except IndexError:
            print("Can't move past the parking lot")
            return

        self.animate(start_space, 
                     end_space, 
                     self.parking_space_width,
                     self.parking_space_height, 
                     self.speed, distance)
        
        self.parking_spaces[start_space[0]][start_space[1]].occupied = False 
        self.parking_spaces[end_space[0]][end_space[1]].occupied = True 

        self.parking_spaces[start_space[0]][start_space[1]].car = None 
        self.parking_spaces[end_space[0]][end_space[1]].car = self

    def move_right(self):
        start_space = (self.col, self.row)
        end_space = (self.col + 1, self.row)
        distance = self.parking_space_width / 50
        try:
            if self.parking_spaces[end_space[0]][end_space[1]].occupied:
                return 
        except IndexError:
            print("Can't move past the parking lot")
            return


        self.animate(start_space, 
                     end_space, 
                     self.parking_space_width,
                     self.parking_space_height, 
                     self.speed, distance)
        
        self.parking_spaces[start_space[0]][start_space[1]].occupied = False 
        self.parking_spaces[end_space[0]][end_space[1]].occupied = True 

        self.parking_spaces[start_space[0]][start_space[1]].car = None 
        self.parking_spaces[end_space[0]][end_space[1]].car = self
            
    
    def move_to_destination(self, lang, destination_col = None, destination_row = None):
        
        if destination_col == None or destination_row == None:
            col, ok1 = QInputDialog.getInt(None, "Input", "Enter destination column:")
            row, ok2 = QInputDialog.getInt(None, "Input", "Enter destination row:")

            if ok1 and ok2:
                self.destination = (col, row)

            else:
                self.setBrush(QColor('#000066'))
                self.is_moving = False
                return
            #hardcoded for read from file requests
            self.remove_afterwards = False
        else:
            self.remove_afterwards = True
            self.destination = (destination_col, destination_row)

        self.is_moving = True
        self.setBrush(QColor('#ff0000'))

        self.parking_spaces[self.destination[0]][self.destination[1]].setAsDestination()
        self.parking_lot.start_timer()
        
        #move to init if it is garbage collected
        self.worker = WorkerThread(self.parking_spaces, self.destination, self.id, self.parking_lot, lang)
        self.worker.start()
        self.worker.finished.connect(self.evt_worker_finished)   
        
        self.worker.moves_list_signal.connect(self.write_move_1)
        self.worker.elapsed_time_calculation_signal.connect(self.write_2)
        # self.worker.move_direction_signal.connect(self.move)

    def write_move_1(self, val):
        start_time_moving = time.time()

        for move in val:
            direction, (src_x, src_y), (dest_x, dest_y) = move

            # signals for this
            if direction == 'right':
                self.parking_spaces[src_x][src_y].car.move_right()
            elif direction == 'up':
                self.parking_spaces[src_x][src_y].car.move_up()
            elif direction == 'left':
                self.parking_spaces[src_x][src_y].car.move_left()
            elif direction == 'down':
                self.parking_spaces[src_x][src_y].car.move_down()

        end_time_moving = time.time()
        elapsed_time_moving = end_time_moving - start_time_moving

        self.parking_spaces[self.destination[0]][self.destination[1]].unsetAsDestination()
        self.parking_lot.add_text_to_field(f"Moving time: {elapsed_time_moving:.2f} seconds, number of moves: {len(val)}, ")
        self.parking_lot.stop_timer()
        self.setBrush(QColor('#000066'))
        self.is_moving = False
        self.parking_lot.moves_next()
        if self.remove_afterwards:
            self.parking_lot.removeCarFromDetpot()
        
    def write_2(self, val):
        self.parking_lot.add_text_to_field(f"calculation time: {val*1000:.2f} milliseconds\n\n")
        
    # this function is now redundant; call move_to_destination with extra parameters instead
    # def move_to_depot(self, lang):
    #     self.is_moving = True
    #     self.setBrush(QColor('#ff0000'))
            
    #     moves, elapsed_time_calculation = self.move_to_destination(lang, 0, 0)
    #     print(moves)

    #     self.setBrush(QColor('#000066'))
    #     self.is_moving = False

        
    def move_to_depot(self):
        for parking_column in self.parking_spaces:
            for parking_space in parking_column:
                print(parking_space.occupied)
        self.parking_lot.pathfindToDepot(self.col, self.row, [], self.parking_lot.mapParkingLot())
        self.parking_lot.animateToDepot()
        
        
    def remove(self):
        # Directly remove this car instance from the scene
        self.parking_lot.scene.removeItem(self)
        # Update the parking space to mark it as unoccupied
        self.parking_lot.parking_spaces[self.col][self.row].car = None
        self.parking_lot.parking_spaces[self.col][self.row].occupied = False
        
    def evt_worker_finished(self):
        pass
