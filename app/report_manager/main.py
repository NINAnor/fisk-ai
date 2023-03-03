"""report manager"""
from app.data_manager.data_manager import DataManager
from .report_manager import ReportManager


def main() -> int:
    """Main entry point for the application script"""

    datamanager = DataManager()
    # datamanager.create_table()
    # datamanager.create_tables()
    # datamanager.add_video_data(3, "test", "2023-02-23", "30:00:00")
    # datamanager.add_detection_data(
    #    3,
    #    [
    #        ("12:00:00", "13:00:00"),
    #        ("12:00:00", "13:00:00"),
    #        ("12:00:00", "13:00:00"),
    #        ("12:00:00", "13:00:00"),
    #    ],
    # )
    # datamanager.get_detection_data()

    report = ReportManager(
        "C:/Users/lilli/Documents/hello", "C:/Users/lilli/Documents/hello", datamanager
    )
    report.write_csv_file()
    report.write_xml_file()
    report.write_pdf_file()
    # report2 = ReportManager("csv", "C:/Users/lilli/Documents/hello")
    # report3 = ReportManager("PDF", "C:/Users/lilli/Documents/hello")
    datamanager.close_connection()
    return 0
