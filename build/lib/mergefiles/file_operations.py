from shutil import copy2
from pathlib import Path
import os
from typing import List

def get_file_paths(directory):
    """
    Gets all file paths in the specified directory.
    
    Args:
    directory (str): The directory to search.
    
    Returns:
    set: A set containing all file paths.
    """
    directory_path = Path(directory)
    file_paths = set()
    for file_path in directory_path.rglob('*'):
        if file_path.is_file():
            file_paths.add(file_path)
    return file_paths

def get_file_differences(folder_a, folder_b):
    files_in_a = get_file_paths(folder_a)
    files_in_b = get_file_paths(folder_b)

    folder_a_path = Path(folder_a)
    folder_b_path = Path(folder_b)

    files_in_a_not_in_b = {x.relative_to(folder_a_path) for x in files_in_a} - {x.relative_to(folder_b_path) for x in files_in_b}
    files_in_b_not_in_a = {x.relative_to(folder_b_path) for x in files_in_b} - {x.relative_to(folder_a_path) for x in files_in_a}
    
    return files_in_a_not_in_b, files_in_b_not_in_a

# def merge_folders(folder_a, folder_b):
#     files_in_a_not_in_b, files_in_b_not_in_a = get_file_differences(folder_a, folder_b)
    
#     folder_a_path = Path(folder_a)
#     folder_b_path = Path(folder_b)
    
#     source_folder, target_folder, files_to_copy = (folder_a_path, folder_b_path, files_in_b_not_in_a) if len(files_in_a_not_in_b) > len(files_in_b_not_in_a) else (folder_b_path, folder_a_path, files_in_a_not_in_b)

#     for relative_file_path in files_to_copy:
#         source_file_path = source_folder / relative_file_path
#         target_file_path = target_folder / relative_file_path
        
#         target_file_path.parent.mkdir(parents=True, exist_ok=True)
        
#         try:
#             if not target_file_path.exists():
#                 copy2(source_file_path, target_file_path)
#             else:
#                 print(f"File already exists at {target_file_path}, skipping...")
#         except Exception as e:
#             print(f"An error occurred while copying {source_file_path} to {target_file_path}: {e}")
# def merge_folders(src_folder, dest_folder):
#     src_files = {f.relative_to(src_folder) for f in src_folder.rglob('*') if f.is_file()}
#     dest_files = {f.relative_to(dest_folder) for f in dest_folder.rglob('*') if f.is_file()}

#     files_to_copy_from_src = src_files - dest_files
#     files_to_copy_from_dest = dest_files - src_files

#     if len(files_to_copy_from_src) < len(files_to_copy_from_dest):
#         src_folder, dest_folder = dest_folder, src_folder
#         files_to_copy_from_src, files_to_copy_from_dest = files_to_copy_from_dest, files_to_copy_from_src

#     for relative_file_path in files_to_copy_from_src:
#         src_file_path = src_folder / relative_file_path
#         dest_file_path = dest_folder / relative_file_path

#         os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
#         copy2(src_file_path, dest_file_path)

# def merge_folders(src_folder, dest_folder, overwrite=False):
#     src_folder = Path(src_folder)
#     dest_folder = Path(dest_folder)

#     for item in src_folder.rglob('*'):
#         if item.is_file():
#             relative_path = item.relative_to(src_folder)
#             dest_file = dest_folder / relative_path

#             dest_file.parent.mkdir(parents=True, exist_ok=True)
#             if overwrite or not dest_file.exists():
#                 copy2(item, dest_file)

def smart_merge_folders(source_folder: Path, target_folder: Path, overwrite: bool = False):
    """
    Merges the contents of two folders in a smart way, by copying files from the folder with the most missing files 
    to the folder with the fewest missing files. It also offers an option to handle file conflicts (files with the 
    same name) either by overwriting them or skipping the conflicting files.

    Parameters
    ----------
    source_folder : pathlib.Path
        The source folder which contains the files to be merged into the target folder. It should be a Path object pointing 
        to the source folder's location in the file system.

    target_folder : pathlib.Path
        The target folder where the files from the source folder will be copied to. It should be a Path object pointing 
        to the target folder's location in the file system.

    overwrite : bool, optional
        A flag that dictates how the function should handle file conflicts. If set to True, files in the target folder 
        that have the same name as files in the source folder will be overwritten. If set to False, these files will 
        be skipped during the merge process. The default value is False.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        Raised if either the source_folder or target_folder does not exist.

    Examples
    --------
    >>> from pathlib import Path
    >>> from your_package_name import file_operations
    >>> source_folder = Path("path/to/source_folder")
    >>> target_folder = Path("path/to/target_folder")
    >>> file_operations.smart_merge_folders(source_folder, target_folder, overwrite=True)

    Notes
    -----
    The function performs a "smart" merge by identifying which folder (source or target) has the most missing files 
    and then copies files from the folder with the most missing files to the other folder to minimize the number of 
    file operations.

    This function uses Python's built-in pathlib and shutil modules to perform file operations, and therefore inherits 
    their limitations and behaviors.
    """
    source_files = {f.relative_to(source_folder) for f in source_folder.rglob('*') if f.is_file()}
    target_files = {f.relative_to(target_folder) for f in target_folder.rglob('*') if f.is_file()}

    missing_in_source = target_files - source_files
    missing_in_target = source_files - target_files

    if len(missing_in_source) > len(missing_in_target):
        source_folder, target_folder = target_folder, source_folder
        missing_in_target, missing_in_source = missing_in_source, missing_in_target

    files_to_copy = missing_in_target
    if overwrite:
        files_to_copy = files_to_copy.union(source_files.intersection(target_files))

    for relative_file_path in files_to_copy:
        source_file_path = source_folder / relative_file_path
        target_file_path = target_folder / relative_file_path

        if not target_file_path.parent.exists():
            target_file_path.parent.mkdir(parents=True)

        copy2(source_file_path, target_file_path)
