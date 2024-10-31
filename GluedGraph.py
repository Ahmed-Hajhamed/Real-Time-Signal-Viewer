import statistics
import sys
import numpy as np
import pyqtgraph as pg
from scipy.fft import fft
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox


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
        self.duration = 0
        self.data_y = None

        self.setWindowTitle("Signal Interpolation")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.v_layout = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.v_layout.addWidget(self.plot_widget)

        # Determine which signal is on the left and which is on the right
        self.determine_signal_order()

        # Fit the signals and plot them
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

    def determine_signal_order(self):
        """Determine left and right signals based on time."""
        if self.signal_1[0][0] < self.signal_2[0][0]:
            self.left_signal = self.signal_1
            self.right_signal = self.signal_2
        else:
            self.left_signal = self.signal_2
            self.right_signal = self.signal_1

    def reconstruct_signal(self, signal):
        """Reconstruct the signal using Fourier series."""
        # Extract time and values
        time, values = zip(*signal)
        time = np.array(time)
        values = np.array(values)

        # Perform FFT
        n = len(values)
        fft_values = fft(values)

        # Get significant frequencies and their amplitudes
        freq = np.fft.fftfreq(n, d=(time[1] - time[0]))
        significant_freqs = freq[:n // 2]  # Keep only positive frequencies
        significant_amplitudes = np.abs(fft_values[:n // 2])  # Keep magnitudes
        significant_phases = np.angle(fft_values[:n // 2])

        return significant_freqs, significant_amplitudes, significant_phases

    def fill_gap_with_fourier(self, gap_start, gap_end, num_points=100):
        """Fill the gap using Fourier components."""
        # Reconstruct both left and right signals
        left_freqs, left_amplitudes, left_phases = self.reconstruct_signal(self.left_signal)
        right_freqs, right_amplitudes, right_phases = self.reconstruct_signal(self.right_signal)

        # Create time points for the gap
        new_time_points = np.linspace(gap_start, gap_end, num_points)

        # Initialize predicted values
        predicted_values = np.zeros_like(new_time_points)

        # Get the max and min amplitude from both signals
        left_max_amplitude = max([y for x, y in self.left_signal])
        left_min_amplitude = min([y for x, y in self.left_signal])
        right_max_amplitude = max([y for x, y in self.right_signal])
        right_min_amplitude = min([y for x, y in self.right_signal])

        # Calculate average max and min amplitude
        avg_max_amplitude = (left_max_amplitude + right_max_amplitude) / 2
        avg_min_amplitude = (left_min_amplitude + right_min_amplitude) / 2

        # Add sinusoidal components from both signals
        for freq, amp, phase in zip(left_freqs, left_amplitudes, left_phases):
            predicted_values += (amp / np.max(left_amplitudes)) * avg_max_amplitude * np.sin(2 * np.pi * freq * (new_time_points - gap_start) + phase)

        for freq, amp, phase in zip(right_freqs, right_amplitudes, right_phases):
            predicted_values += (amp / np.max(right_amplitudes)) * avg_max_amplitude * np.sin(2 * np.pi * freq * (new_time_points - gap_end) + phase)

        # Rescale the predicted values to fit within the original signals' max and min amplitudes
        predicted_values = np.clip(predicted_values, avg_min_amplitude, avg_max_amplitude)

        # Rescale the predicted values to fit the range of original signals
        predicted_values = ((predicted_values - np.min(predicted_values)) /
                            (np.max(predicted_values) - np.min(predicted_values)) *
                            (avg_max_amplitude - avg_min_amplitude) + avg_min_amplitude)

        return new_time_points, predicted_values

    def plot_signals(self):
        # Extract time and signal values
        time_left, values_left = zip(*self.left_signal)
        time_right, values_right = zip(*self.right_signal)

        # Check if there's a gap between the left and right signals
        gap_exists = time_left[-1] < time_right[0]

        # Plot Left Signal
        self.plot_widget.plot(*zip(*self.left_signal), pen=pg.mkPen('b', width=2), name='Left Signal')

        # Plot Right Signal
        self.plot_widget.plot(*zip(*self.right_signal), pen=pg.mkPen('g', width=2), name='Right Signal')
        signal_1_data_x, signal_1_data_y = zip(*self.signal_1)
        signal_2_data_x, signal_2_data_y = zip(*self.signal_2)
        if gap_exists:
            # There is a real gap, so fill the gap using Fourier reconstruction
            gap_start = time_left[-1]
            gap_end = time_right[0]

            # Fill the gap
            new_time_points, predicted_values = self.fill_gap_with_fourier(gap_start, gap_end)

            # Plot Predicted Values in the gap
            self.plot_widget.plot(new_time_points, predicted_values, pen=pg.mkPen('r', width=2, style=pg.QtCore.Qt.DashLine), name='Predicted Values')

            # Combine original signals and predicted values for smoothness
            combined_signal = list(self.left_signal) + list(zip(new_time_points, predicted_values)) + list(self.right_signal)

            # Plot Combined Signal (entire sequence for smoothness)
            self.plot_widget.plot(*zip(*combined_signal), pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.SolidLine), name='Combined Signal')

            self.duration = max(signal_1_data_x[-1], signal_2_data_x[-1]) - min(signal_1_data_x[0], signal_2_data_x[0])
            self.data_y = list(predicted_values) + list(signal_2_data_y) + list(signal_1_data_y)
        else:
            self.data_y =list(signal_2_data_y) + list(signal_1_data_y)
        # Add grid and legend
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
