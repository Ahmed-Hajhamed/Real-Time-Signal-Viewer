import sys
from graph import Graph, set_icon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFrame)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi signal plotter")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        v_layout = QVBoxLayout()

        self.graph_1 = Graph()
        self.graph_2 = Graph()

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

        self.graph_1.move_to_another_graph_button.setText("Move Down")
        self.graph_2.move_to_another_graph_button.setText("Move Up")

        h_layout_connect_buttons = QHBoxLayout()

        self.button_linked_graph = QPushButton()
        set_icon(self.button_linked_graph, "icons/unlink.png")
        self.button_linked_graph.setToolTip("link button")
        h_layout_connect_buttons.addWidget(self.button_linked_graph)

        self.zoom_in_connect_graphs = QPushButton()
        set_icon(self.zoom_in_connect_graphs, "icons/zoom in.png")
        self.zoom_in_connect_graphs.setEnabled(False)
        h_layout_connect_buttons.addWidget(self.zoom_in_connect_graphs)

        self.zoom_out_connect_graphs = QPushButton()
        set_icon(self.zoom_out_connect_graphs, "icons/zoom out.png")
        self.zoom_out_connect_graphs.setEnabled(False)
        h_layout_connect_buttons.addWidget(self.zoom_out_connect_graphs)

        self.play_pause_button = QPushButton()
        set_icon(self.play_pause_button, "icons/play.png")
        self.play_pause_button.setEnabled(False)
        h_layout_connect_buttons.addWidget(self.play_pause_button)

        self.speed_button= QPushButton("1X")
        self.speed_button.setEnabled(False)
        self.speed_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.speed_button)

        self.view_all_button = QPushButton("View All")
        self.view_all_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.view_all_button)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setStyleSheet("QFrame { background-color: #2a9d8f; height: 2px; }")
        h_layout_connect_buttons.addWidget(self.separator)

        self.glue_button = QPushButton("Glue")
        self.glue_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.glue_button)

        self.open_radar_button = QPushButton("Radar")
        self.open_radar_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.open_radar_button)

        self.Create_pdf_button = QPushButton("Create PDF")
        self.Create_pdf_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.Create_pdf_button)

        self.open_online_signal_button = QPushButton("Online Signal")
        self.open_online_signal_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.open_online_signal_button)

        container = QWidget()

        v_layout.addLayout(self.graph_1.h_layout)

        v_layout.addLayout(h_layout_connect_buttons)

        v_layout.addLayout(self.graph_2.h_layout)

        container.setLayout(v_layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())