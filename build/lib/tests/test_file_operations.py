from typing import Dict, Union
import tempfile
from tempfile import TemporaryDirectory
import unittest
import json
import os
from typing import Dict, Union
from mergefiles.file_operations import *
from pathlib import Path

# First, let's define the create_test_directories function for generating test scenarios

from typing import Dict, Union

def create_test_directories(directory: str, structure: Dict[str, Union[str, Dict]]) -> None:
    """
    Create a test directory structure in a given directory.
    
    Parameters:
    - directory: str: Root directory for creating the test structure
    - structure: Dict[str, Union[str, Dict]]: Dictionary defining the folder/file structure to be created
    
    Returns:
    - None
    """
    for name, content in structure.items():
        path = Path(directory) / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_test_directories(str(path), content)
        else:
            with open(path, 'w') as f:
                f.write(content)


# Unit tests
def test_collect_files_gen():
    with tempfile.TemporaryDirectory() as tempdir:
        create_test_directories(tempdir, {"file1.txt": "Hello", "folder": {"file2.txt": "World"}})
        
        collected_files = list(collect_files_gen(tempdir))
        collected_files_relative = [Path(p).relative_to(tempdir) for _, p in collected_files]
        
        assert len(collected_files) == 2, f"Expected 2 files, found {len(collected_files)}"
        assert Path("file1.txt") in collected_files_relative, "file1.txt not found"
        assert Path("folder/file2.txt") in collected_files_relative, "folder/file2.txt not found"


def test_resolve_conflict_by_hash():
    with tempfile.TemporaryDirectory() as temp_dir1, tempfile.TemporaryDirectory() as temp_dir2:
        # Create two files with the same content
        file1 = os.path.join(temp_dir1, "file.txt")
        file2 = os.path.join(temp_dir2, "file.txt")
        
        with open(file1, 'w') as f:
            f.write("Hello")
        
        with open(file2, 'w') as f:
            f.write("Hello")
        
        assert resolve_conflict_by_hash(file1, file2) is None, "Conflict not resolved correctly for identical files"
        
        # Update one file to create a conflict
        with open(file2, 'w') as f:
            f.write("World")
        
        assert resolve_conflict_by_hash(file1, file2) == [file1, file2], "Conflict not resolved correctly for different files"


def test_keep_both_files():
    assert keep_both_files("file1", "file2") == ["file1", "file2"], "Failed to keep both files"


def test_keep_files_from_preferred_src():
    with tempfile.TemporaryDirectory() as tempdir1, tempfile.TemporaryDirectory() as tempdir2:
        create_test_directories(tempdir1, {"file1.txt": "Hello"})
        create_test_directories(tempdir2, {"file1.txt": "Hello"})
        
        src1_file = Path(tempdir1) / "file1.txt"
        src2_file = Path(tempdir2) / "file1.txt"
        
        preferred_file = keep_files_from_preferred_src(str(src1_file), str(src2_file), preferred_src=tempdir1)
        
        assert preferred_file == str(src1_file), "Failed to keep file from preferred source"
        assert preferred_file != str(src2_file), "Incorrectly kept file from non-preferred source"

def test_write_summary_to_log():
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file_path = os.path.join(temp_dir, "log.json")
        summary = {"key": "value"}
        
        write_summary_to_log(summary, log_file_path)
        
        with open(log_file_path, 'r') as f:
            loaded_summary = json.load(f)
        
        assert loaded_summary == summary, "Summary not written to log correctly"

# other tests

def test_merge_directories():
    """Test the final version of the merge_directories function."""
    with TemporaryDirectory() as src1, TemporaryDirectory() as src2, TemporaryDirectory() as dst:
        create_test_directories(src1, {"file1.txt": "Hello", "folder": {"file2.txt": "World"}})
        create_test_directories(src2, {"file1.txt": "Hello", "folder": {"file2.txt": "Universe"}})
        
        # Run the function
        summary = merge_directories([src1, src2], dst, log_file_path=None, dry_run=False)
        
        # Validate the results
        assert summary['files_copied'] == 2
        assert summary['directories_created'] == 1
        assert summary['conflicts'] == []
        
        # Check the actual files
        with open(os.path.join(dst, "file1.txt"), "r") as f:
            assert f.read() == "Hello"
        with open(os.path.join(dst, "folder", "file2.txt"), "r") as f:
            assert f.read() == "World"

def test_merge_directories_dry_run():
    """Test the final version of the merge_directories function with dry-run enabled."""
    with TemporaryDirectory() as src1, TemporaryDirectory() as src2, TemporaryDirectory() as dst:
        create_test_directories(src1, {"file1.txt": "Hello", "folder": {"file2.txt": "World"}})
        create_test_directories(src2, {"file1.txt": "Hello", "folder": {"file2.txt": "Universe"}})
        
        # Run the function
        summary = merge_directories([src1, src2], dst, log_file_path=None, dry_run=True)
        
        # Validate the results
        assert summary['files_copied'] == 0
        assert summary['directories_created'] == 0
        assert summary['conflicts'] == []
        
        # Make sure no actual files were created
        assert not os.path.exists(os.path.join(dst, "file1.txt"))
        assert not os.path.exists(os.path.join(dst, "folder", "file2.txt"))
