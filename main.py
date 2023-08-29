import sys
import re
from adapter_config import get_adapters, get_adapters_name, get_adapter, set_selected_adapter, ChangeIP
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QVBoxLayout, QWidget, \
    QFormLayout, QRadioButton, QMessageBox


class MainWindow(QMainWindow):
    selected_adapter_caption = ''
    isDHCP = False
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Change IP - Radar Connect")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Dropdown and Refresh Button
        self.dropdown_label = QLabel("Choose:")
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        self.dropdown.currentIndexChanged.connect(self.on_dropdown_change)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)

        # Radio Buttons
        radio_label = QLabel("Select:")
        self.radio1 = QRadioButton("DHCP")
        self.radio1.toggled.connect(self.on_radio_changed)
        self.radio2 = QRadioButton("Static")
        self.radio2.toggled.connect(self.on_radio_changed)

        # Create a layout for the radio buttons
        self.radio_layout = QVBoxLayout()
        self.radio_layout.addWidget(self.radio1)
        self.radio_layout.addWidget(self.radio2)

        # Input Fields with Labels
        input_label = QLabel("Edit static IP:")
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
        self.submit_button = QPushButton("Change")
        self.submit_button.clicked.connect(self.submit_form)

        # Set up the main layout
        main_layout.addWidget(self.dropdown_label)
        main_layout.addWidget(self.dropdown)
        main_layout.addWidget(self.refresh_button)

        main_layout.addWidget(radio_label)
        main_layout.addLayout(self.radio_layout)

        self.form_layout = QFormLayout()
        self.form_layout.addRow(input_label)
        for label, input_field in zip(self.input_labels, self.input_fields):
            self.form_layout.addRow(label, input_field)
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(self.submit_button)

        self.radio1.toggle()
        self.refresh_data()

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
    window.show()
    sys.exit(app.exec_())
