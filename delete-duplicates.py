#!/usr/bin/env python3

import subprocess
import time
import sys
import os
import re

if getattr(sys, 'frozen', False):  # Check if running as a compiled executable
    script_path = os.path.abspath(sys.executable)
else:  # Running as a regular Python script
    script_path = os.path.abspath(__file__)
CONFIG_FILE = os.path.join(os.path.dirname(script_path),"cleanup-actions.txt")

def find_similar_files(folder):
    files = os.listdir(folder)
    # Pattern to match content within parentheses or brackets at the end of the filename, before the extension
    pattern = re.compile(r'(.*?)(\s*(\(|\[)\d+(\)|\])\s*)*$')

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

            # Only remember files if they would be changed after they’re normalized
            if file != normalized_name:
                if normalized_name in file_dict:
                        file_dict[normalized_name].append(file)
                else:
                    normalized_file = os.path.join(folder, normalized_name)
                    if os.path.isfile(normalized_file):
                        file_dict[normalized_name] = [normalized_file, file]
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

def add_actions_to_config(file_dict, folder, duplicates_only):
    action_info = [
        "Info: The keys set in this files have to be exact",
        "Info: Lines like this with 'Info:' can be used for comments",
        "Info: Also they can be set to 'Naming:' and 'Deleting:'",
        "Info: Any 'Naming:' entrys will be renamed to the earlyest avalible file name",
        "Info: So 'Naming: test (4).txt' will be renamed to 'test.txt'",
        "Info: If that file is there 1 gets added in parentheses at the end",
        "Info: So the next one would be 'test (1).txt' then 'test (2).txt' and so on",
        "Info: Remove any arguments from the started python file to run this action file",
        f"Info: Actions below are for folder '{folder}'"
    ]
    actions = []
    for base_name, file_list in file_dict.items():
        if len(file_list) > 1 or (len(file_list) > 0 and not duplicates_only):
            # Sort files by modification time, keep the latest one
            file_list.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
            latest_file = file_list[0]
            file_path = os.path.join(folder, latest_file)
            naming_action = f"Naming: {file_path}"

            # Prepare actions
            if len(file_list) > 1:
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

def normalize_and_rename_file(file_path, simulate, simulation_paths):
    folder, file_name = os.path.split(file_path)
    base_name, extension = os.path.splitext(file_name)

    # Remove any numbering or brackets from the base name
    normalized_base_name = re.sub(r'(\s*(\(|\[)\d+(\)|\])\s*)+$', '', base_name).strip()
    normalized_name = f"{normalized_base_name}{extension}"
    new_path = os.path.join(folder, normalized_name)

    # if the new name is in the simulation_paths list and exist negate it
    new_path_exists = os.path.exists(new_path)
    if new_path in simulation_paths and new_path_exists:
        simulation_paths.remove(new_path)
        new_path_exists = False

    # Handle conflicts by appending a suffix if necessary
    if new_path_exists or new_path in simulation_paths:
        i = 1
        while True:
            new_paths = []
            for j,h in [["[","]"],["(",")"]]:
                num_entries = 4
                for k in range(2**num_entries): # Try all possible ways to add spaces
                    binary = f"{k:0{num_entries}b}"  # Convert to binary with leading zeros
                    c = [" " if bit == "1" else "" for bit in binary] # Convert to empty string or space
                    new_paths.append(os.path.join(folder, f"{normalized_base_name}{c[0]}{j}{c[1]}{i}{c[2]}{h}{c[3]}{extension}")) # Add the gererated path

            next_name = f"{normalized_base_name} ({i}){extension}"
            next_path = os.path.join(folder, next_name)

            if next_path in simulation_paths and next_path in new_paths:
                simulation_paths.remove(next_path)
                new_paths.remove(next_path)

            # Check if none of the paths exist
            if not any([path for path in new_paths if os.path.exists(path)]) and not next_path in simulation_paths:
                break # if they dont exist we are are done, leave the loop

            i += 1

        new_path = os.path.join(folder, next_name) # set the new filename

    if simulate:
        print(f"Simulation: Rename '{file_path}' to '{new_path}'")
        return new_path
    else:
        os.rename(file_path, new_path)
        print(f"Renamed: {file_path} -> {new_path}")


def select_folder():
    try:
        import tkinter as tk
        from tkinter import filedialog
        gui_selector = True
    except Exception as e:
        gui_selector = False

    if gui_selector:
        # Create a Tk root widget, which is necessary to use filedialog.
        root = tk.Tk()
        root.withdraw()  # Hide the root window

    print("Select / Input the target directory\nThis directory is relative to the working directory unless a absolute path is given")

    # Open the folder selection dialog and return the selected folder path.
    folder_path = False
    while folder_path == False or (folder_path and not os.path.isdir(folder_path)):
        if gui_selector:
            folder_path = filedialog.askdirectory()
        else:
            folder_path = input("Folder path: ")
        if not folder_path:
            folder_path = None

    if folder_path:
        print(f"Selected folder '{folder_path}'")
    return folder_path

def execute_config_file(simulate, keep_actions):
    simulation_paths = []
    if os.path.exists(CONFIG_FILE):
        print(f"Executing tasks from '{CONFIG_FILE}'")
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                command = line.strip()
                if command.startswith("Deleting:"):
                    file_path = command[len("Deleting:"):].strip()
                    if os.path.exists(file_path):
                        if simulate:
                            print(f"Simulation: Remove '{file_path}'")
                            simulation_paths.append(file_path)
                        else:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                elif command.startswith("Naming:"):
                    file_name = command[len("Naming:"):].strip()
                    possible_file = normalize_and_rename_file(file_name, simulate, simulation_paths)
                    if possible_file and simulate:
                        simulation_paths.append(possible_file)
                elif command.startswith("Info:"):
                    info = command[len("Info:"):].strip()
                    print("Info: " + info)
                else:
                    print(f"Unknown command: {command}")

        if not keep_actions:
            if simulate:
                print("Simulation: The cleanup-actions.txt would be deleted here")
            else:
                os.remove(CONFIG_FILE)
    else:
        return f"No action file found at '{CONFIG_FILE}'\nYou can use the target folder as argument to the script to generate the action file for automation"
    return None

def process(folders, purecli, simulate, duplicates_only, keep_actions):
    returnmessage = None
    if not folders:
        returnmessage = execute_config_file(simulate, keep_actions)

    if purecli == False and not folders and returnmessage:
        try:
            folders = [select_folder()]
        except Exception as e:
            print("Tk not avalible, can't display a folder selection.")
            folders = []
        else:
            if not folders:
                print("Folder selcetion was not valid")
    elif purecli == True:
        print("CLI mode used, not displaying any tk windows")

    if not folders:
        if returnmessage:
            print(returnmessage)
    else:
        err = 0
        for folder in folders:
            if folder and os.path.isdir(folder):
                similar_files = find_similar_files(folder)
                add_actions_to_config(similar_files, folder, duplicates_only)
            else:
                print(f"The folder '{folder}' is not a directory.")
                err = 1

            exit(err)

def main():
    folders = []
    purecli = False
    simulate = False
    helpme = False
    wrongarg = False
    duplicates_only = False
    keep_actions = False
    for i in sys.argv[1:]:
        j = i.lower()
        if j == "-h":
            helpme = True
        if j == "-c":
            purecli = True
        if j == "-s":
            simulate = True
        if j == "-d":
            duplicates_only = True
        if j == "-k":
            keep_actions = True
        elif i and os.path.isdir(i):
            folders.append(i)
        else:
            wrongarg = True
            print("Argument is no valid path or known option.")
            print("Use arguments as desribed bellow.")
    if helpme or wrongarg:
        print("List of possible arguments:")
        print("-h\tUse for this help message and exit.")
        print("-c\tUse for cli only mode (no tk file selection gui).")
        print("-s\tUse for simulating the cleanup actions (print actions only).")
        print("-d\tUse so renaming will only be done if there are duplicates avalible.")
        print("-k\tUse to keep the config file after running the actions.")
        print("Any paths added as any argument will be prossed.")
        if helpme:
            exit()

    if folders:
        folders_string = "', '".join(folders)
        print(f"Found following folders in cli '{folders_string}'")
    process(folders, purecli, simulate, duplicates_only, keep_actions)
    time.sleep(2)

if __name__ == "__main__":
    main()
