#!/usr/bin/env python3

import subprocess
import time
import sys
import os
import re

CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),"cleanup-actions.txt")

def find_similar_files(folder):
    files = os.listdir(folder)
    # Pattern to match content within parentheses or brackets at the end of the filename, before the extension
    pattern = re.compile(r'(.*?)(\s*\((\d+)\)|\s*\[(\d+)\])?$')

    file_dict = {}

    for file in files:
        if not os.path.isfile(os.path.join(folder, file)):
            continue

        # Split filename into name and extension
        base_name, extension = os.path.splitext(file)

        # Match the base name with the pattern
        match = pattern.match(base_name)
        if match:
            normalized_name = match.group(1).strip() + extension

            if normalized_name in file_dict:
                file_dict[normalized_name].append(file)
            else:
                file_dict[normalized_name] = [file]

    return file_dict

def open_config_file(file_path):
    if sys.platform == 'win32':
        os.startfile(file_path)  # Windows
    elif sys.platform == 'darwin':
        subprocess.run(['open', file_path])  # macOS
    else:
        subprocess.run(['xdg-open', file_path])  # Linux

def add_actions_to_config(file_dict, folder):
    action_info = [
        "Info: The keys set in this files have to be exact",
        "Info: Lines like this with 'Info:' can be used for comments",
        "Info: Also they can be set to 'Naming:' and 'Deleting:'",
        "Info: Any 'Naming:' entrys will be renamed to the earlyest avalible file name",
        "Info: So 'Naming: test (4).txt' will be renamed to 'test.txt'",
        "Info: If that file is there 1 gets added in parentheses at the end",
        "Info: So the next one would be 'test (1).txt' then 'test (2).txt' and so on",
        "Info: Remove any arguments from the started python file to run this action file"
    ]
    actions = []
    for base_name, file_list in file_dict.items():
        if len(file_list) > 1:
            # Sort files by modification time, keep the latest one
            file_list.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
            latest_file = file_list[0]
            file_path = os.path.join(folder, latest_file)
            naming_action = f"Naming: {file_path}"

            # Prepare actions
            for file in file_list[1:]:
                file_path = os.path.join(folder, file)
                action = f"Deleting: {file_path}"
                actions.append(action)

            actions.append(naming_action)

    # Write actions to config file if not present
    if actions:
        actions = action_info + actions
        existing_actions = set()
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                existing_actions = set(line.strip() for line in f)

        with open(CONFIG_FILE, 'a') as f:
            for action in actions:
                if action.strip() not in existing_actions:
                    f.write(f"{action.strip()}\n")
        print(f"Actions added to '{CONFIG_FILE}'")

        # Open the config file using the default application
        open_config_file(CONFIG_FILE)
    else:
        print(f"No file duplicates found in the folder '{folder}'")

def normalize_and_rename_file(file_path):
    folder, file_name = os.path.split(file_path)
    base_name, extension = os.path.splitext(file_name)

    # Remove any numbering or brackets from the base name
    normalized_base_name = re.sub(r'\s*\(\d+\)\s*|\s*\[\d+\]\s*', '', base_name).strip()
    normalized_name = f"{normalized_base_name}{extension}"
    new_path = os.path.join(folder, normalized_name)
    new_paths = [new_path, "", "", ""]

    # Handle conflicts by appending a suffix if necessary
    if os.path.exists(new_path):
        i = 1
        while True:
            new_paths[0] = os.path.join(folder, f"{normalized_base_name} ({i}){extension}")
            new_paths[1] = os.path.join(folder, f"{normalized_base_name}({i}){extension}")
            new_paths[2] = os.path.join(folder, f"{normalized_base_name} [{i}]{extension}")
            new_paths[3] = os.path.join(folder, f"{normalized_base_name}[{i}]{extension}")
            if not any([path for path in new_paths if os.path.exists(path)]):
                break
            i += 1

    os.rename(file_path, new_paths[0])
    print(f"Renamed: {file_path} -> {new_paths[0]}")


def select_folder():
    import tkinter as tk
    from tkinter import filedialog
    # Create a Tk root widget, which is necessary to use filedialog.
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open the folder selection dialog and return the selected folder path.
    folder_path = False
    while folder_path == False or (folder_path and not os.path.isdir(folder_path)):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            folder_path = None

    if folder_path:
        print(f"Selected folder '{folder_path}'")
    return folder_path

def execute_config_file():
    if os.path.exists(CONFIG_FILE):
        print(f"Executing tasks from '{CONFIG_FILE}'")
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                command = line.strip()
                if command.startswith("Deleting:"):
                    file_path = command[len("Deleting:"):].strip()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                elif command.startswith("Naming:"):
                    file_name = command[len("Naming:"):].strip()
                    normalize_and_rename_file(file_name)
                elif command.startswith("Info:"):
                    info = command[len("Info:"):].strip()
                    print("Info: " + info)
                else:
                    print(f"Unknown command: {command}")
        os.remove(CONFIG_FILE)
    else:
        return f"No action file found at '{CONFIG_FILE}'\nYou can use the target folder as argument, to the script to generate the action file, if tk is missing or for automation"
    return None

def main(folder, purecli):
    returnmessage = None
    if not folder:
        returnmessage = execute_config_file()


    if purecli == False and not folder and returnmessage:
        try:
            folder = select_folder()
        except Exception as e:
            print("Tk not avalible, can't display a folder selection.")
            folder = None
        else:
            if not folder:
                print("Folder selcetion was not valid")
    elif purecli == True:
        print("CLI mode used, not displaying any tk windows")

    if not folder:
        if returnmessage:
            print(returnmessage)
    else:
        if not os.path.isdir(folder):
            print(f"The folder '{folder}' is not a directory.")
            time.sleep(2)
            sys.exit(1)

        similar_files = find_similar_files(folder)
        add_actions_to_config(similar_files, folder)

if __name__ == "__main__":
    folder = None
    purecli = False
    for i in sys.argv[1:]:
        if i.find(os.sep) == -1 and "cli" in i:
            purecli = True
        elif os.path.isdir(i):
            folder = i
    if folder:
        print(f"Found following folder in cli '{folder}'")
    main(folder, purecli)
    time.sleep(2)
