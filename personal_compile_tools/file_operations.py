"""Functions for common file opertions. Mainly wrappers to standard library functions
condensed into one file"""

import os
import shutil
from glob import glob
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
    return sum(
        os.stat(p).st_size
        for p in glob(f"{folder}/**/*", recursive=True)
        if os.path.isfile(p)
    )
