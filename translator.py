"""Translate a subset of JavaScript into executable Python."""

import re


def translate(js_source):
    """Convert JavaScript source code into Python source code."""
    source = remove_comments(js_source)
    source = convert_function_expressions(source)
    source = convert_arrow_function_blocks(source)
    source = protect_object_literals(source)
    source = protect_for_loop_semicolons(source)
    source = convert_else_blocks(source)
    source = convert_braces_to_indent(source)
    lines = source.split("\n")
    python_lines = []

    for line in lines:
        converted = convert_line(line)
        if converted is not None:
            python_lines.append(converted)

    return "\n".join(python_lines) + "\n"


def remove_comments(source):
    """Remove // and /* */ comments."""
    result = []
    i = 0
    in_string = None

    while i < len(source):
        char = source[i]

        if in_string:
            result.append(char)
            if char == "\\" and i + 1 < len(source):
                result.append(source[i + 1])
                i += 2
                continue
            if char == in_string:
                in_string = None
            i += 1
            continue

        if char in ("'", '"'):
            in_string = char
            result.append(char)
            i += 1
            continue

        if char == "/" and i + 1 < len(source):
            next_char = source[i + 1]
            if next_char == "/":
                while i < len(source) and source[i] != "\n":
                    i += 1
                continue
            if next_char == "*":
                i += 2
                while i + 1 < len(source) and not (source[i] == "*" and source[i + 1] == "/"):
                    i += 1
                i += 2
                continue

        result.append(char)
        i += 1

    return "".join(result)


def convert_function_expressions(source):
    """Turn simple assigned function expressions into declarations."""
    pattern = r"\b(?:let|const|var)\s+(\w+)\s*=\s*function\s*\((.*?)\)\s*\{"
    return re.sub(pattern, r"function \1(\2) {", source)


def convert_arrow_function_blocks(source):
    """Turn simple assigned block arrow functions into declarations."""
    pattern = r"\b(?:let|const|var)\s+(\w+)\s*=\s*(?:\((.*?)\)|(\w+))\s*=>\s*\{"

    def replace(match):
        params = match.group(2) if match.group(2) is not None else match.group(3)
        return f"function {match.group(1)}({params}) {{"

    return re.sub(pattern, replace, source)


def protect_object_literals(source):
    """Convert object literals before brace indentation sees them as blocks."""
    result = []
    index = 0
    in_string = None

    while index < len(source):
        char = source[index]

        if in_string:
            result.append(char)
            if char == "\\" and index + 1 < len(source):
                result.append(source[index + 1])
                index += 2
                continue
            if char == in_string:
                in_string = None
            index += 1
            continue

        if char in ("'", '"'):
            in_string = char
            result.append(char)
            index += 1
            continue

        if char == "{" and is_object_literal_start(source, index):
            content, close_index = read_braced_content(source, index)
            result.append(convert_object_literal(content))
            index = close_index + 1
            continue

        result.append(char)
        index += 1

    return "".join(result)


def is_object_literal_start(source, brace_index):
    """Heuristic: object literals usually follow =, (, [, comma, colon, or return."""
    pos = brace_index - 1
    while pos >= 0 and source[pos].isspace():
        pos -= 1
    if pos < 0:
        return True
    if source[pos] in "=([,:":
        return True
    return source[max(0, pos - 5) : pos + 1].strip().endswith("return")


def read_braced_content(source, open_index):
    """Return text inside a balanced {...} pair."""
    depth = 1
    index = open_index + 1
    start = index
    in_string = None

    while index < len(source):
        char = source[index]
        if in_string:
            if char == "\\":
                index += 2
                continue
            if char == in_string:
                in_string = None
            index += 1
            continue
        if char in ("'", '"'):
            in_string = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index], index
        index += 1

    raise ValueError("Unbalanced object literal")


def convert_object_literal(content):
    """Convert { name: value } into js_object({'name': value})."""
    items = []
    for part in split_at_depth_zero(content, ","):
        part = part.strip()
        if not part:
            continue
        key, value = split_object_property(part)
        key = key.strip()
        if not ((key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'"))):
            key = repr(key)
        value = value.strip()
        if value.startswith("{") and value.endswith("}"):
            converted_value = convert_object_literal(value[1:-1])
        else:
            converted_value = convert_expression(value)
        items.append(f"({key}, {converted_value})")
    return "js_object([" + ", ".join(items) + "])"


def split_object_property(part):
    """Split one object property at its top-level colon."""
    pieces = split_at_depth_zero(part, ":")
    if len(pieces) < 2:
        raise ValueError(f"Unsupported object property: {part}")
    return pieces[0], ":".join(pieces[1:])


def convert_else_blocks(source):
    """Turn '} else {' into a marker before brace conversion."""
    return source.replace("} else {", "}__ELSE__{")


def protect_for_loop_semicolons(source):
    """Keep for-loop headers on one line during brace conversion."""
    result = []
    index = 0

    while index < len(source):
        match = re.match(r"for\s*\(", source[index:])
        if not match:
            result.append(source[index])
            index += 1
            continue

        result.append(source[index : index + match.end()])
        index += match.end()
        depth = 1

        while index < len(source) and depth > 0:
            char = source[index]
            if char == "(":
                depth += 1
                result.append(char)
            elif char == ")":
                depth -= 1
                result.append(char)
            elif char == ";" and depth == 1:
                result.append("__FOR_SEM__")
            else:
                result.append(char)
            index += 1

    return "".join(result)


def convert_braces_to_indent(source):
    """Convert JavaScript braces and semicolons into Python indentation."""
    result = []
    indent = 0
    i = 0

    while i < len(source):
        if source.startswith("__ELSE__{", i):
            indent = max(0, indent - 1)
            result.append("\n")
            result.append("    " * indent)
            result.append("else:")
            indent += 1
            result.append("\n")
            result.append("    " * indent)
            i += len("__ELSE__{")
            continue

        char = source[i]

        if char == "{":
            result.append(":")
            indent += 1
            result.append("\n")
            result.append("    " * indent)
            i += 1
            continue

        if char == "}":
            indent = max(0, indent - 1)
            i += 1
            if i < len(source) and source[i] not in ";\n\r\t ":
                result.append("\n")
                result.append("    " * indent)
            continue

        if char == ";":
            result.append("\n")
            result.append("    " * indent)
            i += 1
            continue

        if char in "\n\r":
            result.append(char)
            i += 1
            while i < len(source) and source[i] in " \t":
                i += 1
            result.append("    " * indent)
            continue

        result.append(char)
        i += 1

    return "".join(result)


def convert_line(line):
    """Convert one line of intermediate code into Python."""
    stripped = line.strip()
    if not stripped:
        return None

    indent = line[: len(line) - len(line.lstrip())]

    if stripped == "else:":
        return indent + "else:"

    if stripped.startswith("if "):
        return convert_if_line(indent, stripped)

    if stripped.startswith("while "):
        return convert_while_line(indent, stripped)

    if stripped.startswith("for "):
        return convert_for_line(indent, stripped)

    if stripped.startswith("function "):
        return convert_function_line(indent, stripped)

    if stripped.startswith("return"):
        return convert_return_line(indent, stripped)

    return indent + convert_statement(stripped)


def convert_if_line(indent, stripped):
    """Convert an if-statement header."""
    match = re.match(r"if\s*\((.*)\)\s*:?\s*$", stripped)
    if not match:
        raise ValueError(f"Unsupported if statement: {stripped}")

    condition = convert_expression(match.group(1))
    return f"{indent}if js_truthy({condition}):"


def convert_while_line(indent, stripped):
    """Convert a while-loop header."""
    match = re.match(r"while\s*\((.*)\)\s*:?\s*$", stripped)
    if not match:
        raise ValueError(f"Unsupported while loop: {stripped}")

    condition = convert_expression(match.group(1))
    return f"{indent}while js_truthy({condition}):"


def convert_for_line(indent, stripped):
    """Convert a C-style for loop into a Python for/range loop."""
    match = re.match(r"for\s*\((.*)\)\s*:?\s*$", stripped)
    if not match:
        raise ValueError(f"Unsupported for loop: {stripped}")

    parts = match.group(1).split("__FOR_SEM__")
    if len(parts) != 3:
        raise ValueError(f"Unsupported for loop header: {stripped}")

    loop_var, range_expr = parse_for_to_range(parts[0], parts[1], parts[2])
    return f"{indent}for {loop_var} in {range_expr}:"


def parse_for_to_range(init, condition, update):
    """Convert for-loop init/condition/update into a Python range()."""
    init = re.sub(r"^(let|const)\s+", "", init.strip())
    init_match = re.match(r"(\w+)\s*=\s*(.+)", init)
    if not init_match:
        raise ValueError(f"Unsupported for-loop init: {init}")

    loop_var = init_match.group(1)
    start = convert_expression(init_match.group(2).strip())
    step = parse_for_update_step(loop_var, update.strip())
    end = parse_for_condition_end(loop_var, condition.strip())
    return loop_var, f"range({start}, {end}, {step})"


def parse_for_update_step(loop_var, update):
    """Read ++, --, +=, or -= update expressions."""
    if update in (f"{loop_var}++", f"++{loop_var}"):
        return 1
    if update in (f"{loop_var}--", f"--{loop_var}"):
        return -1

    plus_eq = re.match(rf"{loop_var}\s*\+=\s*(.+)", update)
    if plus_eq:
        return convert_expression(plus_eq.group(1).strip())

    minus_eq = re.match(rf"{loop_var}\s*-=\s*(.+)", update)
    if minus_eq:
        step = convert_expression(minus_eq.group(1).strip())
        return f"-({step})"

    raise ValueError(f"Unsupported for-loop update: {update}")


def parse_for_condition_end(loop_var, condition):
    """Convert loop condition into the range end boundary."""
    for operator in ("<=", ">=", "<", ">"):
        match = re.match(rf"{loop_var}\s*{re.escape(operator)}\s*(.+)", condition)
        if not match:
            continue

        bound = convert_expression(match.group(1).strip())
        if operator == "<=":
            return f"({bound}) + 1"
        if operator == "<":
            return bound
        if operator == ">=":
            return f"({bound}) - 1"
        if operator == ">":
            return bound

    raise ValueError(f"Unsupported for-loop condition: {condition}")


def convert_function_line(indent, stripped):
    """Convert a function declaration header."""
    match = re.match(r"function\s+(\w+)\s*\((.*?)\)\s*:?\s*$", stripped)
    if not match:
        raise ValueError(f"Unsupported function declaration: {stripped}")

    name = match.group(1)
    params = convert_function_params(match.group(2).strip())
    return f"{indent}def {name}({params}):"


def convert_function_params(params):
    """Convert simple JS rest parameters into Python *args."""
    if not params:
        return params
    parts = [part.strip() for part in params.split(",")]
    converted = []
    for part in parts:
        if part.startswith("..."):
            converted.append("*" + part[3:].strip())
        else:
            converted.append(part)
    return ", ".join(converted)


def convert_return_line(indent, stripped):
    """Convert a return statement."""
    match = re.match(r"return\s+(.*)", stripped)
    if match:
        value = convert_expression(match.group(1))
        return f"{indent}return {value}"
    return f"{indent}return"


def convert_statement(statement):
    """Convert a regular statement."""
    statement = re.sub(r"^(let|const)\s+", "", statement)
    statement = re.sub(r"^console\.log\s*\(", "console.log(", statement)

    plus_eq_match = re.match(r"^(.+?)\+=\s*(.+)$", statement)
    if plus_eq_match:
        target = plus_eq_match.group(1).strip()
        value = plus_eq_match.group(2).strip()
        return f"{convert_expression(target)} += {convert_expression(value)}"

    inc_match = re.match(r"^(\w+)\+\+$", statement)
    if inc_match:
        return f"{inc_match.group(1)} += 1"

    dec_match = re.match(r"^(\w+)--$", statement)
    if dec_match:
        return f"{dec_match.group(1)} -= 1"

    if statement.startswith("console.log(") and statement.endswith(")"):
        args = statement[len("console.log(") : -1]
        converted_args = convert_call_arguments(args)
        return f"console.log({converted_args})"

    if "=" in statement and not re.search(r"==|!=|<=|>=|\+=", statement):
        target, value = split_assignment(statement)
        if value == "":
            return convert_expression(statement)
        property_match = re.match(r"^(\w+)\.(\w+)$", target.strip())
        if property_match:
            obj_name = property_match.group(1)
            prop_name = property_match.group(2)
            return f"js_set({obj_name}, {prop_name!r}, {convert_expression(value.strip())})"
        return f"{convert_expression(target.strip())} = {convert_expression(value.strip())}"

    return convert_expression(statement)


def split_assignment(statement):
    """Split on the first = that is not part of ==, !=, <=, or >=."""
    for index, char in enumerate(statement):
        if char != "=":
            continue
        before = statement[:index]
        after = statement[index + 1 :]
        if before.endswith(("=", "!", "<", ">", "+", "-", "*", "/", "%")):
            continue
        if after.startswith(("=", ">")):
            continue
        return before, after
    return statement, ""


def convert_call_arguments(args):
    """Convert comma-separated call arguments."""
    parts = split_at_depth_zero(args, ",")
    return ", ".join(convert_expression(part.strip()) for part in parts)


def convert_expression(expr):
    """Convert a JavaScript expression into Python."""
    expr = expr.strip()
    if not expr:
        return expr

    arrow = convert_arrow_function(expr)
    if arrow != expr:
        return arrow

    for operator, python_operator in (("||", "or"), ("&&", "and")):
        parts = split_at_depth_zero(expr, operator)
        if len(parts) > 1:
            return f" {python_operator} ".join(convert_expression(part.strip()) for part in parts)

    if expr.startswith("!") and not expr.startswith("!="):
        inner = expr[1:].strip()
        if is_wrapped_in_parentheses(inner):
            inner = inner[1:-1].strip()
        return f"not js_truthy({convert_expression(inner)})"

    for operator, func_name in (
        ("===", "js_strict_eq"),
        ("!==", "js_strict_ne"),
        ("==", "js_eq"),
        ("!=", "js_ne"),
    ):
        parts = split_at_depth_zero(expr, operator)
        if len(parts) > 1:
            left = convert_expression(parts[0])
            right = convert_expression(parts[1])
            return f"{func_name}({left}, {right})"

    parts = split_at_depth_zero(expr, "+")
    if len(parts) > 1:
        result = convert_expression(parts[0])
        for part in parts[1:]:
            result = f"js_add({result}, {convert_expression(part)})"
        return result

    expr = convert_spread_operator(expr)
    expr = convert_member_calls(expr)
    expr = convert_property_access(expr)
    return convert_literals(expr)


def convert_arrow_function(expr):
    """Convert expression-bodied arrow functions into Python lambdas."""
    arrow_index = find_top_level_arrow(expr)
    if arrow_index == -1:
        return expr

    params = expr[:arrow_index].strip()
    body = expr[arrow_index + 2 :].strip()
    if params.startswith("(") and params.endswith(")"):
        params = params[1:-1].strip()
    return f"lambda {params}: {convert_expression(body)}"


def is_wrapped_in_parentheses(expr):
    """Return True when one outer (...) pair wraps the full expression."""
    if not (expr.startswith("(") and expr.endswith(")")):
        return False
    try:
        _, close_index = extract_parenthesized_content(expr, 0)
    except ValueError:
        return False
    return close_index == len(expr) - 1


def find_top_level_arrow(expr):
    """Find => outside strings, parentheses, brackets, and object literals."""
    depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string = None
    index = 0

    while index < len(expr) - 1:
        char = expr[index]
        if in_string:
            if char == "\\":
                index += 2
                continue
            if char == in_string:
                in_string = None
            index += 1
            continue
        if char in ("'", '"'):
            in_string = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif depth == 0 and bracket_depth == 0 and brace_depth == 0 and expr.startswith("=>", index):
            return index
        index += 1
    return -1


def convert_spread_operator(expr):
    """Convert [...arr] into Python [*arr] forms."""
    expr = expr.replace("[...", "[*")
    expr = expr.replace(", ...", ", *")
    return expr


def convert_property_access(expr):
    """Convert obj.name into js_get(obj, 'name') for simple property reads."""
    changed = True
    while changed:
        changed = False
        search_from = 0
        while True:
            dot_index = expr.find(".", search_from)
            if dot_index == -1:
                break
            name_match = re.match(r"\.([A-Za-z_]\w*)", expr[dot_index:])
            if not name_match:
                search_from = dot_index + 1
                continue
            prop_name = name_match.group(1)
            after_name = dot_index + len(prop_name) + 1
            if after_name < len(expr) and expr[after_name] == "(":
                search_from = dot_index + 1
                continue
            receiver, recv_start = extract_receiver(expr, dot_index)
            if receiver is None or receiver in ("Math", "console"):
                search_from = dot_index + 1
                continue
            converted = f"js_get({convert_expression(receiver)}, {prop_name!r})"
            expr = expr[:recv_start] + converted + expr[after_name:]
            changed = True
            break
    return expr


def extract_receiver(expr, dot_index):
    """Return receiver text and its start index before dot_index."""
    receiver, start = parse_suffix_expression(expr, dot_index)
    return receiver, start


def parse_suffix_expression(expr, end):
    """Parse the expression immediately before end (usually a dot)."""
    pos = end - 1
    while pos >= 0 and expr[pos].isspace():
        pos -= 1
    if pos < 0:
        return None, None

    if expr[pos] == ")":
        close = pos
        depth = 1
        pos -= 1
        while pos >= 0 and depth > 0:
            if expr[pos] == ")":
                depth += 1
            elif expr[pos] == "(":
                depth -= 1
            pos -= 1

        name_end = pos
        while name_end >= 0 and (expr[name_end].isalnum() or expr[name_end] == "_"):
            name_end -= 1

        if name_end < pos:
            if name_end >= 0 and expr[name_end] == ".":
                left, left_start = parse_suffix_expression(expr, name_end)
                if left is None:
                    return expr[name_end + 1 : close + 1], name_end + 1
                return left + expr[name_end : close + 1], left_start
            return expr[name_end + 1 : close + 1], name_end + 1

        return expr[pos + 1 : close + 1], pos + 1

    if expr[pos] == "]":
        close = pos
        depth = 1
        pos -= 1
        while pos >= 0 and depth > 0:
            if expr[pos] == "]":
                depth += 1
            elif expr[pos] == "[":
                depth -= 1
            pos -= 1
        name_end = pos
        while name_end >= 0 and (expr[name_end].isalnum() or expr[name_end] == "_"):
            name_end -= 1
        return expr[name_end + 1 : close + 1], name_end + 1

    if expr[pos] in ("'", '"'):
        quote = expr[pos]
        close = pos
        pos -= 1
        while pos >= 0:
            if expr[pos] == quote and (pos == 0 or expr[pos - 1] != "\\"):
                return expr[pos : close + 1], pos
            pos -= 1
        return None, None

    if expr[pos].isalnum() or expr[pos] == "_":
        close = pos
        while pos >= 0 and (expr[pos].isalnum() or expr[pos] == "_"):
            pos -= 1
        return expr[pos + 1 : close + 1], pos + 1

    return None, None


def extract_parenthesized_content(expr, open_paren_index):
    """Return content inside parentheses and the index of the closing parenthesis."""
    if expr[open_paren_index] != "(":
        raise ValueError("Expected '('")

    depth = 0
    index = open_paren_index
    while index < len(expr):
        char = expr[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return expr[open_paren_index + 1 : index], index
        index += 1

    raise ValueError("Unbalanced parentheses")


def convert_member_calls(expr):
    """Convert JS method calls into runtime helper calls."""
    method_specs = [
        ("push", "js_push", True),
        ("pop", "js_pop", False),
        ("shift", "js_shift", False),
        ("unshift", "js_unshift", True),
        ("splice", "js_splice", True),
        ("reverse", "js_reverse", False),
        ("sort", "js_sort", True),
        ("join", "js_join", True),
        ("slice", "js_slice", True),
        ("concat", "js_concat", True),
        ("includes", "js_includes", True),
        ("indexOf", "js_index_of", True),
        ("split", "js_split", True),
        ("trim", "js_trim", False),
        ("replace", "js_replace", True),
        ("replaceAll", "js_replace_all", True),
        ("substring", "js_substring", True),
        ("startsWith", "js_starts_with", True),
        ("endsWith", "js_ends_with", True),
        ("toUpperCase", "js_to_upper_case", False),
        ("toLowerCase", "js_to_lower_case", False),
        ("map", "js_map", True),
        ("filter", "js_filter", True),
        ("reduce", "js_reduce", True),
        ("find", "js_find", True),
        ("some", "js_some", True),
        ("every", "js_every", True),
    ]

    changed = True
    while changed:
        changed = False
        for method_name, helper_name, has_args in method_specs:
            search_from = 0
            while True:
                if has_args:
                    marker = f".{method_name}("
                    dot_index = expr.find(marker, search_from)
                    if dot_index == -1:
                        break
                    receiver, recv_start = extract_receiver(expr, dot_index)
                    if receiver is None:
                        search_from = dot_index + 1
                        continue
                    open_paren = dot_index + len(method_name) + 1
                    args, close_paren = extract_parenthesized_content(expr, open_paren)
                    if args.strip():
                        converted = (
                            f"{helper_name}({convert_expression(receiver)}, "
                            f"{convert_call_arguments(args)})"
                        )
                    else:
                        converted = f"{helper_name}({convert_expression(receiver)})"
                    expr = expr[:recv_start] + converted + expr[close_paren + 1 :]
                else:
                    marker = f".{method_name}()"
                    dot_index = expr.find(marker, search_from)
                    if dot_index == -1:
                        break
                    receiver, recv_start = extract_receiver(expr, dot_index)
                    if receiver is None:
                        search_from = dot_index + 1
                        continue
                    converted = f"{helper_name}({convert_expression(receiver)})"
                    expr = expr[:recv_start] + converted + expr[dot_index + len(marker) :]

                changed = True
                break
            if changed:
                break

    return expr


def convert_literals(expr):
    """Convert JavaScript literals to Python values."""
    expr = re.sub(r"\bnew\s+Date\s*\(", "Date(", expr)
    expr = re.sub(r"\btrue\b", "True", expr)
    expr = re.sub(r"\bfalse\b", "False", expr)
    expr = re.sub(r"\bnull\b", "None", expr)
    expr = re.sub(r"\bundefined\b", "undefined", expr)
    return expr


def split_at_depth_zero(text, operator):
    """Split text on an operator that appears outside strings and parentheses."""
    parts = []
    current = []
    depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string = None
    index = 0
    op_len = len(operator)

    while index < len(text):
        char = text[index]

        if in_string:
            current.append(char)
            if char == "\\" and index + 1 < len(text):
                current.append(text[index + 1])
                index += 2
                continue
            if char == in_string:
                in_string = None
            index += 1
            continue

        if char in ("'", '"'):
            in_string = char
            current.append(char)
            index += 1
            continue

        if char == "(":
            depth += 1
            current.append(char)
            index += 1
            continue

        if char == ")":
            depth -= 1
            current.append(char)
            index += 1
            continue

        if char == "[":
            bracket_depth += 1
            current.append(char)
            index += 1
            continue

        if char == "]":
            bracket_depth -= 1
            current.append(char)
            index += 1
            continue

        if char == "{":
            brace_depth += 1
            current.append(char)
            index += 1
            continue

        if char == "}":
            brace_depth -= 1
            current.append(char)
            index += 1
            continue

        if depth == 0 and bracket_depth == 0 and brace_depth == 0 and text.startswith(operator, index):
            parts.append("".join(current))
            current = []
            index += op_len
            continue

        current.append(char)
        index += 1

    parts.append("".join(current))
    return parts
