import os
import sys
import re
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon

from adapter_config import get_adapters, get_adapters_name, get_adapter, set_selected_adapter, ChangeIP
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QVBoxLayout, QWidget, \
    QFormLayout, QRadioButton, QMessageBox, QDesktopWidget, QSizePolicy, QHBoxLayout, QSplitter

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class MainWindow(QMainWindow):
    selected_adapter_caption = ''
    isDHCP = False
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Change IP - Radar Connect")

        print(os.path.join(basedir, 'icons', 'minimize-window-32.png'))
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Minimize button
        self.min_button = QPushButton("")
        self.min_button.setIcon(QIcon(os.path.join(basedir, 'icons', 'minimize-window-32.png')))
        self.min_button.clicked.connect(self.showMinimized)
        self.min_button.setFixedSize(32, 32)

        # Close button
        self.close_button = QPushButton("")
        self.close_button.setIcon(QIcon(os.path.join(basedir, 'icons', 'cancel-32.png')))
        # self.close_button.setIconSize(QSize(200,200))
        self.close_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.close_button.setStyleSheet("padding: 2px 2px")
        self.close_button.clicked.connect(self.close_window)
        self.close_button.setFixedSize(32, 32)

        # Title Layout
        self.titleLayout = QHBoxLayout()
        self.title_label = QLabel("IP Changer")
        self.title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px;")

        self.titleLayout.addWidget(self.title_label)
        self.titleLayout.addWidget(self.min_button)
        self.titleLayout.addWidget(self.close_button)

        # Splitter
        self.splitter = QSplitter()
        self.splitter.setStyleSheet("background: red;")
        # Dropdown selected label
        self.dropdown_label = QLabel("Choose:")
        self.dropdown_label.setStyleSheet("margin-top: 10px;")
        self.dropdown_label.setWordWrap(True)

        # Dropdown
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        self.dropdown.currentIndexChanged.connect(self.on_dropdown_change)
        self.dropdown.setStyleSheet("padding: 8px 2px")
        # Refresh button
        self.refresh_button = QPushButton("")
        self.refresh_button.setIcon(QIcon(os.path.join(basedir, 'icons', 'refresh-32.png')))
        self.refresh_button.setFixedSize(32, 32)
        self.refresh_button.setStyleSheet("padding: 0px 0px")
        self.refresh_button.clicked.connect(self.refresh_data)

        # Dropdown Layout
        self.adapterSelectionLayout = QHBoxLayout()

        self.adapterSelectionLayout.addWidget(self.dropdown)
        self.adapterSelectionLayout.addWidget(self.refresh_button)

        # Radio Buttons
        self.radio_label = QLabel("Select:")
        self.radio1 = QRadioButton("DHCP")
        self.radio1.toggled.connect(self.on_radio_changed)
        self.radio2 = QRadioButton("Static")
        self.radio2.toggled.connect(self.on_radio_changed)

        # Create a layout for the radio buttons
        self.radio_layout = QHBoxLayout()
        self.radio_layout.addWidget(self.radio_label)
        self.radio_layout.addWidget(self.radio1)
        self.radio_layout.addWidget(self.radio2)

        # Input Fields with Labels
        input_label = QLabel("Static configuration:")
        self.input_labels = []
        self.input_fields = []
        self.default_options = ['192.168.1.11','255.255.255.0','192.168.1.1','8.8.8.8 - 8.8.4.4']
        self.input_labels_values = ['IP','Subnetmask','Gateway','DNS']
        for i in range(4):
            label = QLabel(f"{self.input_labels_values[i]}:")
            input_field = QLineEdit(f"{self.default_options[i]}")
            self.input_fields.append(input_field)
            self.input_labels.append(label)

        # Submit Button
        self.submit_button = QPushButton("Apply")
        self.submit_button.clicked.connect(self.submit_form)

        # Set up the main layout
        main_layout.addLayout(self.titleLayout)
        main_layout.addWidget(self.splitter)
        main_layout.addLayout(self.adapterSelectionLayout)

        main_layout.addLayout(self.radio_layout)

        self.form_layout = QFormLayout()
        self.form_layout.addRow(input_label)
        for label, input_field in zip(self.input_labels, self.input_fields):
            self.form_layout.addRow(label, input_field)
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(self.submit_button)

        self.radio1.toggle()
        self.refresh_data()
        self.center()
        self.oldPos = self.pos()
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    def on_dropdown_change(self, index):
        print('on_dropdown_change')
        selected_option = self.dropdown.currentText()
        val = 'None'
        if selected_option != '':
            val = (str(selected_option[0: 40]))
            if len(selected_option) > 40:
                val += '...'
        self.dropdown_label.setText(f"Selected: {val}")
        self.selected_adapter_caption = selected_option

        set_selected_adapter(self.get_selected_adapter())

    def close_window(self):
        self.close()

    def get_selected_adapter(self):
        return get_adapter(self.selected_adapter_caption)

    def refresh_data(self):
        # Add code here to refresh data
        print('refresh')
        get_adapters()

        self.change_dropdown_items(get_adapters_name())
        adapter = get_adapter(self.selected_adapter_caption)

        if adapter is None:
            return

        if adapter.DHCPEnabled:
            self.radio1.toggle()
        else:
            self.radio2.toggle()

    def show_popup(self, status):
        popup = QMessageBox()
        popup.setWindowTitle("Change IP Status")
        if status:
            popup.setText("Successfully changed!")
            popup.setIcon(QMessageBox.Information)
        else:
            popup.setText("Some error occurred.")
            popup.setIcon(QMessageBox.Warning)
        popup.exec_()
    def submit_form(self):
        print('update ip')
        static_options = []
        for field in self.input_fields:
            static_options.append(field.text())

        print(static_options)
        status = ChangeIP(self.isDHCP, static_options)
        self.show_popup(status)

    def on_radio_changed(self):
        print('on_radio_changed')
        option:QRadioButton = self.sender()
        if option.isChecked():
            if option.text() == 'DHCP':
                self.isDHCP = True
            else:
                self.isDHCP = False
            print(option.text())
            print(self.isDHCP)
            self.set_static_options_enabled()

    def set_static_options_enabled(self):
        print('set_static_options_enabled')
        if self.isDHCP:
            for field in self.input_fields:
                field.setDisabled(True)
        else:
            for field in self.input_fields:
                field.setDisabled(False)

    def change_dropdown_items(self, new_items):
        self.dropdown.clear()  # Clear existing items
        print('new_items: ', new_items)
        dropdown_items = []
        for item in new_items:
            regex = dropdown_labels_filter(item)
            ignore, name = regex[0]
            print('regex: ', regex)
            if(len(regex[0]) > 1):
                print('regex: ', name)
                dropdown_items.append(name)
            else:
                dropdown_items.append(item)
        self.dropdown.addItems(dropdown_items)  # Add new items


def dropdown_labels_filter(input_text):
    found = re.findall(r"^(\[[^\]]+\])?(.*)$", input_text)
    return found

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint )
    styles_path = os.path.join(basedir, 'styles', 'style.qss')
    with open(styles_path, "r") as fh:
        window.setStyleSheet(fh.read())

    window.setWindowIcon(QIcon(os.path.join(basedir, 'icons', 'app-icon.png')))
    window.show()
    sys.exit(app.exec_())
