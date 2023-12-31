"""
    This file contains the UI tests for the app.
    """
import sys
import unittest

from PyQt6.QtCore import QEventLoop, qCritical  # , Qt

# from ..globals import Globals
from PyQt6.QtWidgets import QApplication

# import pytest
from app.main import MainWindow
from app.widgets.file_browser import FileBrowser

# import app.widgets.options_widgets as options_widgets
from app.widgets.widgets_options import (
    AdvancedOptions,
    Checkbox,
    DropDownWidget,
    add_label,
)

# from pytestqt.qtbot import QtBot

# from PyQt6.QtTest import QTest


# class TestUI(MainWindow):
class TestUI(unittest.TestCase):
    """Class for testing the UI

    Args:
        unittest (unittest.TestCase): Inherits from the unittest.TestCase class
    """

    def setUp(self) -> None:
        """Sets up the app for testing"""
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.drop_down = DropDownWidget("Test", (["1", "2", "3"]), "test")
        self.advanced = AdvancedOptions()
        self.checkbox = Checkbox("Test", "test")
        self.file_browser = FileBrowser("Test", "test")

    def test_main_window(self) -> None:
        """Tests the main window"""
        self.window.show()
        app = QApplication.instance()
        loop = QEventLoop()
        window = self.window.windowHandle()
        window.windowStateChanged.connect(loop.quit)
        app.processEvents()
        while not self.window.isVisible():
            app.processEvents()
        # loop.exec()
        self.assertTrue(self.window.isVisible())

    def test_run_button(self) -> None:
        """_summary_"""
        # qtbot = QtBot
        # qtbot.mouseClick(self.window.run_btn, Qt.MouseButton.LeftButton)
        # QTest.mouseClick(self.window.run_btn, Qt.MouseButton.LeftButton)
        assert self.window.run_btn.text() == "Run"
        # self.assertEqual(self.window.run_btn.text(), "Running...")
        qCritical("Test")

    def test_default_values(self) -> None:
        """Tests the default values"""
        # self.assertEqual(self.window.dir_fb, "")
        self.assertEqual(self.drop_down.label, "Test")
        self.assertEqual(self.file_browser.label, "Test")
        self.assertEqual(self.advanced.text, "<a href='#'>Advanced Options</a>")
        self.assertEqual(self.checkbox.checkbox.isChecked(), True)
        all_buffer_times = [
            self.drop_down.combo_box.itemText(i)
            for i in range(self.drop_down.combo_box.count())
        ]
        self.assertEqual(all_buffer_times, ["1", "2", "3"])

        # self.assertEqual(self.checkbox., ["1", "2", "3"])

    def test_drop_down_widget(self) -> None:
        """Tests the drop down widget"""
        widget = DropDownWidget("Test", ["1", "2", "3"], "test")
        self.window.show()
        # qtbot = QtBot
        # qtbot.waitExposed(widget)
        # QTest.qWaitForWindowExposed(widget)
        self.window.layout().addWidget(widget)
        self.assertTrue(widget.isVisible())

    def test_add_label(self) -> None:
        """Tests the add_label function"""
        widget = add_label("Test", "test")
        self.window.show()
        # QTest.qWaitForWindowExposed(self.window.windowHandle())
        self.window.layout().addWidget(widget)
        # self.assertTrue(widget.isVisible())

    # def test_add_checkbox(self) -> None:
    #    """Tests the add_checkbox function"""
    #    widget = Checkbox("Test")
    #    self.window.show()
    #    QTest.qWaitForWindowExposed(self.window)
    #    self.window.layout().addWidget(widget)
    #    self.assertTrue(widget.isVisible())

    # def test_add_line_edit(self) -> None:
    #    """Tests the add_line_edit function"""
    #    widget = add_line_edit("Test")
    #    self.window.show()
    #    QTest.qWaitForWindowExposed(self.window)
    #    self.window.layout().addWidget(widget)
    #    self.assertTrue(widget.isVisible())

    # def test_add_button(self) -> None:
    #    """Tests the add_button function"""
    #    widget = add_button("Test")
    #    self.window.show()
    #    QTest.qWaitForWindowExposed(self.window)
    #    self.window.layout().addWidget(widget)
    #    self.assertTrue(widget.isVisible())

    # def test_add_slider(self) -> None:
    #    """Tests the add_slider function"""
    #    widget = add_slider("Test")
    #    self.window.show()
    #    QTest.qWaitForWindowExposed(self.window)
    #    self.window.layout().addWidget(widget)
    #    self.assertTrue(widget.isVisible())

    # def test_add_spinbox(self) -> None:
    #    """Tests the add_spinbox function"""
    #    widget = add_spinbox("Test")
    #    self.window.show()
    #    QTest.qWaitForWindowExposed

    def tearDown(self) -> None:
        """Clean up the test"""
        self.window.close()
        del self.window
        del self.app


if __name__ == "__main__":
    unittest.main()
