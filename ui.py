"""To modify only the Json Value."""
# %% Import
# Standard library imports
import sys
from typing import Tuple

# Third party imports
import qdarkstyle
from PyQt5.Qsci import QsciLexerJSON, QsciScintilla
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QFont, QKeyEvent, QKeySequence, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow

# Local imports
from json_infos import ContainerLineInfo, ValueKind


class JsonValueEditor(QsciScintilla):
    """."""

    def __init__(self, json_str: str, parent=None):
        """."""
        super().__init__(parent)
        json_lexer = QsciLexerJSON(self)

        # Dark Color setting
        default_c = "#c0c9e9"
        json_lexer.setDefaultPaper(QColor("#1a1b26"))
        json_lexer.setColor(QColor(default_c), 0)  # Default
        json_lexer.setColor(QColor("#e39d64"), 1)  # Number
        json_lexer.setColor(QColor("#9ece6a"), 2)  # String
        json_lexer.setColor(QColor(default_c), 3)  # Unclosed String
        json_lexer.setColor(QColor("#7aa2f7"), 4)  # Property
        json_lexer.setColor(QColor(default_c), 5)  # EscapeSequnece
        json_lexer.setColor(QColor(default_c), 6)  # CommentLine
        json_lexer.setColor(QColor(default_c), 7)  # CommentBlock
        json_lexer.setColor(QColor(default_c), 8)  # Operator (parenthesis)
        json_lexer.setColor(QColor(default_c), 9)  # IRI
        json_lexer.setColor(QColor(default_c), 10)  # IRICompact
        json_lexer.setColor(QColor(default_c), 11)  # Keyword
        json_lexer.setColor(QColor(default_c), 12)  # KeywordLD
        json_lexer.setPaper(QColor("#db4b4b"), 13)  # Error
        json_lexer.setColor(QColor("#4bdbdb"), 13)  # Error
        json_lexer.setFont(QFont("Courier new", 12))

        self.setCaretLineVisible(True)
        self.setCaretForegroundColor(QColor("#aaaaaa"))
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#272727"))
        # Color setting End

        self.setMargins(0)
        self.setLexer(json_lexer)
        self.line_infos = ContainerLineInfo(json_str)
        self.setText(self.line_infos.json_str)
        self.setCursorPosition(1, self.start_pos_of_value(1))

        self.mouse_clicked = False

    def start_pos_of_value(self, line_no: int) -> int:
        """Return the starting position of Value in the line."""
        return self.line_infos.start_pos_of_value(line_no)

    def end_pos_of_value(self, line_no: int) -> int:
        """Return the ending position of Value in the line."""
        line = self.text(line_no)
        return self.line_infos.end_pos_of_value(line_no, line)

    def pos_of_value(self, line_no: int) -> Tuple[int, int]:
        """Return the starting, ending position of Value in the line."""
        line = self.text(line_no)
        return self.line_infos.pos_of_value(line_no, line)

    def get_cusor_pos_from_qmousepos(self, point: QPoint) -> Tuple[int, int]:
        """Convert position of mouse to position of cursor."""
        pos = self.SendScintilla(self.SCI_POSITIONFROMPOINT, point.x(), point.y())
        line_no, col_no = self.lineIndexFromPosition(pos)
        return line_no, col_no

    def set_cursor_pos(self, line_no: int, pos_col: int):
        """Set cursor position."""
        start_pos_of_value, end_pos_of_value = self.pos_of_value(line_no)
        if start_pos_of_value > pos_col:
            pos_col = start_pos_of_value
        elif end_pos_of_value < pos_col:
            pos_col = end_pos_of_value

        self.setCursorPosition(line_no, pos_col)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        """Prevent select property of json."""
        line_no, pos_col = self.get_cusor_pos_from_qmousepos(e.pos())
        start_pos_of_value, end_pos_of_value = self.pos_of_value(line_no)

        if start_pos_of_value <= pos_col <= end_pos_of_value:
            self.mouse_clicked = True
            super().mousePressEvent(e)
        else:
            self.set_cursor_pos(line_no, pos_col)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        """Prevent select property of json."""
        self.mouse_clicked = False
        super().mouseReleaseEvent(e)
        self.validate_selection()

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        """Prevent select property of json."""
        line_no, pos_col = self.get_cusor_pos_from_qmousepos(e.pos())
        start_pos_of_value, end_pos_of_value = self.pos_of_value(line_no)

        if start_pos_of_value <= pos_col <= end_pos_of_value:
            super().mouseDoubleClickEvent(e)
            self.validate_selection()

    def get_post_char(self) -> str:
        """Get Character after cursor."""
        line_num, col_num = self.getCursorPosition()
        line = self.text(line_num)
        if len(line) - 1 < col_num:
            return ""
        else:
            return line[col_num]

    def get_prev_char(self) -> str:
        """Get Character before cursor."""
        line_num, col_num = self.getCursorPosition()
        line = self.text(line_num)
        if col_num < 1:
            return ""
        else:
            return line[col_num - 1]

    def validate_cursor_pos(self):
        """Validate the cursor position."""
        line_no, pos_col = self.getCursorPosition()
        start_col, end_col = self.pos_of_value(line_no)
        if pos_col < start_col:
            self.setCursorPosition(line_no, start_col)
        elif pos_col > end_col:
            self.setCursorPosition(line_no, end_col)

    def validate_selection(self):
        """Validate the selection."""
        line_no0, pos_sel_start, line_no1, pos_sel_end = self.getSelection()
        if line_no0 == -1:
            return

        if line_no0 != line_no1:
            self.setSelection(-1, -1, -1, -1)
            self.validate_cursor_pos()
            return

        line_no, pos_cursor = self.getCursorPosition()

        pos_start_of_value, pos_end_of_value = self.pos_of_value(line_no)
        pos_sel_start_new = pos_sel_start
        pos_sel_end_new = pos_sel_end

        if pos_start_of_value > pos_sel_start:
            pos_sel_start_new = pos_start_of_value
        if pos_end_of_value < pos_sel_end:
            pos_sel_end_new = pos_end_of_value

        if pos_cursor == pos_sel_start:
            pos_sel_end_new, pos_sel_start_new = pos_sel_start_new, pos_sel_end_new
        self.setSelection(line_no, pos_sel_start_new, line_no, pos_sel_end_new)

        # If Json value type is NUM_LIST and text_selected has comma, change selection.
        val_type = self.line_infos[line_no].val_type
        if val_type != ValueKind.NUM_LIST:
            return

        text_selected = self.selectedText()
        if "," not in text_selected:
            return

        line_no, pos_cursor = self.getCursorPosition()
        line_no0, pos_sel_start, line_no1, pos_sel_end = self.getSelection()
        line = self.text(line_no)
        if pos_cursor == pos_sel_start:
            pos_sel_start_new = line[:pos_sel_end].rfind(",") + 1
            self.setSelection(line_no, pos_sel_end, line_no, pos_sel_start_new)
        else:
            pos_sel_end_new = line[pos_sel_start:].find(",") + pos_sel_start
            self.setSelection(line_no, pos_sel_start, line_no, pos_sel_end_new)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        """Process key event."""
        line_no, _ = self.getCursorPosition()
        chars_allowed = self.line_infos[line_no].chars_allowed

        key = e.key()
        if key == Qt.Key_Space:
            key_char = " "
        else:
            key_char = QKeySequence(key).toString()
        ctrl_only_pressed = e.modifiers() == Qt.ControlModifier

        if self.mouse_clicked or key in [Qt.Key_Return]:
            return
        if ctrl_only_pressed and key in [Qt.Key_Z, Qt.Key_Y, Qt.Key_C]:  # shortcut
            super().keyPressEvent(e)
        elif key in [
            Qt.Key_Left,
            Qt.Key_Right,
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_Home,
            Qt.Key_End,
            Qt.Key_PageDown,
            Qt.Key_PageUp,
        ]:  # Arrow keys
            super().keyPressEvent(e)
        elif key_char in chars_allowed:
            super().keyPressEvent(e)
        elif self.hasSelectedText() and key in [Qt.Key_Backspace, Qt.Key_Delete]:
            super().keyPressEvent(e)
        elif key == Qt.Key_Backspace:
            char_prev = self.get_prev_char()
            if char_prev in chars_allowed:
                super().keyPressEvent(e)
        elif key == Qt.Key_Delete:
            char_post = self.get_post_char()
            if char_post in chars_allowed:
                super().keyPressEvent(e)

        self.validate_selection()
        self.validate_cursor_pos()


class MainWindow(QMainWindow):
    """Mainwindow."""

    def __init__(self, parent) -> None:
        """init."""
        json_example = """
{ "glossary1": [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2],
  "glossary2": [3, 2, 3, 4, 5, 6, 7, 9],
  "glossary3dd": ["dkrwhi", "dkwin"],
  "dhrwodn": {"dhrwidn":[1],
      "dh1": {"kk": 55, "yy":"widn", "sdknw": [1,2,3]},
      "dh2": {"kk": 55, "yy":"widn", "sdknw": [1,2,{"dhrwodn": 44}]}},
  "fc": 9e9 }
"""
        super().__init__(parent)
        widget = JsonValueEditor(json_example)
        widget.setMinimumSize(1600, 1200)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        pass

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainwindow = MainWindow(None)
    mainwindow.show()
    app.exec_()
