import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QWidget, QColorDialog, QLabel, QFileDialog, QSlider)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
import numpy as np
import random
import pandas as pd


class SubmarineRadar(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the main window and plot widget
        self.setWindowTitle("Enhanced Real-Time Submarine Radar")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")  # Dark theme

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked(True)  # To maintain circular aspect ratio
        self.plot_widget.setBackground('k')  # Radar background to black

        # Set radar limits (radius from 0 to 1000 units)
        self.plot_widget.setXRange(-1000, 1000)
        self.plot_widget.setYRange(-1000, 1000)

        # Main layout
        main_layout = QVBoxLayout()

        # Horizontal layout for the radar and buttons
        layout = QHBoxLayout()

        # Add the plot widget to the layout
        layout.addWidget(self.plot_widget)

        # Vertical layout for buttons on the right side
        button_layout = QVBoxLayout()

        # Style for buttons
        button_style = """
        QPushButton {
            background-color: #2a9d8f;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #2ec4b6;
        }
        QPushButton:pressed {
            background-color: #1b7f72;
        }
        """

        # Create the Toggle button for Start/Pause and make it square
        self.toggle_button = QPushButton("Start Radar")
        self.toggle_button.setFixedSize(100, 100)  # Square button
        self.toggle_button.setStyleSheet(button_style)
        self.toggle_button.clicked.connect(self.toggle_radar)
        button_layout.addWidget(self.toggle_button)

        # Create a button for changing the color of radar blips
        self.color_button = QPushButton("Change Color")
        self.color_button.setStyleSheet(button_style)
        self.color_button.clicked.connect(self.change_color)
        button_layout.addWidget(self.color_button)

        # Create a button for loading a CSV file
        self.load_button = QPushButton("Load CSV File")
        self.load_button.setStyleSheet(button_style)
        self.load_button.clicked.connect(self.load_csv)
        button_layout.addWidget(self.load_button)

        # Add a button for Cine-Mode
        self.cine_button = QPushButton("Start Cine-Mode")
        self.cine_button.setStyleSheet(button_style)
        self.cine_button.clicked.connect(self.toggle_cine_mode)
        button_layout.addWidget(self.cine_button)

        # Add a label for instructions
        self.info_label = QLabel("Click 'Change Color' to Customize Radar Points.")
        self.info_label.setStyleSheet("color: white; font-size: 12px;")
        button_layout.addWidget(self.info_label)

        # Slider for speed control in cine-mode
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 1000)  # 100ms to 1000ms
        self.speed_slider.setValue(500)  # Default 500ms
        self.speed_slider.valueChanged.connect(self.update_cine_speed)
        button_layout.addWidget(self.speed_slider)

        # Add the button layout (right side) to the horizontal layout
        layout.addLayout(button_layout)

        # Set the layout in a container widget
        container = QWidget()
        container.setLayout(layout)
        main_layout.addWidget(container)
        self.setCentralWidget(container)

        # Plot a static circle to visualize the maximum radar radius
        self.max_radius = 1000  # Maximum radius for the radar
        self.draw_static_circle(self.max_radius)

        # Scatter plot for blips (objects detected by radar)
        self.scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 0, 255))
        self.plot_widget.addItem(self.scatter)

        # Timer for updating the plot (real-time updates and cine-mode)
        self.timer = QTimer()
        self.timer.setInterval(100)  # Update interval in milliseconds
        self.timer.timeout.connect(self.update_display)

        self.num_objects = 10  # Number of objects to detect
        self.objects = []  # List of (r, theta) tuples representing objects

        # Initialize current_color with a default color
        self.current_color = (255, 255, 0, 255)  # Default color for radar blips

        # Track whether radar is running
        self.is_running = False
        self.cine_mode = False  # Track whether cine mode is active
        self.cine_index = 0  # Current index in cine-mode

        # Default CSV file path (change this to your desired default)
        self.default_csv_file_path = "file_of_signal/radarEXSheet1(1).csv"
        self.load_csv(self.default_csv_file_path)  # Load the default CSV on startup

        # Add mouse move event for displaying coordinates
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)

        # QLabel to display coordinates
        self.coord_label = QLabel("")
        self.coord_label.setStyleSheet("color: white; font-size: 14px;")
        button_layout.addWidget(self.coord_label)

        self.toggle_radar()  # Start the radar automatically

    def draw_static_circle(self, radius):
        """Draw a static circle representing the radar boundary."""
        theta = np.linspace(0, 2 * np.pi, 100)  # Angle from 0 to 2π
        x = radius * np.cos(theta)  # X coordinates of the circle
        y = radius * np.sin(theta)  # Y coordinates of the circle
        self.plot_widget.plot(x, y, pen=pg.mkPen('w', width=2))  # Plot the circle in white

    def generate_random_object(self):
        """Generate random object positions in polar coordinates (r, theta)."""
        radius = random.uniform(100, self.max_radius)  # Random radius between 100 and max_radius
        theta = random.uniform(0, 2 * np.pi)  # Random angle between 0 and 360 degrees
        return radius, theta

    def update_display(self):
        """Update the radar display. Handle both live updates and cine-mode."""
        if self.cine_mode:
            self.update_cine_mode()
        else:
            self.update_radar()

    def update_radar(self):
        """Update the radar by adding new objects and plotting them."""
        # Clear previous objects
        self.objects.clear()

        # Generate new objects
        for _ in range(self.num_objects):
            r, theta = self.generate_random_object()
            self.objects.append((r, theta))

        # Convert polar to Cartesian coordinates
        x_data = [r * np.cos(theta) for r, theta in self.objects]
        y_data = [r * np.sin(theta) for r, theta in self.objects]

        # Update the scatter plot with the new object positions
        spots = [{'pos': (x, y)} for x, y in zip(x_data, y_data)]
        self.scatter.setData(spots, brush=pg.mkBrush(*self.current_color))  # Use the current color for blips

    def update_cine_mode(self):
        """Update the radar display in cine-mode."""
        if self.cine_index < len(self.objects):
            r, theta = self.objects[self.cine_index]
            self.scatter.setData([{'pos': (r * np.cos(theta), r * np.sin(theta))}], brush=pg.mkBrush(*self.current_color))
            self.cine_index += 1
        else:
            self.cine_index = 0  # Reset to the first object if we reach the end

    def load_csv(self, file_name=None):
        """Load CSV data for r and theta."""
        if file_name is None:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                # Load the CSV file into a DataFrame
                data = pd.read_csv(file_name)

                # Clear previous objects
                self.objects.clear()

                # Ensure the CSV has the correct columns
                if 'r' in data.columns and 'theta' in data.columns:
                    for index, row in data.iterrows():
                        r = row['r']
                        theta = np.radians(row['theta'])  # Convert degrees to radians
                        self.objects.append((r, theta))

                    # Update the radar with the loaded objects
                    self.update_radar()
                else:
                    print("CSV must contain 'r' and 'theta' columns.")
            except Exception as e:
                print(f"Error loading CSV: {e}")

    # def load_default_csv(self):
    #     """Load the default CSV file on startup."""
    #     try:
    #         data = pd.read_csv(self.default_csv_file_path)
    #
    #         # Clear previous objects
    #         self.objects.clear()
    #
    #         # Ensure the CSV has the correct columns
    #         if 'r' in data.columns and 'theta' in data.columns:
    #             for index, row in data.iterrows():
    #                 r = row['r']
    #                 theta = np.radians(row['theta'])  # Convert degrees to radians
    #                 self.objects.append((r, theta))
    #
    #             # Update the radar with the loaded objects
    #             self.update_radar()
    #         else:
    #             print("CSV must contain 'r' and 'theta' columns.")
    #     except Exception as e:
    #         print(f"Error loading default CSV: {e}")

    def toggle_radar(self):
        """Start or pause the radar based on the current state."""
        if self.is_running:
            # Pause the radar
            self.timer.stop()
            self.toggle_button.setText("Start Radar")
        else:
            # Start the radar
            self.timer.start()
            self.toggle_button.setText("Pause Radar")

        # Toggle the running state
        self.is_running = not self.is_running

    def toggle_cine_mode(self):
        """Start or stop cine-mode based on the current state."""
        if self.cine_mode:
            # Stop cine mode
            self.cine_mode = False
            self.cine_button.setText("Start Cine-Mode")
            self.cine_index = 0  # Reset index
            self.scatter.setData([], brush=pg.mkBrush(*self.current_color))  # Clear blips
        else:
            # Start cine mode
            self.cine_mode = True
            self.cine_button.setText("Stop Cine-Mode")
            self.cine_index = 0  # Reset index to start from the beginning

    def update_cine_speed(self):
        """Update the cine-mode speed based on slider value."""
        speed = self.speed_slider.value()
        self.timer.setInterval(speed)

    def change_color(self):
        """Open a color picker dialog to change the color of the radar blips."""
        color = QColorDialog.getColor()

        if color.isValid():
            # Update the current color with the selected color
            self.current_color = (color.red(), color.green(), color.blue(), 255)

            # Apply the new color immediately to the scatter plot
            self.scatter.setBrush(pg.mkBrush(*self.current_color))  # Update the scatter plot color

    def mouse_moved(self, evt):
        """Handle mouse movement over the scatter plot to display coordinates."""
        if self.is_running:  # Only check coordinates if radar is paused
            return

        # Get mouse point
        pos = evt  # pos is a QPoint object

        if self.plot_widget.sceneBoundingRect().contains(pos):  # If mouse is within the plot area
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()

            # Calculate distance from the center to determine if mouse is near any object
            for index, (r, theta) in enumerate(self.objects):
                object_x = r * np.cos(theta)
                object_y = r * np.sin(theta)

                # Check if mouse is within a small radius of the object
                if np.sqrt((x - object_x) ** 2 + (y - object_y) ** 2) < 15:  # 15 pixels
                    # Update the label with the coordinates
                    self.coord_label.setText(f"r: {r:.2f} m, θ: {np.degrees(theta):.2f}°")
                    return

        # Clear label if no object is hovered
        self.coord_label.setText("")


def radar_window():
    radar_win = QApplication(sys.argv)
    window = SubmarineRadar()
    window.show()
    sys.exit(radar_win.exec_())


if __name__=="__main__":
    radar_window()

