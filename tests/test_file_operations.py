from unittest.mock import patch

from personal_compile_tools.file_operations import (
    copy_file,
    copy_folder,
    delete_file,
    delete_files,
    delete_folder,
    delete_folders,
    get_folder_size,
)
from tests.conftest import EXAMPLE_FOLDER

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


def test_get_folder_size():
    """Should get full byte size of folder"""
    EXPECTED_BYTE_SIZE: int = 89

    assert get_folder_size(EXAMPLE_FOLDER) == EXPECTED_BYTE_SIZE
