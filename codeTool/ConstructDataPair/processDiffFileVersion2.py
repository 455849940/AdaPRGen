import os
import json
import subprocess
import re

def check_git_repo(path):
    try:
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0 and result.stdout.strip() == 'true'
    except Exception as e:
        return False

def read_json(json_name):
    with open(json_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_temp_file(entry, output='output'):
    user_id = entry['user_id']
    problem_id = entry['problem_id']
    
    code1 = entry['code1']
    code2 = entry['code2']

    os.makedirs(f"{output}/{problem_id}", exist_ok=True)
    
    code1_filename = os.path.join(f"{output}/{problem_id}", f'{user_id}_{problem_id}_code1.py')
    code2_filename = os.path.join(f"{output}/{problem_id}", f'{user_id}_{problem_id}_code2.py')

    with open(code1_filename, 'w') as code1_file:
        code1_file.write(code1)
        code1_file.write('\n')
    
    with open(code2_filename, 'w') as code2_file:
        code2_file.write(code2)
        code2_file.write('\n')
    
    print(f'************Saved {user_id} code1 to {code1_filename}************')
    print(f'************Saved {user_id} code2 to {code2_filename}************')

    return code1_filename, code2_filename

def git_diff_file(code1_filename, code2_filename, output='output_txt', output_indicator_new='+', output_indicator_old='-'):
    os.makedirs(output, exist_ok=True)
    
    code1_filename = os.path.abspath(code1_filename)
    code2_filename = os.path.abspath(code2_filename)
    output = os.path.abspath(output)
    
    subprocess.run(['git', 'add', code1_filename], cwd=output)
    subprocess.run(['git', 'add', code2_filename], cwd=output)
    subprocess.run(['git', 'commit', '-m', f'Add {code1_filename} and {code2_filename}'], cwd=output, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    user_id = code1_filename.split('/')[-1].split('_')[0]
    problem_id = code1_filename.split('/')[-1].split('_')[1]
    problem_output_dir = os.path.join(output, problem_id)
    os.makedirs(problem_output_dir, exist_ok=True)
    
    output_filename = os.path.join(problem_output_dir, f'{user_id}_{problem_id}.txt')
    
    git_diff_command = [
        'git', 'diff', '--unified=1024', '--no-index', code1_filename, code2_filename,
        f'--output-indicator-new={output_indicator_new}',
        f'--output-indicator-old={output_indicator_old}'
    ]
    
    sed_command = "sed 's/^\(@@.*@@\) /\\1\\n/'"
    
    with open(output_filename, 'w') as output_file:
        process1 = subprocess.Popen(git_diff_command, stdout=subprocess.PIPE, cwd=output)
        process2 = subprocess.Popen(sed_command, stdin=process1.stdout, stdout=output_file, shell=True)
        process1.stdout.close()
        process2.communicate()
    
    return output_filename    

def process_diff_file(input_file, output_file, new_indicator="+", old_indicator="-"):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        added_line_written = False

        for _ in range(4):
            next(infile)

        for line in infile:
            if line.startswith("+++"):
                outfile.write(line)
                continue
            
            if line.startswith("@@"):
                continue

            if line.startswith(new_indicator):
                if not added_line_written:
                    # outfile.write(new_indicator + '\n')
                    outfile.write('<+>' + '\n')
                    added_line_written = True

            elif line.startswith(old_indicator):
                continue
            else:
                outfile.write(line)
                added_line_written = False

def dispose_file(data, output='output', output_indicator_new='+', output_indicator_old='-'):
    output = os.path.abspath(output)
    os.makedirs(output, exist_ok=True)

    if not check_git_repo(output):
        subprocess.run(['git', 'init'], cwd=output)
        current_file_path = __file__
        current_file_name = os.path.basename(current_file_path)
        destination_path = os.path.join(output, current_file_name)
        with open(current_file_path, 'r') as source_file:
            with open(destination_path, 'w') as dest_file:
                dest_file.write(source_file.read())
        subprocess.run(['git', 'add', current_file_name], cwd=output)
        subprocess.run(['git', 'commit', '-m', 'Initialize repository'], cwd=output)

    for i, entry in enumerate(data):
        code1_filename, code2_filename = save_temp_file(entry=entry, output=output)
        problem_id = entry["problem_id"]
        output_filename = git_diff_file(code1_filename=code1_filename, code2_filename=code2_filename, output=f"{output}/output_txt", output_indicator_new=output_indicator_new, output_indicator_old=output_indicator_old)
        final_output_filename = os.path.join(output, problem_id, f'{output_filename.split("/")[-1].split(".")[0]}_processed.txt')
        process_diff_file(input_file=output_filename, output_file=final_output_filename, new_indicator=output_indicator_new, old_indicator=output_indicator_old)
        subprocess.run(['git', 'rm', code1_filename], cwd=output)
        subprocess.run(['git', 'rm', code2_filename], cwd=output)
        subprocess.run(['git', 'commit', '-m', f'Remove {code1_filename} and {code2_filename}'], cwd=output)


def add_empty_line_to_file(filename):
    with open(filename, 'a') as file:
        file.write('\n')

def remove_last_empty_line(file_path):
    """
     Open the file and remove the last empty line (if it exists)
    :param file_path: Path to the file
    """
    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = file.readlines()
            if not lines:
                print("The file is empty.")
                return

            if lines[-1].strip() == '':
                lines = lines[:-1]
            
            file.seek(0)
            file.truncate()
            file.writelines(lines)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except IOError as e:
        print(f"Error reading/writing file '{file_path}': {e}")
       
def get_diff_stats(code1_filename, code2_filename):
    code1_filename = os.path.abspath(code1_filename)
    code2_filename = os.path.abspath(code2_filename)

    add_empty_line_to_file(code1_filename)
    add_empty_line_to_file(code2_filename)

    result = subprocess.run(
        ['git', 'diff', '--no-index', '--shortstat', code1_filename, code2_filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = result.stdout.strip()
    
    insertions = re.search(r'(\d+) insertions?\(\+\)', output)
    deletions = re.search(r'(\d+) deletions?\(-\)', output)
    
    added_lines = int(insertions.group(1)) if insertions else 0
    removed_lines = int(deletions.group(1)) if deletions else 0
    
    remove_last_empty_line(code1_filename)
    remove_last_empty_line(code2_filename)

    return added_lines, removed_lines

def get_file_line_count(file_path):
    """
    Count the number of lines in the file
    :param file_path: Path to the file
    :return: Number of lines in the file; returns 0 if the file does not exist or fails to read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return 0
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")
        return 0

if __name__ == '__main__':
    json_name = 'test.json'
    data = read_json(json_name)
    dispose_file(data, output='output', output_indicator_old='-', output_indicator_new='+')
    added_lines,removed_lines= get_diff_stats('test1.py', 'test2.py')
    print(f'Added lines: {added_lines}')
    print(f'Removed lines: {removed_lines}')
    line = get_file_line_count('test1.py')
    print(line)


