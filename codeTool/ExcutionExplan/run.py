import sys

def trace_lines(frame, event, arg):
    if event == "line":
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename
        with open(filename, "r") as file:
            lines = file.readlines()
            current_line = lines[line_no - 1].strip()
            
        locals_copy = frame.f_locals.copy()
        #print(f"Function {func_name} Line {line_no}: {locals_copy}")
        print(f"{func_name} Line {line_no}: {current_line} | Locals: {frame.f_locals}")
    return trace_lines

def activate_tracer():
    sys.settrace(trace_lines)

def deactivate_tracer():
    sys.settrace(None)

def test_function(x):
    for i in range(2):
        y = x + 10
        z = y * 2
        x += 5
    return z

activate_tracer()
result = test_function(5)
deactivate_tracer()

print(f"Result: {result}")
