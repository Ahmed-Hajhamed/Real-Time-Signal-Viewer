import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class BTCPricePlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Live BTC Price Plot")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and a layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create a PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.x_data = []
        self.y_data = []


        self.curve = self.plot_widget.plot(pen='b')


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def fetch_btc_price(self):
        """Fetch the current BTC price from Binance."""
        try:
            response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            data = response.json()
            price = float(data['price'])
            return price
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None

    def update_plot(self):

        price = self.fetch_btc_price()
        if price is not None:

            self.x_data.append(self.x_data[-1] + 1 if len(self.x_data) > 0 else 0)

            self.y_data.append(price)


            self.curve.setData(self.x_data, self.y_data)
            self.plot_widget.setLabel('left', 'BTC Price', units='US $')
            self.plot_widget.setLabel('bottom', 'time ', units='sec')
            if len(self.x_data) > 60:
                self.x_data.pop(0)
                self.y_data.pop(0)

            self.plot_widget.setXRange(max(0, len(self.x_data) - self.x_data[-1]), self.x_data[-1])
            self.plot_widget.setYRange(min(self.y_data), max(self.y_data))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BTCPricePlotter()
    window.show()
    sys.exit(app.exec_())
