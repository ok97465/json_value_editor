"""Json formatter.

- No line breaks only when the list is composed of numbers.
- Line has no more than one value(Number, String, list).
- Line has no more than one key.

References:
    https://gist.github.com/lwthatcher/cd3f7a0a452147fbaae48730354e9993

:author: ok97465
:Date created: 21.10.29 11:50:31
"""
# %% Import
# Standard library imports
import json
import re

# Third party imports
import _ctypes


class NoIndent(object):
    """."""

    def __init__(self, value):
        """."""
        self.value = value

    def __repr__(self):
        """."""
        if not isinstance(self.value, list):
            return repr(self.value)
        else:  # Sort the representation of any dicts in the list.
            reps = (
                "{{{}}}".format(
                    ", ".join(("{!r}:{}".format(k, v) for k, v in sorted(v.items())))
                )
                if isinstance(v, dict)
                else repr(v)
                for v in self.value
            )
            return "[" + ", ".join(reps) + "]"


def di(obj_id):
    """Reverse of id() function."""
    # from https://stackoverflow.com/a/15012814/355230
    return _ctypes.PyObj_FromPtr(obj_id)


def check_objs(obj):
    """."""
    # base case
    if isinstance(obj, list):
        for val in obj:
            if not(isinstance(val, int) or isinstance(val, float)):
                break
        else:
            # No line breaks only when the list is composed of numbers.
            return NoIndent(obj)

    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = check_objs(v)
    elif isinstance(obj, list):
        for i, l in enumerate(obj):
            obj[i] = check_objs(l)
    # return changed object

    return obj


class PrettyJsonEncoder(json.JSONEncoder):
    """."""

    FORMAT_SPEC = "@@{}@@"
    regex = re.compile(FORMAT_SPEC.format(r"(\d+)"))

    def default(self, obj):
        """."""
        return (
            self.FORMAT_SPEC.format(id(obj))
            if isinstance(obj, NoIndent)
            else super().default(obj)
        )

    def encode(self, obj):
        """."""
        # recursively check if should convert to NoIndent object
        obj = check_objs(obj)

        # start formatting
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.
        json_repr = super().encode(obj)  # Default JSON repr.

        # Replace any marked-up object ids in the JSON repr with the value
        # returned from the repr() of the corresponding Python object.
        for match in self.regex.finditer(json_repr):
            id = int(match.group(1))
            # Replace marked-up id with actual Python object repr().
            json_repr = json_repr.replace(
                '"{}"'.format(format_spec.format(id)), repr(di(id))
            )
        json_repr = json_repr.replace("'", '"')
        return json_repr
