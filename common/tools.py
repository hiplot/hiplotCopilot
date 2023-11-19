import logging
import os
import shutil
import subprocess

from common.print_color import print_green


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


def path_exists(path: str) -> bool:
    current_directory = os.getcwd()
    docs_folder = os.path.join(current_directory, path)
    return os.path.exists(docs_folder) and os.path.isdir(docs_folder)


def delete_dir(path: str):
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)
            os.chmod(path, 0o777)
    shutil.rmtree(path)
    print_green(f"Clean {path} successful.")


def show_file_content(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            print(content)
    except FileNotFoundError as e:
        logging.error(e)
