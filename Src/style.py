
def get_stylesheet():
    return """
    /* Global Styles */
    QWidget {
        background-color: #2b2b2b;
        color: #e0e0e0;
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: 14px;
        selection-background-color: #3a4b58;
        selection-color: #ffffff;
    }

    /* QMainWindow */
    QMainWindow {
        background-color: #1e1e1e;
    }

    /* QGroupBox */
    QGroupBox {
        border: 1px solid #3e3e42;
        border-radius: 6px;
        margin-top: 24px;
        padding-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        color: #007acc;
        background-color: transparent;
    }

    /* QPushButton */
    QPushButton {
        background-color: #3e3e42;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px 12px;
        color: #ffffff;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #4e4e52;
        border-color: #007acc;
    }
    QPushButton:pressed {
        background-color: #007acc;
        border-color: #007acc;
    }
    QPushButton:disabled {
        background-color: #2d2d30;
        color: #6d6d6d;
        border-color: #3e3e42;
    }

    /* QLineEdit & QTextEdit */
    QLineEdit, QTextEdit {
        background-color: #1e1e1e;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 4px;
        color: #e0e0e0;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #007acc;
    }

    /* QListWidget */
    QListWidget {
        background-color: #1e1e1e;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 4px;
    }
    QListWidget::item {
        padding: 6px;
        border-radius: 2px;
    }
    QListWidget::item:selected {
        background-color: #3a4b58;
        color: #ffffff;
        border-left: 3px solid #007acc;
    }
    QListWidget::item:hover {
        background-color: #2a2d2e;
    }

    /* QTabWidget */
    QTabWidget::pane {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        background-color: #2b2b2b;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #2d2d30;
        color: #a0a0a0;
        border: 1px solid #3e3e42;
        border-bottom-color: #3e3e42;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 16px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #2b2b2b;
        color: #007acc;
        border-bottom-color: #2b2b2b;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background-color: #3e3e42;
        color: #ffffff;
    }

    /* QProgressBar */
    QProgressBar {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        text-align: center;
        background-color: #1e1e1e;
        color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #007acc;
        border-radius: 3px;
    }
    
    /* QRadioButton */
    QRadioButton {
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
    }
    QRadioButton::indicator:unchecked {
        border: 2px solid #555555;
        border-radius: 9px;
        background-color: transparent;
    }
    QRadioButton::indicator:unchecked:hover {
        border-color: #007acc;
    }
    QRadioButton::indicator:checked {
        border: 2px solid #007acc;
        border-radius: 9px;
        background-color: #007acc;
    }

    /* QScrollBar */
    QScrollBar:vertical {
        border: none;
        background: #1e1e1e;
        width: 12px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #424242;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #686868;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        border: none;
        background: #1e1e1e;
        height: 12px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:horizontal {
        background: #424242;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #686868;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    """
