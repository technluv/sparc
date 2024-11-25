import os
import fnmatch

def read_gitignore(root_dir):
    print("Reading .gitignore")
    gitignore_path = os.path.join(root_dir, '.gitignore')
    ignored_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    if stripped_line.endswith('/'):
                        ignored_patterns.append(f"{stripped_line}*")
                    else:
                        ignored_patterns.append(stripped_line)
    print(f"Ignored patterns: {ignored_patterns}")
    return ignored_patterns

def get_folder_structure(root_dir):
    print("Getting folder structure")
    folder_structure = []
    for root, dirs, files in os.walk(root_dir):
        level = root.replace(root_dir, '').count(os.sep)
        folder_structure.append((root, level))
    return folder_structure

def find_max_nesting(folder_structure):
    print("Finding maximum nesting level")
    max_nesting = max(level for _, level in folder_structure)
    return max_nesting

def should_ignore(file_path, ignored_patterns, script_name):
    additional_ignored_files = ['README.md', 'create.sh']
    if file_path == script_name or os.path.basename(file_path) in additional_ignored_files:
        return True
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    return False

def list_files_with_contents(root_dir, script_name):
    print("Listing files with contents")
    ignored_patterns = read_gitignore(root_dir)
    file_data = []
    folder_structure = get_folder_structure(root_dir)
    max_nesting = find_max_nesting(folder_structure)
    file_data.append(f"Maximum level of nesting: {max_nesting}\n\nFolder Structure:\n")

    # Add folder structure with indentation for levels
    for folder, level in folder_structure:
        indent = '    ' * level
        folder_name = os.path.basename(folder) if os.path.basename(folder) else folder
        file_data.append(f"{indent}- {folder_name}/")

    file_data.append("\n\nFiles with Contents:\n")
    for root, dirs, files in os.walk(root_dir):
        # Exclude directories that match ignored patterns
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(os.path.relpath(os.path.join(root, d), root_dir), pattern) for pattern in ignored_patterns)]
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), root_dir)
            if not should_ignore(relative_path, ignored_patterns, script_name):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    file_data.append(f"### {relative_path} ###\n{content}\n\n")
                    print(f"Processed file: {relative_path}")
                except Exception as e:
                    file_data.append(f"### {relative_path} ###\nError reading file: {e}\n\n")
                    print(f"Error reading file {relative_path}: {e}")
    return file_data

def main():
    root_dir = "/workspaces/sparc/fun" # You can specify a different directory here
    script_name = os.path.basename(__file__)
    print(f"Script name: {script_name}")
    files_with_contents = list_files_with_contents(root_dir, script_name)
    result = '\n'.join(files_with_contents)
    output_file = 'output.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"File list with contents has been written to {output_file}.")

if __name__ == "__main__":
    main()

