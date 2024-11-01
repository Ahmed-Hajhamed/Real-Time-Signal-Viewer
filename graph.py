import os

import numpy as np
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QDialog,
                             QFileDialog, QColorDialog, QCheckBox, QMenu, QLineEdit, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, QSize
import pyqtgraph as pg
from PlotWidget import CustomPlotWidget
from signal_1 import Signal


def set_icon(button, icon_path):
    pixmap = QPixmap(icon_path)
    button.setIcon(QIcon(pixmap))
    button.setIconSize(QSize(30, 30))
    button.setFixedSize(30, 30)
    button.setStyleSheet("border: none; background-color: none;")


class NameInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rename Item')

        # Layout for the dialog
        layout = QVBoxLayout()

        self.label = QLabel('Enter new name:', self)
        layout.addWidget(self.label)

        self.name_input = QLineEdit(self)
        layout.addWidget(self.name_input)

        self.confirm_button = QPushButton('Confirm', self)
        self.confirm_button.clicked.connect(self.accept)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def get_new_name(self):
        return self.name_input.text()


class Graph:
    def __init__(self):

        self.signals = dict()
        self.screenshots = []
        self.statistics = []
        self.selected_data = []
        self.is_cine_mode = True
        self.is_paused = False
        self.is_off = False
        self.current_index = 0
        self.current_index_increment = 10
        self.window_size = 100

        self.h_signal_name = QHBoxLayout()
        self.v_layout_icon_button = QVBoxLayout()
        self.v_layout_right_button = QVBoxLayout()
        self.h_buttons_layout = QHBoxLayout()
        self.v_layout_button = QVBoxLayout()
        self.h_layout = QHBoxLayout()

        button_style = """
                QPushButton {
                    background-color: #2a9d8f;
                    color: white;
                    border-radius: 10px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2ec4b6;
                }
                QPushButton:pressed {
                    background-color: #1b7f72;
                }
                """

        self.plot_widget = CustomPlotWidget()
        self.plot_widget.setLabel('left', 'Voltage', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.h_layout.addWidget(self.plot_widget)

        self.plot_widget.setLimits(xMin=0, xMax=50, yMin=5, yMax=5)

        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.check_hide)
        combo_box_style = """
    QComboBox {
        background-color: #2a9d8f;
        color: white;
        border-radius: 10px;
        padding: 5px;
    }
    QComboBox:hover {
        background-color: #2ec4b6;
    }
    QComboBox:pressed {
        background-color: #1b7f72;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: url(none);  /* Customize or remove the down arrow if needed */
    }
    QComboBox QAbstractItemView {
        background-color: #2a9d8f;  /* Background of the dropdown */
        color: white;
        selection-background-color: #2ec4b6;  /* Background when an item is hovered */
        padding: 5px;
        min-width: 170px;  /* Minimum width of the dropdown (adjust this as needed) */
    }
"""
        self.combo_box.setStyleSheet(combo_box_style)
        self.h_signal_name.addWidget(self.combo_box)

        self.more_button = QPushButton()
        set_icon(self.more_button, "icons/more.png")
        self.menu = QMenu()

        self.menu.addAction("Add", self.add_signal)
        self.menu.addAction("Rename", self.rename)
        self.menu.addAction("Delete", self.delete_signal)
        self.more_button.setMenu(self.menu)

        self.h_signal_name.addWidget(self.more_button)

        self.color_button = QPushButton()
        set_icon(self.color_button, "icons/color-picker.png")
        self.color_button.clicked.connect(self.change_line_color)
        self.color_button.setEnabled(False)
        self.v_layout_icon_button.addWidget(self.color_button)

        self.move_to_another_graph_button = QPushButton("Move to Other Graph")
        self.move_to_another_graph_button.setStyleSheet(button_style)
        self.v_layout_right_button.addWidget(self.move_to_another_graph_button)

        self.cine_mode_button = QPushButton("Cine Mode On")
        self.cine_mode_button.clicked.connect(self.cine_mode)
        self.cine_mode_button.setStyleSheet(button_style)
        self.v_layout_right_button.addWidget(self.cine_mode_button)

        self.play_pause_button = QPushButton()
        self.play_pause_button.clicked.connect(self.play_pause_signal)
        set_icon(self.play_pause_button, "icons/play.png")
        self.v_layout_icon_button.addWidget(self.play_pause_button)

        self.zoom_in_button = QPushButton()
        set_icon(self.zoom_in_button, "icons/zoom in.png")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setEnabled(False)
        self.v_layout_icon_button.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton()
        set_icon(self.zoom_out_button, "icons/zoom out.png")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setEnabled(False)
        self.v_layout_icon_button.addWidget(self.zoom_out_button)

        self.speed_button = QPushButton("1X")
        self.speed_button.clicked.connect(self.speed_signal)
        self.speed_button.setStyleSheet(button_style)
        self.v_layout_right_button.addWidget(self.speed_button)

        self.rewind_button = QPushButton("Rewind Signal")
        self.rewind_button.clicked.connect(self.rewind_signal)
        self.rewind_button.setStyleSheet(button_style)
        self.v_layout_right_button.addWidget(self.rewind_button)

        self.view_all_button = QPushButton("View All")
        self.view_all_button.clicked.connect(self.view_all_signals)
        self.view_all_button.setStyleSheet(button_style)
        self.v_layout_right_button.addWidget(self.view_all_button)

        self.visibility_checkbox = QCheckBox("Hide Signal")
        self.visibility_checkbox.setChecked(False)
        self.visibility_checkbox.stateChanged.connect(self.toggle_signal_visibility)
        self.v_layout_right_button.addWidget(self.visibility_checkbox)

        self.off_button = QPushButton("Off")
        self.off_button.setEnabled(False)
        self.off_button.clicked.connect(self.off_signal)
        self.off_button.setStyleSheet(button_style)
        self.v_layout_right_button.addWidget(self.off_button)

        self.h_buttons_layout.addLayout(self.v_layout_icon_button)
        self.h_buttons_layout.addLayout(self.v_layout_right_button)
        self.v_layout_button.addLayout(self.h_signal_name)
        self.v_layout_button.addLayout(self.h_buttons_layout)
        self.h_layout.addLayout(self.v_layout_button)

        self.timer = QTimer()
        self.timer.setInterval(100)  # Update every 100ms
        self.timer.timeout.connect(self.update_plot_graph)

        # Connect region change signal to handle selected data
        self.plot_widget.region.sigRegionChanged.connect(self.on_region_changed)

        self.update_placeholder_combo_box()

        self.colors = ['g', 'b', 'c', 'm', 'y']

    def on_region_changed(self):
        """Handle changes in the selected region."""
        if self.plot_widget.region:
            min_x, max_x = self.plot_widget.region.getRegion()
            signal_name = self.combo_box.currentText()

            if signal_name in self.signals:
                signal = self.signals[signal_name]
                mask = (signal.x_data >= min_x) & (signal.x_data <= max_x)
                selected_x = signal.x_data[mask]
                selected_y = signal.y_data[mask]
                self.selected_data = list(zip(selected_x, selected_y))  # Store selected data as (x, y) tuples

    def move_to_another_graph(self, graph):
        signal_name = self.combo_box.currentText()
        if signal_name not in graph.signals.keys() and signal_name != "Upload Signal":
            graph.add_signal(self.signals[signal_name].csv_file)
            self.delete_signal()

    def toggle_signal_visibility(self):
        signal_name = self.combo_box.currentText()
        if len(self.signals) > 0 and signal_name in self.signals.keys():
            checked = self.visibility_checkbox.isChecked()
            if checked:
                self.signals[signal_name].curve.setVisible(False)

            else:
                self.signals[signal_name].curve.setVisible(True)
            self.combo_box.setItemData(self.combo_box.currentIndex(), checked)

    def view_all_signals(self):
        # Set the view to fit all the plotted signals
        self.plot_widget.plotItem.vb.autoRange()

    def add_signal(self, csv_file=None):
        # Open a file dialog to select a CSV file
        if csv_file is None:
            csv_file, _ = QFileDialog.getOpenFileName(None, "Open CSV File", "", "CSV Files (*.csv)")
        signal_name = os.path.splitext(os.path.basename(csv_file))[0]

        if csv_file and signal_name not in self.signals.keys():
            color = self.colors[len(self.signals) % len(self.colors)]

            signal = Signal(self.plot_widget, color, name=signal_name, csv_file=csv_file)
            # for signal_on_graph in self.signals.values():
            #     if signal.y_data.size == signal_on_graph.y_data.size:
            #         if np.array_equal(signal.y_data, signal_on_graph.y_data):
            #             QMessageBox.warning(None, "Input Error", "Data already exist")
            #             break
            #         else:
            #             QMessageBox.warning(None, "Input Info", "Data has the same size but different values.")
            #             break
            self.combo_box.addItem(signal.name, False)
            self.update_placeholder_combo_box()
            self.signals[signal.name] = signal

            self.set_plot_limits()
            set_icon(self.play_pause_button, "icons/pause.png")
            self.off_button.setEnabled(True)
            self.zoom_in_button.setEnabled(True)
            self.zoom_out_button.setEnabled(True)
            self.color_button.setEnabled(True)
            self.move_to_another_graph_button.setEnabled(True)

            self.timer.start()
        else:
            QMessageBox.warning(None, "Input Error", f"A signal with the name '{signal_name}' already exists.")
            pass
    def cine_mode(self):
        if self.is_cine_mode:
            self.cine_mode_button.setText("Cine Mode Off")
        else:
            self.cine_mode_button.setText("Cine Mode On")

        self.is_cine_mode = not self.is_cine_mode

    def zoom_in(self):

        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]

        self.plot_widget.setXRange(x_range[0] + 0.1 * (x_range[1] - x_range[0]),
                                   x_range[1] - 0.1 * (x_range[1] - x_range[0]), padding=0)
        self.plot_widget.setYRange(y_range[0] + 0.1 * (y_range[1] - y_range[0]),
                                   y_range[1] - 0.1 * (y_range[1] - y_range[0]), padding=0)

    def zoom_out(self):

        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]

        self.plot_widget.setXRange(x_range[0] - 0.1 * (x_range[1] - x_range[0]),
                                   x_range[1] + 0.1 * (x_range[1] - x_range[0]), padding=0)
        self.plot_widget.setYRange(y_range[0] - 0.1 * (y_range[1] - y_range[0]),
                                   y_range[1] + 0.1 * (y_range[1] - y_range[0]), padding=0)

    def set_plot_limits(self):
        """Set the plot limits based on the loaded data."""
        if self.signals:
            x_max = max([signal.x_data[-1] for signal in self.signals.values()])

            y_min = min([min(signal.y_data) for signal in self.signals.values()])
            y_max = max([max(signal.y_data) for signal in self.signals.values()])

            y_min = y_min - y_min * 0.05 if y_min > 0 else y_min + y_min * 0.05

            self.plot_widget.setLimits(
                xMin=0, xMax=x_max + 10,
                yMin=y_min, yMax=y_max + y_max * 0.05
            )

    def change_line_color(self):
        # Open a color dialog and get the selected color for the line
        color = QColorDialog.getColor()

        if color.isValid():
            # Get the RGB values of the selected color
            rgb = color.getRgb()[:3]
            new_pen = pg.mkPen(color=rgb)

            signal_name = self.combo_box.currentText()
            self.signals[signal_name].curve.setPen(new_pen)

    def update_plot_graph(self):
        if self.signals and self.current_index < len(next(iter(self.signals.values())).x_data):

            x_data_fo_first_signal = next(iter(self.signals.values())).x_data

            # Update each individual signal
            for signal in self.signals.values():
                signal.update_plot(self.current_index)

            self.current_index += self.current_index_increment

            if self.is_cine_mode:
                start_index = max(0, self.current_index - self.window_size)

                self.plot_widget.setXRange(x_data_fo_first_signal[start_index],
                                           x_data_fo_first_signal[self.current_index], padding=1)
            else:
                self.plot_widget.setXRange(0, x_data_fo_first_signal[self.current_index], padding=1)

            self.plot_widget.setLimits(xMax=x_data_fo_first_signal[self.current_index])
        else:
            # self.rewind_signal()
            self.timer.stop()

    def delete_signal(self):
        """Delete the most recently added signal."""
        if len(self.signals) == 1:
            self.off_signal()
        elif self.signals:
            signal_name = self.combo_box.currentText()
            self.remove_selected_item()

            signal = self.signals.pop(signal_name)

            # Remove the curve from the plot
            signal.curve.clear()
            self.set_plot_limits()

    def update_placeholder_combo_box(self):
        if self.combo_box.count() == 0:
            self.combo_box.addItem("Upload Signal")
            self.combo_box.setEnabled(False)
        else:
            self.combo_box.setEnabled(True)
            if self.combo_box.itemText(0) == "Upload Signal":
                self.combo_box.removeItem(0)

    def remove_selected_item(self):
        current_index = self.combo_box.currentIndex()
        if current_index >= 0:
            self.combo_box.removeItem(current_index)
        self.update_placeholder_combo_box()

    def speed_signal(self):
        if self.current_index_increment == 10:
            self.current_index_increment = 20
            self.speed_button.setText("2X")
        elif self.current_index_increment == 20:
            self.current_index_increment = 40
            self.speed_button.setText("4X")
        elif self.current_index_increment == 40:
            self.current_index_increment = 80
            self.speed_button.setText("8X")
        else:
            self.current_index_increment = 10
            self.speed_button.setText("1X")

    def off_signal(self):
        self.timer.stop()

        for signal in self.signals.values():
            signal.curve.clear()
        self.signals = dict()

        self.combo_box.clear()
        self.update_placeholder_combo_box()

        self.current_index = 0
        set_icon(self.play_pause_button, "icons/play.png")
        self.is_paused = False
        self.off_button.setEnabled(False)
        self.zoom_in_button.setEnabled(False)
        self.zoom_out_button.setEnabled(False)
        self.color_button.setEnabled(False)
        self.move_to_another_graph_button.setEnabled(False)

        self.plot_widget.setLimits(xMin=0, xMax=2, yMin=-2, yMax=2)

    def play_pause_signal(self):
        if self.is_paused:
            if len(self.signals) == 0:
                self.add_signal("file_of_signal/ECG Signal (Lead V).csv")
            self.timer.start()
            set_icon(self.play_pause_button, "icons/pause.png")
        else:
            self.timer.stop()
            set_icon(self.play_pause_button, "icons/play.png")
        self.is_paused = not self.is_paused

    def rewind_signal(self):
        if self.signals:
            self.current_index = 0
            if self.is_paused:
                set_icon(self.play_pause_button, "icons/pause.png")
            self.timer.start()

    def check_hide(self):
        if self.combo_box.itemData(self.combo_box.currentIndex()):
            self.visibility_checkbox.setChecked(True)
        else:
            self.visibility_checkbox.setChecked(False)

    def rename(self):
        dialog = NameInputDialog()
        if dialog.exec_() == QDialog.Accepted:  # Check if dialog was accepted
            temp_dict = dict()
            new_name = dialog.get_new_name()
            index = self.combo_box.currentIndex()

            old_name = self.combo_box.currentText()
            for key, signal in self.signals.items():
                if key == old_name:
                    temp_dict[new_name] = signal
                    temp_dict[new_name].name = new_name
                else:
                    temp_dict[key] = signal
            self.signals =temp_dict

            if new_name:
                self.combo_box.setItemText(index, new_name)
                QMessageBox.information(None, 'Item Renamed', f'Item renamed to: {new_name}')
            else:
                QMessageBox.warning(None, 'Input Error', 'Please enter a valid name.')
