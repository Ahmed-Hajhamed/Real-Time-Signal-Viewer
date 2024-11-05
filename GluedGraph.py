import statistics
import numpy as np
from scipy.interpolate import interp1d
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox


def calculate_statistics_data(amplitude):
    mean = statistics.mean(amplitude)
    standard_deviation = statistics.stdev(amplitude)
    maximum_amplitude = max(amplitude)
    minimum_amplitude = min(amplitude)
    return mean, standard_deviation, maximum_amplitude, minimum_amplitude


class GlueWindow(QMainWindow):
    number_of_images = 0
    statistics = []

    def __init__(self, signal_1, signal_2):
        super().__init__()

        self.signal_1 = signal_1
        self.signal_2 = signal_2
        self.glued_signal = None
        self.duration = 0
        self.data_y = None
        self.overlaps = False

        self.setWindowTitle("Signal Interpolation")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.v_layout = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.v_layout.addWidget(self.plot_widget)

        self.check_overlap_or_gap(self.signal_1, self.signal_2)
        self.glue_signals(self.signal_1, self.signal_2, self.overlaps)

        self.plot_signals()

        self.snapshot_button = QPushButton("snapshot")
        self.snapshot_button.clicked.connect(self.snapshot)
        self.snapshot_button.setStyleSheet("""
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
                """)
        self.v_layout.addWidget(self.snapshot_button)

        container = QWidget()
        container.setLayout(self.v_layout)
        self.setCentralWidget(container)

    def check_overlap_or_gap(self, signal1, signal2):
        """
        Returns true if 2 signals overlap and false if there's a gap.
        """
        min_time_1, max_time_1 = signal1[0][0], signal1[-1][0]
        min_time_2, max_time_2 = signal2[0][0], signal2[-1][0]
        
        if min_time_2 < min_time_1:
            signal1, signal2 = signal2, signal1
            min_time_1, max_time_1, min_time_2, max_time_2 = min_time_2, max_time_2, min_time_1, max_time_1

        # Check for overlap or gap
        if max_time_1 >= min_time_2:
            self.overlaps = True
        else:
            self.overlaps = False

    def glue_signals(self, signal1 , signal2, overlap):
        
        time1, values1 = zip(*signal1)
        time2, values2 = zip(*signal2)
        
        if time1[-1] > time2[0]:
            signal1, signal2 = signal2, signal1
            time1, values1, time2, values2 = time2, values2, time1, values1
        

        if overlap:
            
            overlap_start = max(time1[0], time2[0])
            overlap_end = min(time1[-1], time2[-1])
            
 
            overlap_indices1 = [i for i, t in enumerate(time1) if overlap_start <= t <= overlap_end]
            overlap_indices2 = [i for i, t in enumerate(time2) if overlap_start <= t <= overlap_end]
            

            averaged_overlap = [(time1[i], (values1[i] + values2[j]) / 2) 
                                for i, j in zip(overlap_indices1, overlap_indices2)]
            

            self.glued_signal = list(zip(time1[:overlap_indices1[0]], values1[:overlap_indices1[0]])) \
                        + averaged_overlap \
                        + list(zip(time2[overlap_indices2[-1] + 1:], values2[overlap_indices2[-1] + 1:]))
        

        else:

            gap_start, gap_end = time1[-1], time2[0]
            gap_time_points = np.linspace(gap_start, gap_end, num=50)
            

            interp_func = interp1d([time1[-1], time2[0]], [values1[-1], values2[0]], kind='linear')
            gap_values = interp_func(gap_time_points)
            

            self.glued_signal = list(zip(time1, values1)) \
                        + list(zip(gap_time_points, gap_values)) \
                        + list(zip(time2, values2))

    def plot_signals (self):
        self.plot_widget.plot(*zip(*self.glued_signal),pen=pg.mkPen('b', width = 2), name = 'Glued Signal')
        glued_signal_data_x, glued_signal_data_y = zip(*self.glued_signal)
        self.duration = glued_signal_data_x[-1] - glued_signal_data_x[0]

        self.data_y =list(glued_signal_data_y)

        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Signal Value')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.setTitle('Signal Interpolation')

    def snapshot(self):
        if (self.signal_1 or self.signal_2) is None:
            QMessageBox.warning(self, "Warning", "No signal to capture!")
            return

        GlueWindow.number_of_images+=1
        screenshot = self.plot_widget.grab()
        screenshot_filename = f"temp_image/temp_screenshot_{GlueWindow.number_of_images}.png"
        screenshot.save(screenshot_filename, 'PNG')

        mean, std_dev, max_amp, min_amp = calculate_statistics_data(
            self.data_y
        )

        GlueWindow.statistics.append({
            'mean': mean,
            'std_dev': std_dev,
            'max_amp': max_amp,
            'min_amp': min_amp,
            'duration': self.duration,
            'filename': screenshot_filename
        })

        QMessageBox.information(self, "Success", "Screenshot captured")
