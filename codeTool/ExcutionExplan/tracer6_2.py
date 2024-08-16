"""
Processed empty files (input of zero) and ellipses

Converted {i:0} to i=0

Handled variable space issue: script_globals = {"__builtins__": __builtins__}

Addressed the issue of missing step comments in custom functions
Based on tracer4.py, modified the code to properly handle data types like lists, tuples, and dictionaries (deep copy)
Based on tracer5.py, added remove_comments and format_float functions to remove comments and format floating-point numbers. Improved the method for comparing current variables with previous variables and enhanced the formatting output variable comments method.
"""

import sys
import ast
import copy
import re
import numpy as np

step_counter = 0
pre_line = ""
pre_line_no = 0

custom_functions = []

def trace_lines(frame, event, arg):
    global step_counter, pre_line, pre_line_no
    if event != "line":
        return trace_lines
    co = frame.f_code
    func_name = co.co_name
    line_no = frame.f_lineno
    filename = co.co_filename
    if filename != "<string>":
        return trace_lines

    try:
        with open(target_script, "r", encoding='utf-8') as file:
            lines = file.readlines()
            current_line = lines[line_no - 1].strip()

    except Exception as e:
        current_line = f"<unable to read line: {e}>"

    if "import " in current_line or "return " in current_line:
        return trace_lines

    if func_name == "<module>" or func_name in custom_functions:

        last_locals = getattr(trace_lines, 'last_locals', {})
        current_locals = frame.f_locals.copy()
        for each in frame.f_locals:
            if isinstance(frame.f_locals[each], (dict,set,list,tuple)):
                current_locals[each] = copy.deepcopy(frame.f_locals[each])

        last_line_no = getattr(trace_lines, 'last_line_no', None)

        # changed_vars = {}
        # for var, value in current_locals.items():
        #     if var not in last_locals or last_locals[var] != value:
        #         changed_vars[var] = value
        # changed_vars = delete_dict(changed_vars)
        changed_vars = {}
        for var, value in current_locals.items():
            if var not in last_locals or not np.array_equal(last_locals[var], value):
                changed_vars[var] = value
        changed_vars = delete_dict(changed_vars)

        #----------------------------------------------
        if step_counter != 0:
            formatted_changed_vars = {key: format_float(value) for key, value in changed_vars.items()}
            if formatted_changed_vars:
                print(f"Step {step_counter-1}: Function {func_name} Line {pre_line_no} {pre_line}: Variables changed - {formatted_changed_vars}")
            else:
                print(f"Step {step_counter-1}: Function {func_name} Line {pre_line_no} {pre_line}: NO CHANGE")
            
            note_exegesis(step_counter-1, pre_line_no, formatted_changed_vars)
        # ---------------------------------------------------------------------------------------
        pre_line = current_line
        pre_line_no = line_no

        step_counter += 1

        trace_lines.last_locals = current_locals
        trace_lines.last_line_no = line_no
    return trace_lines
def delete_dict(d):
    current_script_arg = ['filename', 'input_file', 'file', 'input_data', 'script_content']

    for key in current_script_arg:
        if key in d:
            del d[key]
    return d

update_dict = {}
def note_exegesis(step, lines_no, change_value):
    if lines_no not in update_dict:
        update_dict[lines_no] = []
    if len(change_value) == 0:
        change_value = "NO CHANGE"
    update_dict[lines_no].append((step, change_value))

def format_vars(changed_vars):
    formatted_vars = []
    for key, value in changed_vars.items():
        value_str = str(value).replace('\n', ' ')
        formatted_vars.append(f"{key}={value_str}")
    return ", ".join(formatted_vars)

def add_comment_to_source(filename, update_dict):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines = remove_comments(lines)
    
    for line_no, changes in update_dict.items():
        try:
            lines[line_no-1] = lines[line_no-1].rstrip("\n")
            formatted_changes = [f"({step}): {format_vars(change)}" if change != "NO CHANGE" else f"({step}): NO CHANGE" for step, change in changes]

            if len(formatted_changes) > 3:
                formatted_changes = formatted_changes[:2] + ["..."] + [formatted_changes[-1]]
            comment = " # " + " ".join(formatted_changes)
            lines[line_no-1] += comment + "\n"
        except IndexError as e:
            print(f"Error: Unable to modify line {line_no - 1} due to IndexError: {e}")

    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def add_comment_to_new_file(original_filename, update_dict):
    new_filename = "annotated_" + original_filename
    with open(original_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines = remove_comments(lines)
    
    for line_no, changes in update_dict.items():
        try:
            lines[line_no-1] = lines[line_no-1].rstrip("\n")
            formatted_changes = [f"({step}): {format_vars(change)}" if change != "NO CHANGE" else f"({step}): NO CHANGE" for step, change in changes]
            if len(formatted_changes) > 3:
                formatted_changes = formatted_changes[:2] + ["..."] + [formatted_changes[-1]]
            comment = " # " + " ".join(formatted_changes)
            lines[line_no-1] += comment + "\n"
        except IndexError as e:
            print(f"Error: Unable to modify line {line_no - 1} due to IndexError: {e}")

    with open(new_filename, 'w', encoding='utf-8') as new_file:
        new_file.writelines(lines)
    print(f"Annotated file created: {new_filename}")

def run_script(filename, input_file):
    print("start")
    script_globals = {"__builtins__": __builtins__}
    
    with open(filename, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            custom_functions.append(node.name)
    
    with open(filename, 'r', encoding='utf-8') as file:
        script_content = file.read()
    if input_file is not None:
        with open(input_file, 'r', encoding='utf-8') as input_data:
            sys.stdin = input_data
            exec(script_content, script_globals)
            sys.stdin = sys.__stdin__
    else:
        exec(script_content, script_globals)

def remove_comments(code):
    if isinstance(code, list):
        return [re.sub(r'#.*$', '', line, flags=re.MULTILINE) for line in code]
    else:
        return re.sub(r'#.*$', '', code, flags=re.MULTILINE)

def format_float(value):
   if isinstance(value, float) and '.' in str(value):
        split_value = str(value).split('.')
        if len(split_value) > 1 and len(split_value[1]) > 6:
            formatted_value = "{:.6f}".format(float(value)).rstrip('0').rstrip('.')
            return formatted_value if formatted_value else '0'
   return value

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tracer.py <script_to_trace.py> [<input_file>]")
    else:
        target_script = sys.argv[1]
        input_file = sys.argv[2] if len(sys.argv) > 2 else None
        sys.settrace(trace_lines)
        run_script(target_script, input_file)
        sys.settrace(None)
        #add_comment_to_source(target_script, update_dict)
        add_comment_to_new_file(target_script, update_dict)