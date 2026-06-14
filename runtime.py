"""JavaScript runtime helpers used by translated Python code."""

import math
import random
from datetime import datetime
from functools import cmp_to_key


class _Undefined:
    """Sentinel for JavaScript `undefined`."""

    def __repr__(self):
        return "undefined"


undefined = _Undefined()


class JSObject(dict):
    """Small object wrapper with JavaScript-style property access."""

    def __getattr__(self, name):
        return self.get(name, undefined)

    def __setattr__(self, name, value):
        self[name] = value


def js_object(values):
    """Create an object and wrap nested dicts too."""
    obj = JSObject()
    if isinstance(values, dict):
        values = values.items()
    for key, value in values:
        if isinstance(value, dict) and not isinstance(value, JSObject):
            value = js_object(value)
        obj[key] = value
    return obj


def js_get(obj, key):
    if key == "length" and isinstance(obj, (str, list)):
        return len(obj)
    if isinstance(obj, dict):
        return obj.get(key, undefined)
    return getattr(obj, key, undefined)


def js_set(obj, key, value):
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)
    return value


def js_strict_eq(a, b):
    """JavaScript strict equality (===)."""
    if a is None and b is undefined:
        return False
    if a is undefined and b is None:
        return False
    if a is undefined or b is undefined:
        return a is b
    return type(a) is type(b) and a == b


def js_strict_ne(a, b):
    """JavaScript strict inequality (!==)."""
    return not js_strict_eq(a, b)


def js_string(value):
    """JavaScript String() conversion for common values."""
    if value is undefined:
        return "undefined"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    if isinstance(value, float) and math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    if isinstance(value, list):
        return ",".join(js_string(item) for item in value)
    return str(value)


def js_number(value=0):
    """JavaScript Number() conversion for common values."""
    if value is undefined:
        return float("nan")
    if value is None:
        return 0
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return 0
        try:
            number = float(text)
        except ValueError:
            return float("nan")
        if number.is_integer():
            return int(number)
        return number
    return float("nan")


def js_truthy(value):
    """JavaScript truthy/falsy behavior for common values."""
    if value is undefined or value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0 and not (isinstance(value, float) and math.isnan(value))
    if isinstance(value, str):
        return value != ""
    return True


def js_boolean(value=False):
    return js_truthy(value)


def js_eq(a, b):
    """JavaScript loose equality (==) for common beginner cases."""
    if js_strict_eq(a, b):
        return True
    if (a is None and b is undefined) or (a is undefined and b is None):
        return True
    if isinstance(a, bool):
        return js_eq(js_number(a), b)
    if isinstance(b, bool):
        return js_eq(a, js_number(b))
    if isinstance(a, (int, float)) and isinstance(b, str):
        return js_number(b) == a
    if isinstance(a, str) and isinstance(b, (int, float)):
        return js_number(a) == b
    return False


def js_ne(a, b):
    """JavaScript loose inequality (!=)."""
    return not js_eq(a, b)


def js_add(a, b):
    """JavaScript + with string coercion."""
    if isinstance(a, str) or isinstance(b, str):
        return js_string(a) + js_string(b)
    return a + b


def _format_log_value(value):
    if value is undefined:
        return "undefined"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    if isinstance(value, float) and math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    return str(value)


def console_log(*args):
    """JavaScript console.log."""
    print(" ".join(_format_log_value(arg) for arg in args))


class _Console:
    log = staticmethod(console_log)


class _Math:
    """JavaScript Math object subset."""

    @staticmethod
    def floor(value):
        return math.floor(js_number(value))

    @staticmethod
    def random():
        return random.random()

    @staticmethod
    def ceil(value):
        return math.ceil(js_number(value))

    @staticmethod
    def round(value):
        return math.floor(js_number(value) + 0.5)

    @staticmethod
    def max(*values):
        if not values:
            return -float("inf")
        numbers = [js_number(value) for value in values]
        if any(isinstance(value, float) and math.isnan(value) for value in numbers):
            return float("nan")
        return max(numbers)

    @staticmethod
    def min(*values):
        if not values:
            return float("inf")
        numbers = [js_number(value) for value in values]
        if any(isinstance(value, float) and math.isnan(value) for value in numbers):
            return float("nan")
        return min(numbers)

    @staticmethod
    def abs(value):
        return abs(js_number(value))

    @staticmethod
    def pow(base, exponent):
        return js_number(base) ** js_number(exponent)


class _Date:
    """Practical JavaScript Date subset using local time."""

    def __init__(self):
        self.value = datetime.now()

    def getFullYear(self):
        return self.value.year

    def getMonth(self):
        return self.value.month - 1

    def getDate(self):
        return self.value.day

    def getHours(self):
        return self.value.hour

    def getMinutes(self):
        return self.value.minute

    def toString(self):
        return self.value.strftime("%a %b %d %Y %H:%M:%S")

    def __str__(self):
        return self.toString()


def js_push(arr, item):
    arr.append(item)
    return len(arr)


def js_pop(arr):
    return arr.pop()


def js_shift(arr):
    if not arr:
        return undefined
    return arr.pop(0)


def js_unshift(arr, *items):
    arr[:0] = list(items)
    return len(arr)


def js_splice(arr, start, delete_count=None, *items):
    start = int(start)
    if start < 0:
        start = max(len(arr) + start, 0)
    else:
        start = min(start, len(arr))

    if delete_count is None:
        delete_count = len(arr) - start
    delete_count = max(0, int(delete_count))

    end = min(start + delete_count, len(arr))
    removed = arr[start:end]
    arr[start:end] = list(items)
    return removed


def js_reverse(arr):
    arr.reverse()
    return arr


def js_sort(arr, comparator=None):
    if comparator is None:
        arr.sort(key=lambda item: str(item))
    else:
        arr.sort(key=cmp_to_key(comparator))
    return arr


def js_join(arr, separator=""):
    return separator.join(js_string(item) for item in arr)


def js_slice(value, start=0, end=None):
    if end is None:
        return value[start:]
    return value[start:end]


def js_concat(value, *others):
    result = value
    for other in others:
        result = result + other
    return result


def js_map(arr, callback):
    return [callback(item) for item in arr]


def js_filter(arr, callback):
    return [item for item in arr if js_truthy(callback(item))]


def js_reduce(arr, callback, initial=undefined):
    index = 0
    if initial is undefined:
        if not arr:
            raise TypeError("Reduce of empty array with no initial value")
        result = arr[0]
        index = 1
    else:
        result = initial
    while index < len(arr):
        result = callback(result, arr[index])
        index += 1
    return result


def js_find(arr, callback):
    for item in arr:
        if js_truthy(callback(item)):
            return item
    return undefined


def js_some(arr, callback):
    for item in arr:
        if js_truthy(callback(item)):
            return True
    return False


def js_every(arr, callback):
    for item in arr:
        if not js_truthy(callback(item)):
            return False
    return True


def js_includes(container, value):
    if isinstance(container, str):
        return str(value) in container
    return value in container


def js_index_of(arr, value):
    try:
        if isinstance(arr, str):
            return arr.index(str(value))
        return arr.index(value)
    except ValueError:
        return -1


def js_split(value, separator):
    if separator == "":
        return list(value)
    return value.split(separator)


def js_trim(value):
    return value.strip()


def js_replace(value, old, new):
    return value.replace(old, new, 1)


def js_replace_all(value, old, new):
    return value.replace(old, new)


def js_substring(value, start=0, end=None):
    start = max(0, int(start))
    if end is None:
        end = len(value)
    else:
        end = max(0, int(end))
    if start > end:
        start, end = end, start
    return value[start:end]


def js_starts_with(value, prefix):
    return value.startswith(prefix)


def js_ends_with(value, suffix):
    return value.endswith(suffix)


def js_to_upper_case(value):
    return value.upper()


def js_to_lower_case(value):
    return value.lower()


def build_runtime():
    """Return the global namespace for exec()."""
    return {
        "undefined": undefined,
        "js_object": js_object,
        "js_get": js_get,
        "js_set": js_set,
        "js_strict_eq": js_strict_eq,
        "js_strict_ne": js_strict_ne,
        "js_eq": js_eq,
        "js_ne": js_ne,
        "js_truthy": js_truthy,
        "js_add": js_add,
        "Number": js_number,
        "String": js_string,
        "Boolean": js_boolean,
        "console_log": console_log,
        "console": _Console(),
        "Math": _Math(),
        "Date": _Date,
        "js_push": js_push,
        "js_pop": js_pop,
        "js_shift": js_shift,
        "js_unshift": js_unshift,
        "js_splice": js_splice,
        "js_reverse": js_reverse,
        "js_sort": js_sort,
        "js_join": js_join,
        "js_slice": js_slice,
        "js_concat": js_concat,
        "js_map": js_map,
        "js_filter": js_filter,
        "js_reduce": js_reduce,
        "js_find": js_find,
        "js_some": js_some,
        "js_every": js_every,
        "js_includes": js_includes,
        "js_index_of": js_index_of,
        "js_split": js_split,
        "js_trim": js_trim,
        "js_replace": js_replace,
        "js_replace_all": js_replace_all,
        "js_substring": js_substring,
        "js_starts_with": js_starts_with,
        "js_ends_with": js_ends_with,
        "js_to_upper_case": js_to_upper_case,
        "js_to_lower_case": js_to_lower_case,
    }
