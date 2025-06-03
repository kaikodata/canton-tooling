#!/usr/bin/env python3
import os
import re
import shutil
import logging
import sys
from pathlib import Path
import yaml
import argparse

def setup_logging(debug):
    """Set up logging based on debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s:%(message)s')

def load_env_vars(env_file_path):
    """Load environment variables from a file into a dictionary."""
    env_vars = {}
    if not os.path.isfile(env_file_path):
        logging.error(f"Environment file {env_file_path} does not exist or is not a file")
        print(f"ERROR: Environment file {env_file_path} does not exist or is not a file")
        return env_vars
    
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                    except ValueError:
                        logging.warning(f"Skipping invalid line in {env_file_path}: {line}")
        logging.debug(f"Loaded environment variables from {env_file_path}: {env_vars}")
        if not env_vars:
            logging.warning(f"Environment file {env_file_path} is empty")
            print(f"WARNING: Environment file {env_file_path} is empty")
        return env_vars
    except Exception as e:
        logging.error(f"Failed to read environment file {env_file_path}: {e}")
        print(f"ERROR: Failed to read environment file {env_file_path}: {e}")
        return env_vars

def replace_vars_in_string(text, env_vars):
    """Replace all occurrences of env vars in a string with their values."""
    original_text = text
    replaced = False
    for key, value in env_vars.items():
        pattern = re.escape(key)
        if re.search(pattern, text):
            logging.debug(f"Replacing variable '{key}' with '{value}' in text: {text}")
            text = re.sub(pattern, value, text)
            replaced = True
    if not replaced and env_vars:
        logging.debug(f"No variables replaced in text: {original_text}")
    return text

def get_non_template_alias(chart_yaml_path):
    """Extract the alias from Chart.yaml dependencies where alias is not 'template'."""
    try:
        logging.debug(f"Opening Chart.yaml at {chart_yaml_path} for alias extraction")
        with open(chart_yaml_path, 'r', encoding='utf-8') as f:
            chart_data = yaml.safe_load(f)
        
        if not isinstance(chart_data, dict):
            logging.warning(f"Invalid Chart.yaml format in {chart_yaml_path}: not a dictionary")
            print(f"WARNING: Invalid Chart.yaml format in {chart_yaml_path}: not a dictionary")
            return None
        
        dependencies = chart_data.get('dependencies', [])
        if not isinstance(dependencies, list):
            logging.warning(f"No valid dependencies in {chart_yaml_path} for alias extraction")
            print(f"WARNING: No valid dependencies in {chart_yaml_path} for alias extraction")
            return None
        
        logging.debug(f"Found dependencies for alias extraction: {dependencies}")
        for dep in dependencies:
            if not isinstance(dep, dict):
                logging.warning(f"Invalid dependency entry in {chart_yaml_path} for alias extraction: {dep}")
                continue
            alias = dep.get('alias')
            logging.debug(f"Considering alias '{alias}' in {chart_yaml_path}")
            if alias and alias.strip() and alias != 'template':
                logging.debug(f"Selected alias '{alias}' from {chart_yaml_path}")
                return alias
        logging.warning(f"No non-template alias found in {chart_yaml_path}")
        print(f"WARNING: No non-template alias found in {chart_yaml_path}")
        return None
    except Exception as e:
        logging.error(f"Failed to parse Chart.yaml at {chart_yaml_path} for alias extraction: {e}")
        print(f"ERROR: Failed to parse Chart.yaml at {chart_yaml_path} for alias extraction: {e}")
        return None

def process_yaml_content(src_path, dest_path, env_vars, alias=None, alias_prefix=False):
    """Process YAML file content, replacing env vars, optionally adding alias prefix, ensuring --- at start, and trimming trailing whitespace."""
    try:
        with open(src_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Failed to read YAML file {src_path}: {e}")
        return
    
    new_lines = []
    for line in lines:
        var_found = None
        var_start = None
        for key in env_vars:
            pattern = re.escape(key)
            match = re.search(pattern, line)
            if match:
                var_found = key
                var_start = match.start()
                break
        
        if var_found:
            before_var = line[:var_start]
            if '#' in before_var:
                new_lines.append(line)
            else:
                new_line = replace_vars_in_string(line, env_vars)
                logging.debug(f"Replacing line with variable '{var_found}' in {src_path}: {line.strip()} -> {new_line.strip()}")
                new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    # Trim trailing whitespace while preserving empty lines
    new_lines = [line.rstrip() + '\n' for line in new_lines]
    logging.debug(f"Trimmed trailing whitespace in {dest_path}")
    
    if alias and alias_prefix:
        logging.debug(f"Applying alias prefix '{alias}' to {dest_path}")
        indented_lines = ['  ' + line if line.strip() else line for line in new_lines]
        new_lines = [f'{alias}:\n'] + indented_lines
    elif alias_prefix:
        logging.debug(f"No alias available for prefixing in {dest_path}")
    
    # Ensure --- at start
    if not new_lines or not new_lines[0].strip().startswith('---'):
        logging.debug(f"Adding --- document start marker to {dest_path}")
        new_lines.insert(0, '---\n')
    else:
        logging.debug(f"Document start marker --- already present in {dest_path}")
    
    try:
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception as e:
        logging.error(f"Failed to write YAML file {dest_path}: {e}")

def process_file_content(src_path, dest_path, env_vars):
    """Process non-YAML file content, replacing env vars."""
    try:
        with open(src_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Failed to read file {src_path}: {e}")
        return
    
    new_lines = []
    for line in lines:
        var_found = None
        var_start = None
        for key in env_vars:
            pattern = re.escape(key)
            match = re.search(pattern, line)
            if match:
                var_found = key
                var_start = match.start()
                break
        
        if var_found:
            before_var = line[:var_start]
            if '#' in before_var:
                new_lines.append(line)
            else:
                new_line = replace_vars_in_string(line, env_vars)
                logging.debug(f"Replacing line with variable '{var_found}' in {src_path}: {line.strip()} -> {new_line.strip()}")
                new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    try:
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception as e:
        logging.error(f"Failed to write file {dest_path}: {e}")

def find_git_repo(start_path):
    """Find the Git repository root by searching for .git directory."""
    current = Path(start_path).resolve()
    while current != current.parent:
        if (current / '.git').is_dir():
            return current
        current = current.parent
    return None

def update_gitignore(gitignore_path, new_entries):
    """Append new entries to .gitignore, avoiding duplicates."""
    existing_entries = set()
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_entries = {line.strip().rstrip('/') for line in f if line.strip() and not line.startswith('#')}
    
    with open(gitignore_path, 'a', encoding='utf-8') as f:
        if existing_entries:
            f.write('\n')
        f.write('# Generated by canton-templating.py\n')
        for entry in sorted(new_entries):
            clean_entry = entry.rstrip('/')
            if clean_entry not in existing_entries:
                f.write(clean_entry + '\n')

def process_directory(src_dir, dest_dir, env_file, debug=False, alias_prefix=False, use_gitignore=False, process_ext='yaml'):
    """Process files and directories, replacing env vars, handling aliases, creating symlinks, and updating .gitignore."""
    setup_logging(debug)
    env_vars = load_env_vars(env_file)
    if not env_vars:
        logging.error(f"No environment variables loaded; substitutions will be skipped")
        print(f"ERROR: No environment variables loaded; substitutions will be skipped")
    
    # Normalize process_ext to list of extensions with leading dot
    process_extensions = []
    for ext in process_ext.split(','):
        ext = ext.strip().lower()
        if not ext:
            logging.warning(f"Ignoring empty extension in --process-ext")
            continue
        if '.' in ext:
            logging.warning(f"Ignoring invalid extension '{ext}' in --process-ext (contains dot)")
            continue
        process_extensions.append(f'.{ext}')
    
    if not process_extensions:
        logging.error(f"No valid extensions provided in --process-ext; defaulting to '.yaml'")
        process_extensions = ['.yaml']
    
    for symlink_path in Path(dest_dir).rglob('*'):
        if symlink_path.is_symlink():
            symlink_path.unlink()
            logging.debug(f"Removed existing symlink: {symlink_path}")
    
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    
    dir_mapping = {}
    created_symlinks = set()
    symlink_targets = set()
    
    src_dir_resolved = Path(src_dir).resolve()
    if not src_dir_resolved.is_dir():
        logging.error(f"Source directory {src_dir} does not exist or is not a directory")
        print(f"ERROR: Source directory {src_dir} does not exist or is not a directory")
        return
    
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        logging.debug(f"Processing directory: {root}, relative path: {rel_path}")
        new_root = dest_dir if rel_path == '.' else os.path.join(dest_dir, replace_vars_in_string(rel_path, env_vars))
        Path(new_root).mkdir(parents=True, exist_ok=True)
        
        dir_mapping[new_root] = os.path.basename(root)
        
        alias = None
        chart_yaml_path = Path(root) / 'Chart.yaml'
        logging.debug(f"Checking for Chart.yaml at {chart_yaml_path} for alias extraction")
        if chart_yaml_path.is_file():
            alias = get_non_template_alias(chart_yaml_path)
            logging.debug(f"Using alias '{alias}' for directory {root}")
        else:
            for chart_file in Path(root).glob('[Cc][Hh][Aa][Rr][Tt].[Yy][Aa][Mm][Ll]'):
                logging.debug(f"Found case-variant Chart.yaml: {chart_file} for alias extraction")
                alias = get_non_template_alias(chart_file)
                if alias:
                    logging.debug(f"Using alias '{alias}' for directory {root}")
                    break
            if not alias:
                logging.debug(f"No Chart.yaml found in {root}; no alias will be applied to YAML files")
        
        for file in files:
            src_file = os.path.join(root, file)
            new_filename = replace_vars_in_string(file, env_vars)
            dest_file = os.path.join(new_root, new_filename)
            logging.debug(f"Processing file: {src_file} -> {dest_file}")
            
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in process_extensions:
                if file_ext == '.yaml':
                    if file == 'secrets-clear.yaml':
                        logging.debug(f"Processing secrets-clear.yaml at {src_file} with substitutions only")
                        process_yaml_content(src_file, dest_path=dest_file, env_vars=env_vars, alias=None, alias_prefix=False)
                        # Add to .gitignore
                        relative_file_path = os.path.relpath(dest_file, dest_dir)
                        symlink_targets.add(relative_file_path)
                    elif file in ('Chart.yaml', 'values.yaml'):
                        logging.debug(f"Processing {file} at {src_file} without alias prefix")
                        process_yaml_content(src_file, dest_path=dest_file, env_vars=env_vars)
                    else:
                        logging.debug(f"Processing YAML file {src_file} with potential alias prefix '{alias}'")
                        process_yaml_content(src_file, dest_path=dest_file, env_vars=env_vars, alias=alias, alias_prefix=alias_prefix)
                else:
                    process_file_content(src_file, dest_path=dest_file, env_vars=env_vars)
            else:
                logging.debug(f"Copying non-processed file {src_file} to {dest_file}")
                shutil.copy2(src_file, dest_file)
    
    processed_dirs = set()
    for root, dirs, _ in os.walk(dest_dir, topdown=False, followlinks=False):
        for dir_name in dirs:
            old_dir_path = os.path.join(root, dir_name)
            if old_dir_path in processed_dirs:
                continue
            
            src_dir_name = dir_mapping.get(old_dir_path, dir_name)
            new_dir_name = replace_vars_in_string(src_dir_name, env_vars)
            new_dir_path = os.path.join(root, new_dir_name)
            logging.debug(f"Processing directory rename: {old_dir_path} -> {new_dir_path}")
            
            if old_dir_path != new_dir_path:
                shutil.move(old_dir_path, new_dir_path)
            
            if src_dir_name != new_dir_name:
                symlink_path = os.path.join(root, src_dir_name)
                if symlink_path in created_symlinks:
                    continue
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                relative_target = os.path.basename(new_dir_path)
                try:
                    os.symlink(relative_target, symlink_path)
                    relative_symlink_path = os.path.relpath(symlink_path, dest_dir)
                    symlink_targets.add(relative_symlink_path)
                    created_symlinks.add(symlink_path)
                    logging.debug(f"Created symlink: {symlink_path} -> {relative_target}")
                except OSError as e:
                    logging.error(f"Failed to create symlink: {symlink_path}: {e}")
            
            processed_dirs.add(old_dir_path)
            processed_dirs.add(new_dir_path)
    
    if use_gitignore:
        git_repo = find_git_repo(dest_dir)
        if git_repo:
            gitignore_path = git_repo / '.gitignore'
            gitignore_entries = {os.path.join(os.path.relpath(dest_dir, git_repo), target.rstrip('/')) for target in symlink_targets}
            update_gitignore(gitignore_path, gitignore_entries)
            logging.debug(f"Updated Git repository .gitignore at {gitignore_path}")
        else:
            logging.error(f"No Git repository found; falling back to creating .gitignore in destination directory")
            gitignore_path = os.path.join(dest_dir, '.gitignore')
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write('# Automatically generated by canton-templating.py\n')
                for target in sorted(symlink_targets):
                    f.write(target + '\n')
            logging.debug(f"Created .gitignore at {gitignore_path}")
    else:
        gitignore_path = os.path.join(dest_dir, '.gitignore')
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write('# Automatically generated by canton-templating.py\n')
            for target in sorted(symlink_targets):
                f.write(target + '\n')
        logging.debug(f"Created .gitignore at {gitignore_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Process templates with environment variables, Chart.yaml aliases, symlinks, and .gitignore.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Mandatory arguments:
  src_dir             Source directory containing templates
  dest_dir            Destination directory for processed templates
  env_file            File containing environment variables

Optional arguments:
  -h, --help          Show this help message and exit
  --debug             Enable debug logging for string substitutions (default: False)
  --alias-prefix      Add prefix (e.g., global-domain:) and reindent YAML files, excluding Chart.yaml, values.yaml, and secrets-clear.yaml (default: False)
  --use-gitignore     Update the Git repository's .gitignore instead of creating one in dest_dir (default: False)
  --process-ext       Comma-separated list of file extensions to process for substitutions (default: yaml)
'''
    )
    parser.add_argument('src_dir', help='Source directory containing templates')
    parser.add_argument('dest_dir', help='Destination directory for processed templates')
    parser.add_argument('env_file', help='File containing environment variables')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging for string substitutions')
    parser.add_argument('--alias-prefix', action='store_true', help='Add prefix (e.g., global-domain:) and reindent YAML files, excluding Chart.yaml, values.yaml, and secrets-clear.yaml')
    parser.add_argument('--use-gitignore', action='store_true', help='Update the Git repository\'s .gitignore instead of creating one in dest_dir')
    parser.add_argument('--process-ext', default='yaml', help='Comma-separated list of file extensions to process for substitutions (default: yaml)')
    
    logging.debug(f"Raw command-line arguments: {sys.argv}")
    try:
        args, unknown = parser.parse_known_args()
        if unknown:
            logging.error(f"Unrecognized arguments: {unknown}")
            parser.print_help()
            sys.exit(2)
    except SystemExit as e:
        logging.error(f"Argument parsing failed: {e}")
        sys.exit(e.code)
    
    process_directory(
        args.src_dir,
        args.dest_dir,
        args.env_file,
        debug=args.debug,
        alias_prefix=args.alias_prefix,
        use_gitignore=args.use_gitignore,
        process_ext=args.process_ext
    )

if __name__ == '__main__':
    main()
