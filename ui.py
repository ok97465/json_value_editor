"""To modify only the Json Value."""
# %% Import
# Standard library imports
import sys
from typing import Tuple

# Third party imports
import qdarkstyle
from PyQt5.Qsci import QsciLexerJSON, QsciScintilla
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QFont, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QListView,
)

# Local imports
from json_infos import ContainerLineInfo, ValueData, ValueKind


class SelectionWidget(QListWidget):
    """Selection list widget."""

    def __init__(self, editor, ancestor) -> None:
        """."""
        super().__init__(ancestor)
        self.editor = editor
        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint)
        self.hide()
        self.line_no: int = 0

        self.setMinimumWidth(300)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setResizeMode(QListView.Adjust)
        self.setAutoScroll(False)
        self.setSpacing(2)
        self.itemClicked.connect(self.item_selected)

    def keyPressEvent(self, e: QKeyEvent):
        """Override Qt method."""
        key = e.key()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.item_selected()
        elif key == Qt.Key_Escape:
            self.hide()
        elif key in (
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_PageUp,
            Qt.Key_PageDown,
            Qt.Key_Home,
            Qt.Key_End,
        ):
            super().keyPressEvent(e)

    def item_selected(self, item=None):
        """Perform the item selected action."""
        if item is None:
            item = self.currentItem()
        data = item.data(Qt.UserRole)

        if data:
            editor = self.editor
            pos_start_of_val, pos_end_of_val = self.editor.pos_of_value(self.line_no)
            editor.setSelection(
                self.line_no, pos_start_of_val, self.line_no, pos_end_of_val
            )
            editor.replaceSelectedText(data)

        self.hide()

    def hide(self):
        """Hide self, and focus to editor."""
        super().hide()
        self.editor.setFocus()

    def move_to_val_pos(self, line_no: int):
        """Move selection widget to starting position of value in editor."""
        editor = self.editor
        pos_start_value = editor.start_pos_of_value(line_no)
        pos_sci = editor.SendScintilla(editor.SCI_FINDCOLUMN, line_no, pos_start_value)
        pos_x = editor.SendScintilla(editor.SCI_POINTXFROMPOSITION, 0, pos_sci)
        pos_y = editor.SendScintilla(editor.SCI_POINTYFROMPOSITION, 0, pos_sci)
        height = editor.SendScintilla(editor.SCI_TEXTHEIGHT, line_no)

        self.move(pos_x, pos_y + height)

    def show_at_line(self, line_no: int):
        """Show widget in editor."""
        self.line_no = line_no
        editor = self.editor
        val_list = editor.line_infos[line_no].val_list
        if val_list is None:
            self.hide()
            return
        self.clear()

        for idx, val_data in enumerate(val_list):
            item = QListWidgetItem()
            item.setData(Qt.DisplayRole, val_data.display)
            item.setData(Qt.UserRole, val_data.data)
            if idx % 2:
                item.setBackground(QColor(20, 20, 49))
            else:
                item.setBackground(QColor(18, 32, 49))
            self.addItem(item)

        self.show()
        self.setFocus()
        self.raise_()

        self.move_to_val_pos(line_no)
        self.setCurrentRow(0)

        self.setFixedSize(
            self.sizeHintForColumn(0) + 4 * (self.frameWidth() + self.spacing()),
            self.sizeHintForRow(0) * self.count()
            + 4 * (self.frameWidth() + self.spacing()),
        )


class JsonValueEditor(QsciScintilla):
    """."""

    def __init__(self, json_str: str, parent=None, key_val_list={}):
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
        self.line_infos = ContainerLineInfo(json_str, key_val_list)
        self.setText(self.line_infos.json_str)
        self.setCursorPosition(1, self.start_pos_of_value(1))

        self.mouse_clicked = False

        # selection widget
        self.selection_widget = SelectionWidget(self, parent)

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
        line_no, _ = self.get_cusor_pos_from_qmousepos(e.pos())
        self.selection_widget.show_at_line(line_no)

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
        val_list = self.line_infos[line_no].val_list

        ctrl_only_pressed = e.modifiers() == Qt.ControlModifier
        key_char, key = e.text(), e.key()

        if self.mouse_clicked or key in (Qt.Key_Return, Qt.Key_Enter):
            return
        if ctrl_only_pressed and key in (Qt.Key_Z, Qt.Key_Y, Qt.Key_C):  # shortcut
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
        elif val_list and key == Qt.Key_Tab:
            self.selection_widget.show_at_line(line_no)
        elif self.hasSelectedText():
            if key_char in chars_allowed or key in (Qt.Key_Backspace, Qt.Key_Delete):
                if set(self.selectedText()) <= set(chars_allowed):
                    super().keyPressEvent(e)
        elif key_char in chars_allowed:
            super().keyPressEvent(e)
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):
            if key == Qt.Key_Backspace:
                char = self.get_prev_char()
            else:
                char = self.get_post_char()
            if char in chars_allowed:
                super().keyPressEvent(e)

        self.validate_selection()
        self.validate_cursor_pos()

        # Show value list
        line_no_new, _ = self.getCursorPosition()
        if line_no_new != line_no:
            self.selection_widget.show_at_line(line_no_new)


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
        key_val_list = {
            "kk": [ValueData("Wow : 11", "11"), ValueData("Hwowodinxk: 55", "55")],
            "yy": [
                ValueData("value1", "value1"),
                ValueData("widn", "widn"),
                ValueData("anrndghk Rhcdl", "diwndkwosn"),
            ],
        }
        super().__init__(parent)
        widget = JsonValueEditor(json_example, self, key_val_list)
        widget.setMinimumSize(800, 600)
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
