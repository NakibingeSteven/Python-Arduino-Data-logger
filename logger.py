import sys
import serial
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog
from PyQt5.QtCore import QTimer

from serial.tools import list_ports

class DataLoggerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Logger")
        self.setGeometry(100, 100, 600, 400)

        self.port_dropdown = QComboBox()
        self.log_button = QPushButton("Log Data")
        self.save_button = QPushButton("Save Data")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.port_dropdown)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.log_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        layout.addWidget(self.log_text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.init_ui()
        self.init_serial()
        self.logged_data = []

    def init_ui(self):
        self.log_button.clicked.connect(self.start_logging)
        self.save_button.clicked.connect(self.save_data)
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
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_log)
        self.timer.start(1000)  # Update every 1 second

    def update_log(self):
        line = self.serial.readline().decode().strip()
        if ',' in line:
            distance, command = line.split(',')
            data_str = f"Distance: {distance} cm, Command: {command}"
            self.log_text.append(data_str)
            self.logged_data.append(data_str)

    def save_data(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv)", options=options)
        if file_name:
            with open(file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["Distance", "Command"])
                for data in self.logged_data:
                    distance, command = data.split(',')[0].split(': ')[1], data.split(',')[1].split(': ')[1]
                    csv_writer.writerow([distance, command])

    def closeEvent(self, event):
        if self.serial.is_open:
            self.serial.close()
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataLoggerApp()
    window.show()
    sys.exit(app.exec_())
