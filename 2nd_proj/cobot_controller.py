import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from pymycobot.mycobot import MyCobot
import time

class MyCobotControl(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize MyCobot
        self.mc = MyCobot('COM7', 115200)
        self.mc.send_angles([0,0,0,0,0,0],10)
        time.sleep(3)
        self.mc.set_gripper_calibration()
        self.mc.set_gripper_mode(0)
        self.mc.init_eletric_gripper()
        time.sleep(3)
        # Initialize angles to 0 for all 6 servos
        self.angles = [0, 0, 0, 0, 0, 0]
        self.min_angles = [-168, -180, -180, -180, -180, -180]
        self.max_angles = [168, 180, 180, 180, 180, 180]
        self.selected_servo = 0
        
        self.initUI()
        
    def initUI(self):
        # Layouts
        vbox = QVBoxLayout()
        
        # Initialize all servos to 0 degrees (first row)
        self.init_button = QPushButton('Initialize All Servos to 0°', self)
        self.init_button.clicked.connect(self.initialize_servos)
        vbox.addWidget(self.init_button)
        
        # Servo selection buttons (second row)
        hbox_servo_selection = QHBoxLayout()
        for i in range(1, 7):
            btn = QPushButton(f'Servo {i}', self)
            btn.clicked.connect(lambda checked, i=i: self.select_servo(i))
            hbox_servo_selection.addWidget(btn)
        vbox.addLayout(hbox_servo_selection)
        
        # Angle control buttons (third row)
        hbox_angle_control = QHBoxLayout()
        self.decrease_angle_button = QPushButton('-5°', self)
        self.decrease_angle_button.clicked.connect(self.decrease_angle)
        self.increase_angle_button = QPushButton('+5°', self)
        self.increase_angle_button.clicked.connect(self.increase_angle)
        hbox_angle_control.addWidget(self.decrease_angle_button)
        hbox_angle_control.addWidget(self.increase_angle_button)
        vbox.addLayout(hbox_angle_control)
        
        # Angle display (fourth row)
        self.angle_labels = []
        hbox_angle_display = QHBoxLayout()
        for i in range(6):
            lbl = QLabel(f'Servo {i+1}: {self.angles[i]}°', self)
            self.angle_labels.append(lbl)
            hbox_angle_display.addWidget(lbl)
        vbox.addLayout(hbox_angle_display)
        

        # Input fields for setting servo angles (fifth row)
        hbox_angle_inputs = QHBoxLayout()
        self.angle_inputs = []
        self.limit_labels = []  # Additional labels to display current limits
        for i in range(6):
            input_field = QLineEdit(self)
            input_field.setPlaceholderText(f'Servo {i+1} angle')
            limit_label = QLabel(f'({self.min_angles[i]},{self.max_angles[i]})', self)
            self.angle_inputs.append(input_field)
            self.limit_labels.append(limit_label)
            hbox_angle_inputs.addWidget(input_field)
            hbox_angle_inputs.addWidget(limit_label)
        vbox.addLayout(hbox_angle_inputs)
        
        # "Go" button to set servos to input angles (last row)
        self.go_button = QPushButton('Go', self)
        self.go_button.clicked.connect(self.set_input_angles)
        vbox.addWidget(self.go_button)

        hbox_gripper_control = QHBoxLayout()
        self.open_gripper_button = QPushButton('open gripper', self)
        self.open_gripper_button.clicked.connect(self.open_gripper)
        self.close_gripper_button = QPushButton('close gripper', self)
        self.close_gripper_button.clicked.connect(self.close_gripper)
        hbox_gripper_control.addWidget(self.open_gripper_button)
        hbox_gripper_control.addWidget(self.close_gripper_button)
        vbox.addLayout(hbox_gripper_control)
        
        self.setLayout(vbox)
        self.setWindowTitle('MyCobot Servo Control')
        self.show()

    def initialize_servos(self):
        """ Set all servos to 0 degrees. """
        self.angles = [0, 0, 0, 0, 0, 0]
        self.mc.send_angles(self.angles, 30)
        self.update_angle_labels()

    def close_gripper(self):
        self.mc.set_eletric_gripper(0)
        self.mc.set_gripper_value(0,20)

    def open_gripper(self):
        self.mc.set_eletric_gripper(1)
        self.mc.set_gripper_value(100,20)
    
    def select_servo(self, servo_number):
        """ Select a servo to control. """
        self.selected_servo = servo_number - 1
    
    def decrease_angle(self):
        """ Decrease the selected servo's angle by 5 degrees. """
        self.angles[self.selected_servo] = max(self.angles[self.selected_servo] - 5, -180)
        self.mc.send_angle(self.selected_servo + 1, self.angles[self.selected_servo], 20)
        self.update_angle_labels()
    
    def increase_angle(self):
        """ Increase the selected servo's angle by 5 degrees. """
        self.angles[self.selected_servo] = min(self.angles[self.selected_servo] + 5, 180)
        self.mc.send_angle(self.selected_servo + 1, self.angles[self.selected_servo], 20)
        self.update_angle_labels()
    
    def update_angle_labels(self):
        """ Update the angle display labels. """
        for i in range(6):
            self.angle_labels[i].setText(f'Servo {i+1}: {self.angles[i]}°')

    def set_input_angles(self):
        """ Set servos to the angles input in the text fields. """
        new_angles = []
        try:
            for i in range(6):
                # Get text from input and check if it's empty
                angle_text = self.angle_inputs[i].text()
                if angle_text.strip() == "":
                    raise ValueError(f"Angle for Servo {i+1} is empty")
                
                # Convert text to integer
                angle = int(angle_text)
                
                # Check if the angle is within the valid range
                if -180 <= angle <= 180:
                    new_angles.append(angle)
                else:
                    raise ValueError(f"Angle for Servo {i+1} out of range")
                    
            # If all angles are valid, send them to the robot
            self.angles = new_angles
            self.mc.send_angles(self.angles, 20)
            self.update_angle_labels()
        
        except ValueError as e:
            print(f"Invalid input: {e}")
            return
        
        self.angles = new_angles
        self.mc.send_angles(self.angles, 20)
        self.update_angle_labels()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyCobotControl()
    sys.exit(app.exec_())
