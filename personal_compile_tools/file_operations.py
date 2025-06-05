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
    """Sums all files in folder and sub-folders recursively"""
    return sum(
        sum(os.stat(f"{folder}/{file}").st_size for file in files)
        for folder, _, files in os.walk(folder, followlinks=True)
    )
