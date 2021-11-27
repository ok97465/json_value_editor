r"""Test json infos.

:author: ok97465
:Date created: 21.11.26 20:07:04
"""
# %% Import
# Local imports
from json_infos import ContainerLineInfo

JSON_EXAMPLE = """
{ "glossary1" : [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2],
  "glossary2" : [3, 2, 3, 4, 5, 6, 7, 9],
  "glossary3dd":   ["dkrwhi", "dkwin"],
  "dhrwodn": {"dhrwidn":[1],
      "dh1":  {"kk": 55, "yy":"widn", "sdknw": [1,2,3]},
      "dh2":  {"kk": 55, "yy":"widn", "sdknw": [1,2,{"dhrwodn": 44}]  }},
  "fc": 9e9 }

"""


def test_pos_of_value():
    """Test position of value."""
    line_infos = ContainerLineInfo(JSON_EXAMPLE)
    doc = line_infos.json_str.splitlines()

    assert line_infos.pos_of_value(0, doc[0]) == (1, 1)
    assert line_infos.pos_of_value(1, doc[1]) == (16, 68)
    assert line_infos.pos_of_value(2, doc[2]) == (16, 38)
    assert line_infos.pos_of_value(3, doc[3]) == (18, 18)
    assert line_infos.pos_of_value(4, doc[4]) == (5, 11)
    assert line_infos.pos_of_value(5, doc[5]) == (5, 10)
    assert line_infos.pos_of_value(6, doc[6]) == (4, 4)
    assert line_infos.pos_of_value(7, doc[7]) == (14, 14)
    assert line_infos.pos_of_value(8, doc[8]) == (16, 17)
    assert line_infos.pos_of_value(9, doc[9]) == (12, 12)
    assert line_infos.pos_of_value(10, doc[10]) == (12, 14)
    assert line_infos.pos_of_value(11, doc[11]) == (13, 17)
    assert line_infos.pos_of_value(12, doc[12]) == (16, 23)
    assert line_infos.pos_of_value(13, doc[13]) == (6, 6)
    assert line_infos.pos_of_value(14, doc[14]) == (12, 12)
    assert line_infos.pos_of_value(15, doc[15]) == (12, 14)
    assert line_infos.pos_of_value(16, doc[16]) == (13, 17)
    assert line_infos.pos_of_value(17, doc[17]) == (16, 16)
    assert line_infos.pos_of_value(18, doc[18]) == (8, 9)
    assert line_infos.pos_of_value(19, doc[19]) == (8, 9)
    assert line_infos.pos_of_value(20, doc[20]) == (9, 9)
    assert line_infos.pos_of_value(21, doc[21]) == (21, 23)
    assert line_infos.pos_of_value(22, doc[22]) == (9, 9)
    assert line_infos.pos_of_value(23, doc[23]) == (7, 7)
    assert line_infos.pos_of_value(24, doc[24]) == (5, 5)
    assert line_infos.pos_of_value(25, doc[25]) == (4, 4)
    assert line_infos.pos_of_value(26, doc[26]) == (8, 20)
    assert line_infos.pos_of_value(27, doc[27]) == (1, 1)
