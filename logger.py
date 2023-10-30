import sys
import serial
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QTextEdit, QVBoxLayout, QWidget
from serial.tools import list_ports

class DataLoggerApp(QMainWindow):
    def __init__(self):
        super().__init()

        self.setWindowTitle("Data Logger")
        self.setGeometry(100, 100, 400, 300)

        self.port_dropdown = QComboBox()
        self.log_button = QPushButton("Log Data")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.port_dropdown)
        layout.addWidget(self.log_button)
        layout.addWidget(self.log_text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.init_ui()
        self.init_serial()

    def init_ui(self):
        self.log_button.clicked.connect(self.start_logging)
        self.update_port_list()
        
    def init_serial(self):
        self.serial = serial.Serial()

    def update_port_list(self):
        com_ports = [port.device for port in list_ports.comports()]
        self.port_dropdown.addItems(com_ports)

    def start_logging(self):
        com_port = self.port_dropdown.currentText()
        self.serial.port = com_port
        self.serial.baudrate = 9600  # You can adjust the baud rate as needed
        self.serial.timeout = 2  # Adjust the timeout as needed

        try:
            self.serial.open()
        except serial.SerialException:
            self.log_text.append("Error: Unable to open the selected COM port.")
            return

        self.log_text.append("Logging data from " + com_port)
        with open('sensor_data.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Distance", "Command"])

            while self.serial.is_open:
                line = self.serial.readline().decode().strip()
                if ',' in line:
                    distance, command = line.split(',')
                    csv_writer.writerow([distance, command])
                    self.log_text.append(f"Distance: {distance} cm, Command: {command}")

    def closeEvent(self, event):
        if self.serial.is_open:
            self.serial.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataLoggerApp()
    window.show()
    sys.exit(app.exec_())
