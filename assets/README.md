Signal Viewer Application

Overview

The Signal Viewer application is a powerful desktop tool for displaying and interacting with multi-channel signals. It offers advanced features for visualization, manipulation, and analysis of signals, including real-time signal display and PDF report generation.

Features

1. Multi-Channel Signal Display

Supports 2 channels.

Each channel can display multiple signals simultaneously.

2. Signal Interaction Options

For each signal, you can:

Change its color.

Hide or unhide the signal.

Control the display speed.

Pause, start, and rewind the signal.

Zoom in and out.

Link signals from both channels to run synchronously.

3. Signal Merging

Combine part of a signal from Channel 1 with part of a signal from Channel 2 to create a new glued signal.

4. PDF Report Generation

Generate a PDF report showing the minimum, maximum, and standard deviation of the signals.

5. Non-Rectangular Signal Display

Visualize non-rectangular signals, such as radar signals.

6. Real-Time Signal Display

Display real-time signals using any API.

Example: Visualizing Bitcoin price in real time.

How to Use

Load Signals: Add signals to the desired channel for display.

Interact with Signals: Use the interactive controls to customize the display.

Merge Signals: Select parts from different channels to glue them together.

Generate Reports: Export signal statistics as a PDF.

Real-Time Signals: Connect to an API and view live signal data.

Screenshots/GIFs

Application Preview:

![Main Window](assets/main_window.gif)

Installation

Clone the repository:

git clone <repository_url>

Navigate to the project directory:

cd signal-viewer

Install the required dependencies:

pip install -r requirements.txt

Run the application:

python main.py

Dependencies

Python 3.7+

PyQt5

Matplotlib

ReportLab

Install all dependencies using:

pip install -r requirements.txt

Contribution

Feel free to fork the repository and submit pull requests. Contributions are welcome!

License

This project is licensed under the MIT License.

Contact

For questions or suggestions, contact [Your Email/Your Name].