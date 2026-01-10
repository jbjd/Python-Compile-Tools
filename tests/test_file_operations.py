"""Tests for the file_operations module"""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest

from personal_compile_tools.file_operations import (
    copy_file,
    copy_folder,
    delete_file,
    delete_files,
    delete_folder,
    delete_folders,
    get_folder_size,
    read_file_utf8,
    walk_folder,
    write_file_utf8,
)
from tests.conftest import EXAMPLE_FOLDER, WORKING_DIR

_MODULE_NAME: str = "personal_compile_tools.file_operations"


def test_copy_file():
    """Should call shutil to copy file"""
    with patch(f"{_MODULE_NAME}.shutil.copy") as mock_copy:
        copy_file("foo", "bar")
        mock_copy.assert_called_once_with("foo", "bar")


def test_copy_folder():
    """Should call shutil to copy folder"""
    with patch(f"{_MODULE_NAME}.shutil.copytree") as mock_copy:
        copy_folder("foo", "bar")
        mock_copy.assert_called_once_with("foo", "bar")


def test_delete_file():
    """Should call os.remove to delete file"""
    with patch(f"{_MODULE_NAME}.os.remove") as mock_delete:
        delete_file("foo")
        mock_delete.assert_called_once_with("foo")


def test_delete_file_not_found():
    """Should no-op if file not found"""
    with patch(f"{_MODULE_NAME}.os.remove", side_effect=FileNotFoundError):
        delete_file("foo")


def test_delete_files():
    """Should call os.remove to delete each file"""
    with patch(f"{_MODULE_NAME}.os.remove") as mock_delete:
        delete_files(["foo", "bar"])

        assert mock_delete.call_count == 2
        assert mock_delete.call_args_list[0].args == ("foo",)
        assert mock_delete.call_args_list[1].args == ("bar",)


def test_delete_folder():
    """Should call shutil to delete folder"""
    with patch(f"{_MODULE_NAME}.shutil.rmtree") as mock_delete:
        delete_folder("foo")
        mock_delete.assert_called_once_with("foo", ignore_errors=True)


def test_delete_folders():
    """Should call shutil to delete each folder"""
    with patch(f"{_MODULE_NAME}.shutil.rmtree") as mock_delete:
        delete_folders(["foo", "bar"])

        assert mock_delete.call_count == 2
        assert mock_delete.call_args_list[0].args == ("foo",)
        assert mock_delete.call_args_list[0].kwargs == {"ignore_errors": True}
        assert mock_delete.call_args_list[1].args == ("bar",)
        assert mock_delete.call_args_list[1].kwargs == {"ignore_errors": True}


def test_read_file_utf8():
    """Should open the file as UTF-8 and read"""
    path: str = "some/path"
    content: str = "test"

    with patch("builtins.open", mock_open(read_data=content)) as mock_builtins_open:
        assert read_file_utf8(path) == content
        mock_builtins_open.assert_called_once_with(path, encoding="utf-8")


@pytest.mark.parametrize("make_folders", (True, False))
def test_write_file_utf8(make_folders: bool):
    """Should open the file as UTF-8, create folders if instructed, and write"""
    path: str = "some/path"
    content: str = "test"

    mock_builtins_open: MagicMock  # IDK why linter doesn't understand this
    with (
        patch("builtins.open", mock_open()) as mock_builtins_open,
        patch("os.makedirs") as mock_makedirs,
    ):
        write_file_utf8(path, content, make_folders)
        mock_builtins_open.assert_called_once_with(path, "w", encoding="utf-8")

        mock_write: MagicMock = mock_builtins_open.return_value.write
        mock_write.assert_called_once_with(content)

        if make_folders:
            mock_makedirs.assert_called_once_with("some", exist_ok=True)
        else:
            mock_makedirs.assert_not_called()


def test_get_folder_size():
    """Should get full byte size of folder"""

    # Files have \n\r line breaks and seems this causes an OS schism
    expected_byte_size: int = 40 if os.name == "nt" else 37

    assert get_folder_size(EXAMPLE_FOLDER) == expected_byte_size


def test_walk_folder():
    folders: list[str] = [folder for folder in walk_folder(EXAMPLE_FOLDER)]

    assert len(folders) == 3
    assert _norm_test_path(folders[0]) == "/test_folder/and_now_for.txt"
    assert _norm_test_path(folders[1]) == "/test_folder/subfolder/.hidden"
    assert _norm_test_path(folders[2]) == "/test_folder/subfolder/foo.txt"


def test_walk_folder_non_recursive():
    folders: list[str] = [
        folder for folder in walk_folder(EXAMPLE_FOLDER, recursive=False)
    ]

    assert len(folders) == 1
    assert _norm_test_path(folders[0]) == "/test_folder/and_now_for.txt"


def test_walk_folder_with_ignored_folder():
    folders: list[str] = [
        folder
        for folder in walk_folder(EXAMPLE_FOLDER, folders_to_ignore=["subfolder"])
    ]

    assert len(folders) == 1
    assert _norm_test_path(folders[0]) == "/test_folder/and_now_for.txt"


def _norm_test_path(path: str) -> str:
    return path.removeprefix(WORKING_DIR).replace("\\", "/")
