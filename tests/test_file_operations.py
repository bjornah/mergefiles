import pytest
import tempfile

from shutil import copy2
from pathlib import Path

from mergefiles import file_operations

def test_merge_with_more_missing_files_in_b():
    """
    Test the smart_merge_folders function to ensure that it correctly merges the folders when folder B has more missing files compared to folder A.

    This test creates two folders where folder A has more files compared to folder B. It then uses the smart_merge_folders function to merge them. After merging, it checks if folder B has all the files that were initially in folder A.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        folder_a = Path(tmpdirname) / 'folder_a'
        folder_b = Path(tmpdirname) / 'folder_b'
        folder_a.mkdir()
        folder_b.mkdir()

        (folder_a / 'file1.txt').write_text('File 1 in Folder A')
        (folder_a / 'file2.txt').write_text('File 2 in Folder A')
        (folder_b / 'file1.txt').write_text('File 1 in Folder B')

        file_operations.smart_merge_folders(folder_a, folder_b)

        assert (folder_b / 'file1.txt').read_text() == 'File 1 in Folder B'
        assert (folder_b / 'file2.txt').read_text() == 'File 2 in Folder A'


def test_merge_with_more_missing_files_in_a():
    """
    Test the smart_merge_folders function to ensure that it correctly merges the folders when folder A has more missing files compared to folder B.

    This test creates two folders where folder B has more files compared to folder A. It then uses the smart_merge_folders function to merge them. After merging, it checks if folder A has all the files that were initially in folder B.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        folder_a = Path(tmpdirname) / 'folder_a'
        folder_b = Path(tmpdirname) / 'folder_b'
        folder_a.mkdir()
        folder_b.mkdir()

        (folder_a / 'file1.txt').write_text('File 1 in Folder A')
        (folder_b / 'file1.txt').write_text('File 1 in Folder B')
        (folder_b / 'file2.txt').write_text('File 2 in Folder B')

        file_operations.smart_merge_folders(folder_a, folder_b)

        assert (folder_a / 'file1.txt').read_text() == 'File 1 in Folder A'
        assert (folder_a / 'file2.txt').read_text() == 'File 2 in Folder B'


def test_merge_with_identical_files_overwrite():
    """
    Test the smart_merge_folders function to ensure that it correctly overwrites files in the target folder when the overwrite parameter is set to True.

    This test creates two folders with identical filenames but different content. It then uses the smart_merge_folders function with overwrite set to True to merge them. After merging, it checks if the file in folder B has been overwritten by the file from folder A.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        folder_a = Path(tmpdirname) / 'folder_a'
        folder_b = Path(tmpdirname) / 'folder_b'
        folder_a.mkdir()
        folder_b.mkdir()

        (folder_a / 'file1.txt').write_text('File 1 in Folder A')
        (folder_b / 'file1.txt').write_text('File 1 in Folder B')

        file_operations.smart_merge_folders(folder_a, folder_b, overwrite=True)

        assert (folder_b / 'file1.txt').read_text() == 'File 1 in Folder A'


def test_merge_with_identical_files_no_overwrite():
    """
    Test the smart_merge_folders function to ensure that it does not overwrite files in the target folder when the overwrite parameter is set to False.

    This test creates two folders with identical filenames but different content. It then uses the smart_merge_folders function with overwrite set to False to merge them. After merging, it checks if the file in folder B has retained its original content and was not overwritten by the file from folder A.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        folder_a = Path(tmpdirname) / 'folder_a'
        folder_b = Path(tmpdirname) / 'folder_b'
        folder_a.mkdir()
        folder_b.mkdir()

        (folder_a / 'file1.txt').write_text('File 1 in Folder A')
        (folder_b / 'file1.txt').write_text('File 1 in Folder B')

        file_operations.smart_merge_folders(folder_a, folder_b, overwrite=False)

        assert (folder_b / 'file1.txt').read_text() == 'File 1 in Folder B'



if __name__ == "__main__":
    pytest.main([__file__])
