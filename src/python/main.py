import sys
import os
import traceback
import json
import logging

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from ast import literal_eval

from arduinoserial import ArduinoSerial
from reactiveprocessing import ReactiveProcessing

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)


# logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("RGB Controller")
        self.setWindowIcon(
            QIcon(
                f"{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/images/icon.png"
            )
        )
        self.resize(1280, 720)
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #0f1828;
            }
        """
        )
        button_width = self.width() / 4
        button_height = 100

        label = QLabel("RGB LED Controller", self)
        label.setFont(QFont("Copperplate Gothic Light", 48, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            QLabel {
                margin-top: 20px;
                color: white;
            }
        """
        )

        button1 = QPushButton("Solid Color")
        button1.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        button1.clicked.connect(self.on_button1_clicked)
        button1.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        button1.setFixedSize(button_width, button_height)

        button2 = QPushButton("Music Reactive")
        button2.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        button2.clicked.connect(self.on_button2_clicked)
        button2.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        button2.setFixedSize(button_width, button_height)

        button3 = QPushButton("Settings")
        button3.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        button3.clicked.connect(self.on_button3_clicked)
        button3.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }

            """
        )
        button3.setFixedSize(button_width, button_height)

        button4 = QPushButton("Exit")
        button4.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        button4.clicked.connect(self.on_button4_clicked)
        button4.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }

            """
        )
        button4.setFixedSize(button_width // 2, button_height)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(button1, alignment=Qt.AlignCenter)
        button_layout.addSpacing(20)
        button_layout.addWidget(button2, alignment=Qt.AlignCenter)
        button_layout.addSpacing(20)
        button_layout.addWidget(button3, alignment=Qt.AlignCenter)
        button_layout.addSpacing(20)
        button_layout.addWidget(button4, alignment=Qt.AlignCenter)

        label_layout = QVBoxLayout()
        label_layout.addWidget(label, alignment=Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(label_layout)
        main_layout.addSpacing(100)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.center()
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

    def center(self):
        available_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        x = available_geometry.center().x() - window_geometry.width() / 2
        y = available_geometry.center().y() - window_geometry.height() / 2
        self.move(x, y)

    def on_button1_clicked(self):
        self.solid_color_window = SolidColorWindow(self, self.read_config())
        self.hide()
        self.solid_color_window.show()

    def on_button2_clicked(self):
        self.music_reactive_window = MusicReactiveWindow(self, self.read_config())
        self.hide()
        self.music_reactive_window.show()

    def on_button3_clicked(self):
        self.settings_window = SettingsWindow(self, self.read_config())
        self.hide()
        self.settings_window.show()

    def on_button4_clicked(self):
        self.close()

    def read_config(self):
        config = json.load(
            open(f"{os.path.dirname(os.path.realpath(__file__))}/config.json", "r")
        )
        return config


class SolidColorWindow(QMainWindow):
    def __init__(self, MenuWindow: QMainWindow, config):
        super().__init__()
        self.MenuWindow = MenuWindow
        self.initUI()
        self.serial = ArduinoSerial(
            port=config.get("arduino_port"),
            arduino=True if config.get("arduino").lower() == "on" else False,
        )
        self.threadpool = QThreadPool()

    def initUI(self):
        self.resize(self.MenuWindow.size())
        self.setGeometry(self.MenuWindow.geometry())
        self.setStyleSheet(self.MenuWindow.styleSheet())
        self.setWindowIcon(self.MenuWindow.windowIcon())
        self.setWindowTitle("Solid Color")

        button_width = self.width() / 4
        button_height = self.height() / 4

        label = QLabel("Solid Color", self)
        label.setFont(QFont("Copperplate Gothic Light", 48, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            QLabel {
                margin-top: 20px;
                color: white;
            }
        """
        )
        self.color_picker_button = QPushButton("Select Color", self)
        self.color_picker_button.setFixedSize(button_width, button_height)
        self.color_picker_button.setFont(
            QFont(("Copperplate Gothic Light", 24, QFont.Bold))
        )
        self.color_picker_button.setStyleSheet(
            """
            QPushButton{
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        self.color_picker_button.clicked.connect(self.pick_color)

        back_button = QPushButton("Menu", self)
        back_button.setFixedSize(button_width // 2, button_height // 2)
        back_button.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        back_button.setStyleSheet(
            """
            QPushButton{
                background-color: #000000;
                color: white; 
                font-weight: bold; Z
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        back_button.clicked.connect(self.back_menu)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(self.color_picker_button, alignment=Qt.AlignCenter)

        label_layout = QVBoxLayout()
        label_layout.addWidget(label, alignment=Qt.AlignCenter)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(0)
        bottom_layout.setAlignment(Qt.AlignLeft)
        bottom_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(label_layout)
        main_layout.addSpacing(150)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(150)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def back_menu(self):
        self.close()
        self.MenuWindow.show()

    def pick_color(self):
        self.serial.start_serial()
        color = QColorDialog.getColor()
        if color.isValid():
            self.serial.communicate((color.red(), color.green(), color.blue()))

        self.color_picker_button.setStyleSheet(
            """
            QPushButton{
                background-color: %s;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
        """
            % color.name().strip("\n")
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        self.serial.close_serial()
        return super().closeEvent(event)


class MusicReactiveWindow(QMainWindow):
    def __init__(self, MenuWindow: QMainWindow, config):
        super().__init__()
        self.MenuWindow = MenuWindow

        self.main_reactive_logic = ReactiveProcessing(
            arduino_port=config.get("arduino_port"),
            arduino_on=True if config.get("arduino").lower() == "on" else False,
            chunk=int(config.get("fft_chunk")),
            rate=int(config.get("audio_rate")),
            channel=int(config.get("channel")),
            device_index=int(config.get("device_index")),
            energy_range=literal_eval(config.get("energy_range")),
            reactive=True if config.get("reactive").lower() == "true" else False,
            reactive_count=int(config.get("reactive_count")),
            colors=list(literal_eval(config.get("colors")))
            if type(literal_eval(config.get("colors"))[0]) is tuple
            else [literal_eval(config.get("colors"))],
        )
        self.threadpool = QThreadPool()
        self.initUI()

    def initUI(self):
        self.resize(self.MenuWindow.size())
        self.setGeometry(self.MenuWindow.geometry())
        self.setStyleSheet(self.MenuWindow.styleSheet())
        self.setWindowIcon(self.MenuWindow.windowIcon())
        self.setWindowTitle("Music Reactive")

        button_width, button_height = 300, 100

        label = QLabel("Music Reactive", self)
        label.setFont(QFont("Copperplate Gothic Light", 48, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            QLabel {
                margin-top: 20px;
                color: white;
            }
        """
        )

        button_start = QPushButton("Start")
        button_start.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        button_start.clicked.connect(self.on_button_start_clicked)
        button_start.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        button_start.setFixedSize(button_width, button_height)

        button_stop = QPushButton("Stop")
        button_stop.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        button_stop.clicked.connect(self.on_button_stop_clicked)
        button_stop.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        button_stop.setFixedSize(button_width, button_height)

        back_button = QPushButton("Menu", self)
        back_button.setFixedSize(button_width // 2, button_height // 2)
        back_button.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        back_button.setStyleSheet(
            """
            QPushButton{
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }
            """
        )
        back_button.clicked.connect(self.back_menu)

        self.figure = Figure(figsize=(15, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(button_start, alignment=Qt.AlignCenter)
        button_layout.addSpacing(20)
        button_layout.addWidget(button_stop, alignment=Qt.AlignCenter)

        label_layout = QVBoxLayout()
        label_layout.addWidget(label, alignment=Qt.AlignCenter)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(0)
        bottom_layout.setAlignment(Qt.AlignLeft)
        bottom_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(label_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)

        self.create_animation()
        self.setCentralWidget(container)

    def create_animation(self):
        freqs = self.main_reactive_logic.audio.freqs
        x_data = freqs[freqs < 5000]

        self.figure.set_facecolor("#0f1828")
        self.figure.clear()
        self.figure.suptitle("Energy(Frequency)", color="white")

        ax1 = self.figure.add_subplot(1, 2, 1)
        ax1.set_title("Current Energy")
        ax1.spines["left"].set_color("white")
        ax1.spines["bottom"].set_color("white")
        ax1.spines["bottom"].set_linewidth(2)
        ax1.tick_params(axis="both", colors="white")
        ax1.set_facecolor("#0f1828")
        ax1.title.set_color("white")

        ax2 = self.figure.add_subplot(1, 2, 2)
        ax2.set_title("Plot 2")
        ax2.set_title("Differential Energy")
        ax2.title.set_color("white")
        ax2.spines["left"].set_color("white")
        ax2.spines["bottom"].set_color("white")
        ax2.set_facecolor("#0f1828")
        ax2.spines["bottom"].set_linewidth(2)
        ax2.tick_params(axis="both", colors="white")

        (self.line,) = ax1.plot([], [])
        (self.line2,) = ax2.plot([], [])

        self.line.set_color("white")
        self.line2.set_color("white")

        ax1.set_xticks(x_data[::20])
        ax1.set_ylim(
            self.main_reactive_logic.energy_range[0],
            self.main_reactive_logic.energy_range[1],
        )
        ax2.set_xticks(x_data[::5])
        ax2.set_ylim(
            self.main_reactive_logic.energy_range[0],
            self.main_reactive_logic.energy_range[1],
        )

        def update(frame):
            y_data1 = self.main_reactive_logic.audio.energy_spectrum[: len(x_data)]
            y_data2 = self.main_reactive_logic.audio.diff_energy_spectrum[: len(x_data)]
            self.line.set_data(x_data, y_data1)
            self.line2.set_data(x_data, y_data2)
            ax1.set_ylim(
                self.main_reactive_logic.energy_range[0],
                self.main_reactive_logic.energy_range[1],
            )
            ax2.set_ylim(
                self.main_reactive_logic.energy_range[0],
                self.main_reactive_logic.energy_range[1] * 2,
            )
            ax2.set_xlim(
                self.main_reactive_logic.freq_range[0],
                self.main_reactive_logic.freq_range[1] * 1.5,
            )
            return (self.line, self.line2)

        self.ani = FuncAnimation(
            self.figure,
            update,
            interval=self.main_reactive_logic.audio._chunk
            / self.main_reactive_logic.audio._rate
            * 1000,
            cache_frame_data=False,
        )
        self.timer = self.canvas.new_timer(
            interval=self.main_reactive_logic.audio._chunk
            / self.main_reactive_logic.audio._rate
            * 1000
        )
        self.timer.add_callback(self.canvas.draw)

    def on_button_start_clicked(self):
        if not self.main_reactive_logic.running:
            self.timer.start()
            self.ani.resume()
            worker = Worker(self.main_reactive_logic.start)
            self.threadpool.start(worker)

    def on_button_stop_clicked(self):
        self.stop()

    def stop(self):
        self.timer.stop()
        self.main_reactive_logic.stop()
        self.ani.pause()
        self.line.set_data([], [])
        self.line2.set_data([], [])
        self.canvas.draw()

    def back_menu(self):
        self.close()
        self.MenuWindow.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.timer.stop()
        self.ani.pause()
        self.line.set_data([], [])
        self.line2.set_data([], [])
        self.canvas.draw()
        self.main_reactive_logic.stop()
        self.main_reactive_logic.close()

        del self.timer
        del self.ani

        return super().closeEvent(event)


class SettingsWindow(QMainWindow):
    def __init__(self, MenuWindow: QMainWindow, variables):
        super().__init__()
        self.MenuWindow = MenuWindow
        self.variables = variables
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Settings")
        self.resize(1280, 720)
        self.setWindowIcon(self.MenuWindow.windowIcon())
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #0f1828;
            }
        """
        )

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setVerticalSpacing(10)
        grid_layout.setAlignment(Qt.AlignCenter)

        row = 0
        col = 0
        for variable_name, variable_value in self.variables.items():
            label = QLabel(variable_name)
            label.setFont(QFont("Copperplate Gothic Light", 20, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                """
                QLabel {
                    color: white;
                }
            """
            )
            line_edit = QLineEdit(str(variable_value))
            line_edit.setFont(QFont("Copperplate Gothic Light", 20, QFont.Bold))
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setStyleSheet(
                """
                QLabel {
                    color: white;
                }
            """
            )
            line_edit.setFixedSize(self.frameGeometry().width() // 4, 50)
            line_edit.setObjectName(variable_name)
            grid_layout.addWidget(label, row, col * 2)
            grid_layout.addWidget(line_edit, row, col * 2 + 1)

            col += 1
            if col > 1:
                row += 1
                col = 0

        add_colors_button = QPushButton("Add color")
        add_colors_button.clicked.connect(self.add_colors)
        add_colors_button.setFixedSize(200, 100)
        add_colors_button.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        add_colors_button.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;

            }
            QPushButton:hover{
                background-color: #00002a;
            }

            """
        )
        grid_layout.addWidget(
            add_colors_button, row, col * 2 + 1, alignment=Qt.AlignCenter
        )

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        save_button.setFixedSize(self.frameGeometry().width() // 4, 100)
        save_button.setFont(QFont(("Copperplate Gothic Light", 24, QFont.Bold)))
        save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #000000;
                color: white; 
                font-weight: bold; 
                font-size: 24px; 
                padding: 12px; 
                border: none; 
                border-radius: 6px;
            }
            QPushButton:hover{
                background-color: #00002a;
            }

            """
        )

        label = QLabel("Config", self)
        label.setFont(QFont("Copperplate Gothic Light", 48, QFont.Bold))
        label.setAlignment(Qt.AlignTop)
        label.setStyleSheet(
            """
            QLabel {
                margin-top: 20px;
                color: white;
            }
        """
        )

        label_layout = QVBoxLayout()
        label_layout.addWidget(label, alignment=Qt.AlignCenter)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(0)
        main_layout.addLayout(label_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(grid_layout)
        main_layout.addSpacing(50)
        main_layout.addWidget(save_button, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

    def add_colors(self):
        color = QColorDialog.getColor()
        if color.isValid():
            colors_line_edit: QLineEdit = self.findChildren(QLineEdit, name="colors")[0]
            colors_line_edit.setText(
                f"{colors_line_edit.text()}, {color.red(), color.green(), color.blue()}"
            )

    def save_config(self):
        for child in self.findChildren(QLineEdit):
            variable_name = child.objectName()
            variable_value = child.text()
            self.variables[variable_name] = variable_value

        with open(
            f"{os.path.dirname(os.path.realpath(__file__))}/config.json", "w"
        ) as f:
            json.dump(self.variables, f, indent=4)

        self.close()
        self.MenuWindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
