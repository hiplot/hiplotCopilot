import logging
import os
import sys
import shutil
import subprocess

from common.print_color import print_green, print_yellow


def is_number(s) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def git_clone(url: str):
    try:
        subprocess.run(["git", "clone", url], check=True)
        print_green("Git clone successful")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git clone failed: {e}")


def git_clone_path(url: str, path: str):
    if path_exists(path):
        print_yellow(f"Path <{path}> exists, continue clone? (y/n/q)")
        c = input().lower()
        if c == "y":
            delete_dir(path)
            git_clone(url)
        elif c == "q":
            sys.exit()
    else:
        git_clone(url)


def path_exists(path: str) -> bool:
    current_directory = os.getcwd()
    docs_folder = os.path.join(current_directory, path)
    return os.path.exists(docs_folder) and os.path.isdir(docs_folder)


def delete_dir(path: str):
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            os.chmod(filepath, 0o777)
    shutil.rmtree(path)
    print_green(f"Clean {path} successful.")


def show_file_content(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            print(content)
    except FileNotFoundError as e:
        logging.error(e)
