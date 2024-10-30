import os
import pandas as pd
from statistics import median, mean, mode, stdev


class Signal:
    def __init__(self, plot_widget, color, name=None, x_data=None, y_data=None, csv_file=None, online=False):
        """Initialize a signal by loading data from a CSV file."""
        self.plot_widget = plot_widget
        self.color = color
        self.current_index = 0

        if csv_file is not None:
            self.csv_file = csv_file
            self.name = os.path.splitext(os.path.basename(csv_file))[0]
            self.load_data()
        else:
            self.x_data = x_data
            self.y_data = y_data
            self.name = name

        self.curve = self.plot_widget.plot(self.x_data[:1], self.y_data[:1], pen=self.color)

    def load_data(self):
        """Load signal data from a CSV file."""
        data = pd.read_csv(self.csv_file)

        # Assume first column is time and second column is signal data
        self.x_data = data.iloc[:, 0].values
        self.y_data = data.iloc[:, 1].values

    def update_plot(self, current_index):
        """Update the plot with new data based on the current index."""
        self.current_index = current_index
        if current_index < len(self.x_data):
            self.curve.setData(self.x_data[:current_index], self.y_data[:current_index])

    def get_signal(self, current_index):
        """Return the signal up to the current index for summing."""
        return self.y_data[:current_index] if current_index < len(self.y_data) else self.y_data

    def signal_statistics(self):
        duration = self.x_data[self.current_index]
        #mean, std_dev, max_amp, min_amp, duration
        return mean(self.y_data), stdev(self.y_data), self.y_data.max(), self.y_data.min(), duration
