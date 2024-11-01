import os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from ui import MainWindow
from graph import set_icon
from GluedGraph import GlueWindow
from cineModeRadar import SubmarineRadar
from reportlab.lib.pagesizes import letter
from online import BTCPricePlotter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image
from reportlab.lib import colors


class App(MainWindow):
    def __init__(self):
        super().__init__()

        self.radar_win = None
        self.glue_window_object = None
        self.connected_graphs = False
        self.connected_graphs_toggle = False

        self.graph_1.move_to_another_graph_button.clicked.connect(
            lambda: self.graph_1.move_to_another_graph(self.graph_2))

        self.graph_2.move_to_another_graph_button.clicked.connect(
            lambda: self.graph_2.move_to_another_graph(self.graph_1))

        self.button_linked_graph.clicked.connect(self.linked_graph)

        self.zoom_in_connect_graphs.clicked.connect(self.zoom_in_graphs)
        self.zoom_in_connect_graphs.setEnabled(False)

        self.zoom_out_connect_graphs.clicked.connect(self.zoom_out_graphs)
        self.zoom_out_connect_graphs.setEnabled(False)

        self.play_pause_button.clicked.connect(self.play_pause_graphs)
        self.play_pause_button.setEnabled(False)

        self.glue_button.clicked.connect(self.glue_window)

        self.open_radar_button.clicked.connect(self.radar_window)

        self.Create_pdf_button.clicked.connect(self.create_pdf)

        self.open_online_signal_button.clicked.connect(self.online_signal_window)

    def radar_window(self):
        self.radar_win = SubmarineRadar()
        self.radar_win.show()

    def online_signal_window(self):
        self.online_signal_win = BTCPricePlotter()
        self.online_signal_win.show()

    def glue_window(self):
        if self.graph_1.selected_data and self.graph_2.selected_data:
            self.glue_window_object = GlueWindow(self.graph_1.selected_data, self.graph_2.selected_data)
            self.glue_window_object.show()
            self.graph_1.plot_widget.region.setVisible(False)
            self.graph_2.plot_widget.region.setVisible(False)

    def linked_graph(self):
        if not self.connected_graphs:
            if self.graph_1.current_index < self.graph_2.current_index:
                self.graph_2.current_index = self.graph_1.current_index
            else:
                self.graph_1.current_index = self.graph_2.current_index

            set_icon(self.button_linked_graph, "icons/link.png")
            self.graph_1.set_plot_limits()
            self.graph_2.set_plot_limits()
            self.zoom_in_connect_graphs.setEnabled(True)
            self.zoom_out_connect_graphs.setEnabled(True)
            self.play_pause_button.setEnabled(True)
            self.graph_1.zoom_in_button.setEnabled(False)
            self.graph_2.zoom_in_button.setEnabled(False)
            self.graph_1.zoom_out_button.setEnabled(False)
            self.graph_2.zoom_out_button.setEnabled(False)
            self.graph_1.play_pause_button.setEnabled(False)
            self.graph_2.play_pause_button.setEnabled(False)

        else:

            set_icon(self.button_linked_graph, "icons/unlink.png")
            self.graph_1.set_plot_limits()
            self.graph_2.set_plot_limits()
            self.zoom_in_connect_graphs.setEnabled(False)
            self.zoom_out_connect_graphs.setEnabled(False)
            self.play_pause_button.setEnabled(False)
            self.graph_1.zoom_in_button.setEnabled(True)
            self.graph_2.zoom_in_button.setEnabled(True)
            self.graph_1.zoom_out_button.setEnabled(True)
            self.graph_2.zoom_out_button.setEnabled(True)
            self.graph_1.play_pause_button.setEnabled(True)
            self.graph_2.play_pause_button.setEnabled(True)

        self.connected_graphs = not self.connected_graphs

    def zoom_in_graphs(self):
        self.graph_1.zoom_in()
        self.graph_2.zoom_in()

    def zoom_out_graphs(self):
        self.graph_1.zoom_out()
        self.graph_2.zoom_out()

    def play_pause_graphs(self):

        self.graph_1.play_pause_signal()
        self.graph_2.play_pause_signal()
        if self.connected_graphs_toggle:
            set_icon(self.play_pause_button, "icons/pause.png")
        else:
            set_icon(self.play_pause_button, "icons/play.png")

        self.connected_graphs_toggle = not self.connected_graphs_toggle

    def create_pdf(self):
        pdf_filename = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")[0]
        if pdf_filename:
            pdf = SimpleDocTemplate(pdf_filename, pagesize=letter,
                                    rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)

            elements = []

            logo1 = Image('logo 1.png', width=100, height=100)
            logo2 = Image('logo 2.png', width=100, height=100)

            logo_table_data = [[logo1, Spacer(10, 10), logo2]]  # Adding some space between logos
            logo_table = Table(logo_table_data, colWidths=[100, 400, 100])  # Adjust colWidths if needed
            elements.append(logo_table)

            elements.append(Spacer(1, 20))  # Add space after the logos

            # Step 1: Add screenshots and statistics to PDF
            for stats in GlueWindow.statistics:
                # Add space between image name and image
                elements.append(Spacer(1, 25))

                # Add image
                image = Image(stats['filename'], width=400, height=300)
                elements.append(image)

                # Create table data for this specific image
                table_data = [
                    ['Statistic', 'Value'],  # Table header
                    ['Mean', f"{stats['mean']:.4f}"],
                    ['Std Dev', f"{stats['std_dev']:.2f}"],
                    ['Max', f"{stats['max_amp']:.2f}"],
                    ['Min', f"{stats['min_amp']:.2f}"],
                    ['Duration', f"{stats['duration']:.2f}"],
                ]

                # Step 3: Define table with specific column widths
                table = Table(table_data, colWidths=[100, 100])  # Adjust widths as needed

                # Step 4: Style the table
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(style)

                # Add space between image and table
                elements.append(Spacer(1, 100))  # Space of 12 units before the table
                # Add the table to the elements directly after the image
                elements.append(table)
                if stats["filename"][-5] == 1 or stats["filename"] == GlueWindow.statistics[-1]['filename']:
                    pass
                else:
                    elements.append(Spacer(1, 120))  # More space before the next entry

            # Step 6: Build the PDF
            pdf.build(elements)

            QMessageBox.information(self, "Success", "PDF saved successfully!")
            for stat in GlueWindow.statistics:
                os.remove(stat['filename'])
            GlueWindow.number_of_images = 0
            GlueWindow.statistics.clear()  # Clear statistics after saving


def main():
    app = QApplication(sys.argv)
    win = App()
    win.show()
    sys.exit(app.exec_())
