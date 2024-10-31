import sys
from graph import Graph, set_icon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton)


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

        self.graph_1.move_to_another_graph_button.setText("move down")
        self.graph_2.move_to_another_graph_button.setText("move up")

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
        set_icon(self.play_pause_button, "icons/pause.png")
        self.play_pause_button.setEnabled(False)
        h_layout_connect_buttons.addWidget(self.play_pause_button)

        self.glue_button = QPushButton("glue")
        self.glue_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.glue_button)

        self.open_radar_button = QPushButton("Radar")
        self.open_radar_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.open_radar_button)

        self.Create_pdf_button = QPushButton("Create PDF")
        self.Create_pdf_button.setStyleSheet(button_style)
        h_layout_connect_buttons.addWidget(self.Create_pdf_button)


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