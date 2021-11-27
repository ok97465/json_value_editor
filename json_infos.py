r"""Json line info.

:author: ok97465
:Date created: 21.11.26 20:00:54
"""
# %% Import
# Standard library imports
import json
import re
from typing import List, NamedTuple, Tuple, Optional, Dict

# Local imports
from json_formatting import PrettyJsonEncoder


class ValueKind:
    """Json value type constants."""

    NONE = 0
    NUM = 1
    NUM_LIST = 2
    STR = 3


class ValueData(NamedTuple):
    """Value Data."""

    display: str
    data: str


class LineInfo:
    """Class for Information of the line of json."""

    def __init__(
        self,
        pos_start_of_value: int,
        val_type: int,
        val_list: Optional[List[ValueData]] = None,
    ):
        """."""
        self.pos_start: int = pos_start_of_value
        self.val_type = val_type
        self.val_list = val_list
        self.end_char: str = {
            ValueKind.NONE: "",
            ValueKind.NUM: "",
            ValueKind.NUM_LIST: "]",
            ValueKind.STR: '"',
        }[val_type]

        self.chars_allowed: str = ""  # Editable charaters in editor.

        if val_list is not None:
            pass
        elif val_type in (ValueKind.NUM, ValueKind.NUM_LIST):
            self.chars_allowed = "-.0123456789eE "
        elif val_type == ValueKind.STR:
            self.chars_allowed = (
                "0123456789"
                "abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "!#$%&'()*+,-./:;<=>?@[]^_`{|}~ "
            )


class ContainerLineInfo:
    """Container for json line info."""

    def __init__(self, json_str: str, key_val_list: Dict[str, List[ValueData]]):
        """."""
        self.json_str: str = ""
        self.line_infos: List[LineInfo] = []
        self.key_val_list = key_val_list
        self.parse_json(json_str)

    def parse_json(self, json_str: str):
        """Parse json string."""
        json_parsed = json.loads(json_str)
        # Each line is formatted to have no more than one key and no more than one value
        self.json_str: str = json.dumps(json_parsed, cls=PrettyJsonEncoder, indent=2)

        # if key_pattern is changed, check self.key_val_list.get line.
        key_pattern = re.compile(r'^([ ]*".*": )')
        space_pattern = re.compile(r"^([ ]*)")

        for line in self.json_str.splitlines():
            key = key_pattern.match(line)
            space = space_pattern.match(line)
            val_list = None

            if (line.strip() in ("{", "}", "},", "[", "]", "],")) or (
                line[-1] in ("{", "[")
            ):  # the line has no value.
                pos_start, val_type = len(line), ValueKind.NONE
            else:
                if key:  # the line has key.
                    pos = key.end()
                    val_list = self.key_val_list.get(key[0].strip()[1:-2], None)
                elif space:
                    pos = space.end()
                else:
                    pos = len(line) - 1  # This can't occur when formatting is applied.

                char = line[pos]
                if char == "[":
                    pos_start, val_type = pos + 1, ValueKind.NUM_LIST
                elif char == '"':
                    pos_start, val_type = pos + 1, ValueKind.STR
                else:
                    pos_start, val_type = pos, ValueKind.NUM

            self.line_infos.append(LineInfo(pos_start, val_type, val_list))

    def __getitem__(self, idx: int) -> LineInfo:
        """Get LineInfo."""
        return self.line_infos[idx]

    def start_pos_of_value(self, line_no: int) -> int:
        """Return the starting position of Value in the line."""
        return self.line_infos[line_no].pos_start

    def end_pos_of_value(self, line_no: int, line: str) -> int:
        """Return the ending position of Value in the line."""
        val_type = self.line_infos[line_no].val_type
        end_char = self.line_infos[line_no].end_char
        if line[-1] == "\n":
            line = line[:-1]

        end_pos = len(line)
        if val_type == ValueKind.NONE:
            pass
        elif val_type == ValueKind.NUM:
            if line.rstrip()[-1] == ",":
                end_pos = line.rfind(",")
        else:
            end_pos = line.rfind(end_char)

        return end_pos

    def pos_of_value(self, line_no: int, line: str) -> Tuple[int, int]:
        """Return the starting, ending position of Value in the line."""
        start = self.start_pos_of_value(line_no)
        end = self.end_pos_of_value(line_no, line)
        return start, end
