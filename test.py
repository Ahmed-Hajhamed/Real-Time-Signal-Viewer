import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPdfWriter, QPainter, QFont
from PyQt5.QtCore import QSize, QRect
import pyqtgraph as pg
import time

class RealTimePlotApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-time Plot with Snapshots")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Plot widget (real-time signal)
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Button to take snapshot
        self.snapshot_button = QPushButton("Take Snapshot")
        self.snapshot_button.clicked.connect(self.take_snapshot)
        self.layout.addWidget(self.snapshot_button)

        # Button to save PDF
        self.save_pdf_button = QPushButton("Save PDF")
        self.save_pdf_button.clicked.connect(self.save_pdf)
        self.layout.addWidget(self.save_pdf_button)

        # Table to show statistics
        self.stats_table = QTableWidget(5, 2)
        self.stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])
        self.stats_table.setVerticalHeaderLabels(["Mean", "Std", "Min", "Max", "Duration"])
        self.layout.addWidget(self.stats_table)

        # List to store snapshots and statistics
        self.snapshots = []

        # Start real-time plotting
        self.start_real_time_plot()

    def start_real_time_plot(self):
        """Start real-time signal simulation (update every 100 ms)."""
        self.x = np.linspace(0, 2 * np.pi, 100)
        self.plot_data = np.sin(self.x) + 0.1 * np.random.randn(100)
        self.plot_item = self.plot_widget.plot(self.plot_data, pen='b')

        # Update the plot every 100 ms
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def update_plot(self):
        """Update the plot with new signal data."""
        self.plot_data = np.sin(self.x) + 0.1 * np.random.randn(100)
        self.plot_item.setData(self.plot_data)

    def take_snapshot(self):
        """Take a snapshot of the plot and compute statistics."""
        snapshot = {
            'data': self.plot_data.copy(),
            'timestamp': time.time(),
        }
        self.snapshots.append(snapshot)

        # Compute and display statistics in the table
        mean_val = np.mean(snapshot['data'])
        std_val = np.std(snapshot['data'])
        min_val = np.min(snapshot['data'])
        max_val = np.max(snapshot['data'])
        duration = len(snapshot['data'])

        self.stats_table.setItem(0, 1, QTableWidgetItem(f"{mean_val:.2f}"))
        self.stats_table.setItem(1, 1, QTableWidgetItem(f"{std_val:.2f}"))
        self.stats_table.setItem(2, 1, QTableWidgetItem(f"{min_val:.2f}"))
        self.stats_table.setItem(3, 1, QTableWidgetItem(f"{max_val:.2f}"))
        self.stats_table.setItem(4, 1, QTableWidgetItem(f"{duration}"))

    def save_pdf(self):
        """Save the snapshots and statistics to a PDF."""
        pdf_filename = "real_time_snapshots.pdf"
        pdf_writer = QPdfWriter(pdf_filename)
        pdf_writer.setPageSize(QPdfWriter.A4)
        pdf_writer.setResolution(300)
        pdf_writer.newPage()

        painter = QPainter(pdf_writer)
        painter.setFont(QFont("Arial", 10))

        for snapshot in self.snapshots:
            data = snapshot['data']
            timestamp = snapshot['timestamp']

            # Clear plot and render new data
            self.plot_widget.clear()
            self.plot_widget.plot(data, pen='b')

            # Resize plot widget to fit PDF page
            size = QSize(pdf_writer.width(), int(pdf_writer.height() * 0.6))
            self.plot_widget.resize(size)
            self.plot_widget.render(painter, QRect(0, 0, size.width(), size.height()))

            # Calculate statistics
            mean_val = np.mean(data)
            std_val = np.std(data)
            min_val = np.min(data)
            max_val = np.max(data)
            duration = len(data)

            # Add statistics table below the plot
            table_x = 50
            table_y = size.height() + 50

            painter.drawText(table_x, table_y, f"Snapshot Time: {timestamp:.2f} seconds")
            table_y += 30
            painter.drawText(table_x, table_y, f"Mean: {mean_val:.2f}")
            table_y += 20
            painter.drawText(table_x, table_y, f"Standard Deviation: {std_val:.2f}")
            table_y += 20
            painter.drawText(table_x, table_y, f"Min: {min_val:.2f}")
            table_y += 20
            painter.drawText(table_x, table_y, f"Max: {max_val:.2f}")
            table_y += 20
            painter.drawText(table_x, table_y, f"Duration: {duration} samples")

            if snapshot != self.snapshots[-1]:
                pdf_writer.newPage()

        painter.end()
        print(f"PDF saved as {pdf_filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimePlotApp()
    window.show()
    sys.exit(app.exec_())
