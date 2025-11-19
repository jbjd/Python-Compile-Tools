"""Functions for common file operations. Mainly wrappers to standard library functions
condensed into one file"""

import os
import shutil
from typing import Iterable, Iterator


def copy_file(source: str, destination: str) -> None:
    """Copies a file from source to destination"""
    shutil.copy(source, destination)


def copy_folder(source: str, destination: str) -> None:
    """Copies a folder from source to destination"""
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
    """Deletes folder, doing nothing if it does not exist"""
    shutil.rmtree(folder, ignore_errors=True)


def delete_folders(folders: Iterable[str]) -> None:
    """Deletes folders, doing nothing if they do not exist"""
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)


def get_folder_size(folder: str) -> int:
    """Sums all files in folder and sub-folders"""
    return sum(os.stat(file).st_size for file in walk_folder(folder))


def walk_folder(
    folder: str, recursive: bool = True, folders_to_ignore: Iterable | None = None
) -> Iterator[str]:
    """Edited version of os.walk to yield full paths of files within
    a folder and all sub folders"""
    folders_to_visit_stack: list[str] = [folder]
    ignored_folders: Iterable = [] if folders_to_ignore is None else folders_to_ignore

    while folders_to_visit_stack:
        top_folder = folders_to_visit_stack.pop()
        sub_folders = []

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
                    if recursive and entry.name not in ignored_folders:
                        sub_folders.append(entry.path)
                else:
                    yield entry.path

        folders_to_visit_stack += sub_folders
