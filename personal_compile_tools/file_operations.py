"""Functions for common file operations. Mainly wrappers to standard library functions
condensed into one file"""

import os
import shutil
from typing import Iterable


def copy_file(source: str, destination: str) -> None:
    shutil.copy(source, destination)


def copy_folder(source: str, destination: str) -> None:
    shutil.copytree(source, destination)


def delete_file(file: str) -> None:
    """Deletes file, doing nothing if it does not exist"""
    try:
        os.remove(file)
    except FileNotFoundError:
        pass


def delete_files(files: Iterable[str]) -> None:
    """Deletes files, skipping them if they do not exist"""
    for file in files:
        delete_file(file)


def delete_folder(folder: str) -> None:
    shutil.rmtree(folder, ignore_errors=True)


def delete_folders(folders: Iterable[str]) -> None:
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)


def get_folder_size(folder: str) -> int:
    """Sums all files in folder and sub-folders"""

    size: int = 0
    folders_to_visit_stack: list[str] = [folder]

    while folders_to_visit_stack:
        top_folder = folders_to_visit_stack.pop()
        subfolders = []

        try:
            folder_iter = os.scandir(top_folder)
        except OSError:
            continue

        with folder_iter:
            while True:
                try:
                    entry = next(folder_iter)
                except (OSError, StopIteration):
                    break

                try:
                    is_folder = entry.is_dir()
                except OSError:
                    is_folder = False

                if is_folder:
                    subfolders.append(entry.path)
                else:
                    file_path: str = os.path.join(top_folder, entry.name)
                    size += os.stat(file_path).st_size

        folders_to_visit_stack += subfolders

    return size
