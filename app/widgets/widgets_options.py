"""_summary_"""
from typing import Callable

from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QBoxLayout,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app import settings
from app.common import Common

# from app.settings import Settings

# TODO: Refactor and decouple from settings
#       Either DropDownWidget should be named something more specific
#       or it should be made more generic in terms of settings


class DropDownWidget(QWidget):  # pylint: disable=too-few-public-methods
    """Class for Buffertime widgets

    Args:
        QWidget (QWidget): Inherits from the QWidget class
    """

    def __init__(
        self,
        title: str,
        buffer: list[str],
        tooltip_text: str,
        fit_content: bool = False,
    ) -> None:
        """Initiates the widget with a ComboBox and Label

        Args:
            title (str): string added as the label for the combobox

        Returns:
            QHBoxLayout: Local layout with the combobox and label
        """

        # Creates the local layout for the class
        QWidget.__init__(self)
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Sets up a combobox
        self.combo_box = QComboBox()
        if not fit_content:
            self.combo_box.setFixedWidth(60)
        else:
            self.combo_box.setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToContents
            )

        self.combo_box.addItems(buffer)

        # Adds the combobox widget and label
        layout.addWidget(self.combo_box)
        layout.addWidget(add_label(title, tooltip_text))

        # saves label as a class variable for later use
        self.label = title

    def connect(self, slot: Callable[[int], None]) -> None:
        """Connects the index changed function to the slot

        Args:
            slot (Callable[[int], None]): function to be called when index is changed
        """
        self.combo_box.currentIndexChanged.connect(slot)

    def set_index(self, index: int) -> None:
        """Sets the index of the combobox

        Args:
            index (int): the new index of the combobox
        """
        self.combo_box.setCurrentIndex(index)


class AdvancedOptions(QWidget):
    """Class for Advanced option widget

    Args:
        QWidget (QWidget): Inherits from the QWidget class
    """

    options_open = False  # Variable for if the advanced options are open or not

    def __init__(self) -> None:
        """Initiates the widget with link to open  advanced options"""

        # Creates the local layout for the class
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.advanced_layout = QVBoxLayout()
        self.advanced_layout_horizontal_checkboxes = QHBoxLayout()
        self.advanced_layout_horizontal_dropdown_spinbox = QHBoxLayout()
        self.advanced_layout_horizontal_3 = QHBoxLayout()

        self.setLayout(layout)

        # Adds a clickable label
        self.label = QLabel()
        self.text = "<a href='#'>Advanced Options</a>"
        self.label.setText(self.text)
        self.label.setFont(
            QtGui.QFont("Arial", weight=QtGui.QFont.Weight.Bold, pointSize=10)
        )
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.setStyleSheet(
            """QToolTip { color: #000000; background-color: #ffffff; border: 1px solid white; }"""
        )
        self.label.setToolTip("Click to show advanced options")

        # Adds function to clickable link
        self.label.linkActivated.connect(self.show_options)

        # Adds widgets to the layout
        layout.addWidget(self.label)
        layout.addLayout(self.advanced_layout_horizontal_checkboxes)
        layout.addLayout(self.advanced_layout_horizontal_dropdown_spinbox)
        layout.addLayout(self.advanced_layout_horizontal_3)
        layout.addLayout(self.advanced_layout)

    def show_options(self) -> None:
        """Shows or removes the advanced options"""

        # Checks if the advanced options are open or not
        if self.options_open is False:
            # If not open, then it shows the advanced options
            self.advanced_options()
            self.options_open = True

        else:
            # If it is open, then the advanced options are removed from view
            self.clear_layout(self.advanced_layout)
            self.clear_layout(self.advanced_layout_horizontal_checkboxes)
            self.clear_layout(self.advanced_layout_horizontal_dropdown_spinbox)
            self.clear_layout(self.advanced_layout_horizontal_3)
            self.options_open = False

    def advanced_options(self) -> None:
        """Sets up the advanced options"""

        get_report_cb = Checkbox("Get Report", "Whether to get a report or not")
        get_report_cb.set_check_state(settings.get_report)

        def on_get_report_changed(state: bool) -> None:
            settings.get_report = state

        get_report_cb.connect(on_get_report_changed)
        self.advanced_layout_horizontal_checkboxes.addWidget(get_report_cb)

        box_around_fish_cb = Checkbox(
            "Box Around Fish Detected",
            "Will place a box around the fish detected in the video "
            + "including the confidence level and label",
        )
        box_around_fish_cb.set_check_state(settings.box_around_fish)

        def on_box_around_fish_changed(state: bool) -> None:
            settings.box_around_fish = state

        box_around_fish_cb.connect(on_box_around_fish_changed)
        self.advanced_layout_horizontal_checkboxes.addWidget(box_around_fish_cb)

        report_format_dd = DropDownWidget(
            "Report Format", Common.formats, "What format the report should be in"
        )
        report_format_dd.set_index(Common.formats.index(settings.report_format))

        def on_report_format_changed(index: int) -> None:
            settings.report_format = Common.formats[index]

        report_format_dd.connect(on_report_format_changed)

        self.advanced_layout_horizontal_dropdown_spinbox.addWidget(report_format_dd)

        batch_size_dd = DropDownWidget(
            "Batch Size",
            Common.batch_size,
            "Only for experienced IT (AI) users. \nHow many frames should be processed at once",
        )

        batch_size_dd.set_index(Common.batch_size.index(str(settings.batch_size)))

        def on_batch_size_changed(index: int) -> None:
            settings.batch_size = int(Common.batch_size[index])

        batch_size_dd.connect(on_batch_size_changed)

        self.advanced_layout_horizontal_dropdown_spinbox.addWidget(batch_size_dd)
        prediction_tooltip = (
            "The prediction thres"
            "hold determines the "
            "minimum confidence l"
            "evel required for a "
            "prediction to be con"
            "sidered valid.\r\n"
            "A higher threshold m"
            "eans that only predi"
            "ctions with a high c"
            "onfidence level will"
            " be accepted, reduci"
            "ng the number of pre"
            "dictions and potenti"
            "al false positives."
            "\r\n"
            "A lower threshold in"
            "cludes predictions w"
            "ith lower confidence"
            " levels, resulting i"
            "n more predictions b"
            "ut also a possibilit"
            "y of more false posi"
            "tives."
        )

        threshold_spinbox = SpinBox(
            "Prediction Threshold",
            0,
            100,
            settings.prediction_threshold,
            prediction_tooltip,
        )
        threshold_spinbox.set_suffix("%")

        def on_threshold_changed(value: int) -> None:
            settings.prediction_threshold = value

        threshold_spinbox.connect(on_threshold_changed)
        self.advanced_layout_horizontal_dropdown_spinbox.addWidget(threshold_spinbox)

        self.__populate_advanced_layout_horizontal_3()

    def __populate_advanced_layout_horizontal_3(self) -> None:
        crf_slider = Slider(
            "CRF",
            0,
            51,
            settings.video_crf,
            """Constant Rate Factor (CRF) is a quality control option for the H.264 codec.
The CRF value chosen determines the output video bitrate (quality).
The available range is 0–51 (0 is lossless, 51 is worst quality possible, default is 23)""",
        )

        def on_crf_slider_changed(value: int) -> None:
            settings.video_crf = value

        crf_slider.connect(on_crf_slider_changed)
        self.advanced_layout_horizontal_3.addWidget(crf_slider)

        max_detections_spinbox = SpinBox(
            "Max Detections",
            1,
            300,
            settings.max_detections,
            """The maximum number of detections to include per frame.
Reducing this number will improve performance when there are a lot of fish frames.""",
        )

        def on_max_detections_changed(value: int) -> None:
            settings.max_detections = value

        max_detections_spinbox.connect(on_max_detections_changed)
        self.advanced_layout_horizontal_3.addWidget(max_detections_spinbox)

        frame_buffer_spinbox = SpinBox(
            "Frame Gap Tolerance (S)",
            0,
            10,
            settings.frame_buffer_seconds,
            "The maximum allowed gap (in seconds) between frames without detections "
            + "within a valid range. Frames beyond this gap will be considered as a new range.",
        )

        def on_frame_buffer_changed(value: int) -> None:
            settings.frame_buffer_seconds = value

        frame_buffer_spinbox.connect(on_frame_buffer_changed)
        self.advanced_layout_horizontal_3.addWidget(frame_buffer_spinbox)

    def clear_layout(self, layout: QBoxLayout) -> None:
        """Removes all of the advanced options

        Args:
            layout (QHBoxLayout): the local layout that is to be cleared
        """
        if layout is None:  # Checks if the layout is empty
            return

        # Iterates through the items in the layout to delete them
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_layout(item.layout())


class Checkbox(QWidget):  # pylint: disable=too-few-public-methods
    """Class for Checkbox widget"""

    def __init__(self, msg: str, tooltip_text: str) -> None:
        """Sets up a checkbox

        Returns:
            QHBoxLayout: local layout for the checkbox and label
        """

        # Creates the local layout
        QWidget.__init__(self)
        layout = QHBoxLayout()

        # Sets up the checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setCheckState(Qt.CheckState.Unchecked)
        self.checkbox.setFixedWidth(20)

        # Adds widgets to layout
        layout.addWidget(self.checkbox)
        layout.addWidget(add_label(msg, tooltip_text))
        self.setToolTip(tooltip_text)

        self.setLayout(layout)

    def set_check_state(self, state: bool) -> None:
        """Sets the check state of the checkbox

        Args:
            state (Qt.CheckState): the state to set the checkbox to
        """
        qt_state = Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
        self.checkbox.setCheckState(qt_state)

    def connect(self, slot: Callable[[bool], None]) -> None:
        """Connects the checkbox 'toggled' to a function

        Args:
            function (Callable): the function to connect to
        """
        self.checkbox.toggled.connect(lambda: slot(self.checkbox.isChecked()))


class Slider(QWidget):
    """Class for Slider widget"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        msg: str,
        min_val: int,
        max_val: int,
        default_value: int,
        tooltip_text: str,
    ) -> None:
        QWidget.__init__(self)

        # Create a vertical layout for the widget
        layout = QVBoxLayout()

        # Create a horizontal layout for the slider and the label showing the value
        slider_layout = QHBoxLayout()

        # Create the slider widget
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(min_val, max_val)
        self.slider.setTickInterval(1)
        self.slider.setFixedWidth(200)
        self.slider.setSingleStep(1)
        self.slider.setValue(default_value)
        self.slider.setPageStep(1)

        # Create the label showing the value and add it to the slider layout
        self.label = QLabel(str(default_value), self)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.label)

        # Add the slider layout and the label with tooltip to the vertical layout
        layout.addWidget(add_label(msg, tooltip_text))
        layout.addLayout(slider_layout)

        self.slider.valueChanged.connect(self.update_label)

        self.setLayout(layout)

    def update_label(self, value: int) -> None:
        """Updates the label text when the slider value changes"""
        self.label.setText(str(value))

    def connect(self, slot: Callable[[int], None]) -> None:
        """Connects the slider 'valueChanged' to a function

        Args:
            function (Callable): the function to connect to
        """
        self.slider.valueChanged.connect(lambda: slot(self.slider.value()))


class SpinBox(QWidget):  # pylint: disable=too-few-public-methods
    """Class for SpinBox widget"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        msg: str,
        min_val: int,
        max_val: int,
        default_value: int,
        tooltip_text: str,
    ) -> None:
        """Sets up a spinbox for 'batch size' option

        Args:
            msg (str): the message to be displayed
            min_val (int): the minimum value for the spinbox
            max_val (int): the maximum value for the spinbox
            tooltil_text (str): a string with explaination of the label

        Returns:
            QHBoxLayout: local layout for the spinbox and label
        """

        # Creates the local layout
        QWidget.__init__(self)
        layout = QHBoxLayout()

        # Sets up the spinbox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(min_val, max_val)

        self.spinbox.setFixedWidth(50)

        self.spinbox.setValue(default_value)

        # Adds widgets to layout
        layout.addWidget(self.spinbox)
        layout.addWidget(add_label(msg, tooltip_text))

        self.setLayout(layout)

    def set_suffix(self, suffix: str) -> None:
        """Sets the suffix of the spinbox

        Args:
            suffix (str): the suffix to set the spinbox to
        """
        self.spinbox.setSuffix(suffix)

    def connect(self, slot: Callable[[int], None]) -> None:
        """Connects the spinbox 'valueChanged' to a function

        Args:
            function (Callable): the function to connect to
        """
        self.spinbox.valueChanged.connect(lambda: slot(self.spinbox.value()))


def add_label(title: str, tooltip_text: str) -> QLabel:
    """Creates a label

    Args:
        title (str): a string with the content of the label
        tooltil_text (str): a string with explaination of the label

    Returns:
        QLabel: The label with a standard font and text size
    """
    label = QLabel()
    label.setText(title)
    label.setToolTip(tooltip_text)
    label.setFont(QtGui.QFont("Arial", weight=QtGui.QFont.Weight.Bold, pointSize=10))
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    label.setStyleSheet(
        """QToolTip { color: #000000; background-color: #ffffff; border: 1px solid white; }"""
    )
    return label
