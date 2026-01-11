"""Common file operations."""

import os
import shutil
from collections.abc import Iterable, Iterator


def copy_file(source: str, destination: str) -> None:
    """Copies a file from source to destination."""
    shutil.copy(source, destination)


def copy_folder(source: str, destination: str) -> None:
    """Copies a folder from source to destination."""
    shutil.copytree(source, destination)


def delete_file(file: str) -> None:
    """Deletes file, doing nothing if it does not exist."""
    try:
        os.remove(file)
    except FileNotFoundError:
        pass


def delete_files(files: Iterable[str]) -> None:
    """Deletes files, skipping them if they do not exist."""
    for file in files:
        delete_file(file)


def delete_folder(folder: str) -> None:
    """Deletes folder, doing nothing if it does not exist."""
    shutil.rmtree(folder, ignore_errors=True)


def delete_folders(folders: Iterable[str]) -> None:
    """Deletes folders, doing nothing if they do not exist."""
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)


def read_file_utf8(path: str) -> str:
    """Reads a UTF-8 file and returns its contents."""
    with open(path, encoding="utf-8") as fp:
        return fp.read()


def write_file_utf8(path: str, content: str, make_folders: bool = False) -> None:
    """Writes content to a UTF-8 file. If make_folders, also attempts to make any
    folders along the path that don't exist.
    """

    if make_folders:
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)


def get_folder_size(folder: str) -> int:
    """Sums all files in folder and sub-folders."""
    return sum(os.stat(file).st_size for file in walk_folder(folder))


def walk_folder(
    folder: str, recursive: bool = True, folders_to_ignore: Iterable[str] | None = None
) -> Iterator[str]:
    """Edited version of os.walk to yield full paths of files within
    a folder and all sub folders.
    """
    folders_to_visit_stack: list[str] = [folder]
    ignored_folders: Iterable[str] = (
        [] if folders_to_ignore is None else folders_to_ignore
    )

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
