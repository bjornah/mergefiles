# Here is the full Python code for merging directories with advanced features.

import os
import json
import shutil
import itertools
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Union, Callable, Optional, Any, Generator, Optional
from threading import Lock
import time
import logging
from logging import Logger

def setup_logger(name: str, level: int = logging.INFO, log_file_path: str = None) -> Logger:
    """
    Setup a logger with the specified name, level, and optional log file.
    
    Parameters:
    - name (str): The name of the logger
    - level (int): The logging level (default: logging.INFO)
    - log_file_path (str): The path to the log file (default: None, logs to stdout)
    
    Returns:
    - Logger: Configured logger object
    
    Example:
    ```python
    logger = setup_logger("my_logger", level=logging.DEBUG)
    logger.debug("This is a debug message.")
    ```
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove all handlers to avoid duplicate logs in this environment
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler if log_file_path is provided
    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def collect_files_gen(directory: str) -> Generator[str, None, None]:
    """
    Generate relative file paths from a given directory.

    Parameters:
    - directory: str: Source directory

    Returns:
    - Generator[str, None, None]: Yields relative file paths
    """
    for root, _, files in os.walk(directory):
        for file in files:
            abs_path = os.path.join(root, file)
            yield os.path.relpath(abs_path, directory), abs_path


def resolve_conflict_by_hash(src_path: str, dst_path: str, **kwargs: Any) -> Optional[str]:
    """
    Resolve conflict between source and destination files based on their hash.

    Parameters:
    - src_path: str: Source file path
    - dst_path: str: Destination file path
    - kwargs: Any: Additional keyword arguments

    Returns:
    - Optional[str]: Resolved file path to keep
    """
    src_hash = hashlib.sha256(open(src_path, 'rb').read()).hexdigest()
    dst_hash = hashlib.sha256(open(dst_path, 'rb').read()).hexdigest()
    
    if src_hash == dst_hash:
        return None  # No action needed, files are identical
    else:
        return [src_path, dst_path]  # Keep both files


def keep_both_files(src_path: str, dst_path: str, **kwargs: Any) -> List[str]:
    """
    Keep both conflicting files.

    Parameters:
    - src_path: str: Source file path
    - dst_path: str: Destination file path
    - kwargs: Any: Additional keyword arguments

    Returns:
    - List[str]: List of file paths to keep
    """
    return [src_path, dst_path]


def keep_files_from_preferred_src(src_path: str, dst_path: str, preferred_src: str, **kwargs: Any) -> Optional[str]:
    """
    Automatically keep files from the preferred source directory.

    Parameters:
    - src_path: str: Source file path
    - dst_path: str: Destination file path
    - preferred_src: str: Preferred source directory path
    - kwargs: Any: Additional keyword arguments

    Returns:
    - Optional[str]: Resolved file path to keep
    """
    return src_path if os.path.commonpath([src_path, preferred_src]) == preferred_src else None


def write_summary_to_log(summary: Dict[str, Union[int, List[str]]], log_file_path: str) -> None:
    """
    Write summary dictionary to a JSON log file.

    Parameters:
    - summary: Dict[str, Union[int, List[str]]]: Summary of the copy action
    - log_file_path: str: Path to the log file

    Returns:
    - None
    """
    with open(log_file_path, 'w') as log_file:
        json.dump(summary, log_file, indent=4)


def copy_file(
    src_path: str, 
    dst_path: str, 
    conflict_resolver: Callable[..., Union[str, List[str]]], 
    summary: Dict[str, Union[int, List[str]]],
    summary_lock: Lock,
    dry_run: bool = False,
    progress_counter: Optional[List[int]] = None,  # Mutable list as a workaround to update integer in place
    **kwargs: Any
) -> None:
    """
    Copy a single file from source to destination with error handling.

    Parameters:
    - src_path: str: Source file path
    - dst_path: str: Destination file path
    - conflict_resolver: Callable[..., Union[str, List[str]]]: Conflict resolution function
    - summary: Dict[str, Union[int, List[str]]]: Summary of the copy action
    - summary_lock: Lock: Lock object for thread-safe updates to the summary dictionary
    - dry_run: bool: Whether to perform a dry run without actual copy
    - progress_counter: Optional[List[int]]: Mutable list containing a single integer for progress count (default: None)
    - kwargs: Any: Additional keyword arguments for the conflict resolver

    Returns:
    - None
    """
    dst_dir = os.path.dirname(dst_path)

    # print(f"Debug: Inside copy_file. src_path={src_path}, dst_path={dst_path}, dry_run={dry_run}")
    
    # Initialize local variables for summary updates
    files_copied = 0
    directories_created = 0
    conflicts = []
    errors = []
    
    try:
        # Handle conflict if destination file exists
        if os.path.exists(dst_path):
            resolved_paths = conflict_resolver(src_path, dst_path, **kwargs)
            
            # If conflict could not be resolved, skip and log the conflict
            if resolved_paths is None:
                conflicts.append(dst_path)
            else:
                # If multiple resolved paths, handle each one
                if isinstance(resolved_paths, list):
                    for i, path in enumerate(resolved_paths):
                        versioned_dst_path = f"{dst_path[:-4]}_v{i+1}{dst_path[-4:]}"
                        files_copied += 1
                        if not dry_run:
                            if not os.path.exists(dst_dir):
                                os.makedirs(dst_dir)
                                directories_created += 1
                            shutil.copy(path, versioned_dst_path)
                else:
                    # If single resolved path, continue as usual
                    src_path = resolved_paths if resolved_paths else src_path
        
        # Copy file to destination
        if not dry_run:
            files_copied += 1
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
                directories_created += 1
            shutil.copy(src_path, dst_path)
        
        # Update progress counter if specified
        if progress_counter is not None:
            progress_counter[0] += 1
        
    except (PermissionError, FileNotFoundError, OSError) as e:
        errors.append({"src": src_path, "dst": dst_path, "error": str(e)})
    
    # Update summary dictionary in a thread-safe manner
    with summary_lock:
        summary['files_copied'] += files_copied
        summary['directories_created'] += directories_created
        summary['conflicts'].extend(conflicts)
        summary['errors'].extend(errors)

    # print(f"Debug: Updated summary: {summary}")


# Finalizing the code using the last debug version as a basis
def merge_directories(
    src_dirs: List[str], 
    dst_dir: str, 
    conflict_resolver: Callable[..., Union[str, List[str]]] = resolve_conflict_by_hash, 
    log_file_path: Optional[str] = None,
    dry_run: bool = False,
    num_threads: int = 4,
    **kwargs: Any  # Additional keyword arguments for the conflict resolver
) -> Dict[str, Union[int, List[str]]]:
    """
    Final version of merge_directories with all features.
    
    Parameters:
    - src_dirs: List[str]: List of source directories
    - dst_dir: str: Destination directory
    - conflict_resolver: Callable[..., Union[str, List[str]]]: Conflict resolution function (default: resolve_conflict_by_hash)
    - log_file_path: Optional[str]: Path to the log file (default: None)
    - dry_run: bool: Whether to perform a dry run without actual copy (default: False)
    - num_threads: int: Number of threads for file copying (default: 4)
    - kwargs: Any: Additional keyword arguments for the conflict resolver

    Returns:
    - Dict[str, Union[int, List[str]]]: Summary of the merge action
    """

    # print(f"Debug: Inside merge_directories. dry_run={dry_run}, num_threads={num_threads}")

    # Initialize summary dictionary
    summary = {
        'files_copied': 0,
        'directories_created': 0,
        'conflicts': [],
        'errors': []
    }
    
    processed_files = set()  # To keep track of already processed files
    
    # Create a generator to yield files from all source directories
    file_gen = itertools.chain(*[collect_files_gen(src) for src in src_dirs])
    
    # Calculate total number of files for progress monitoring
    total_files = sum(1 for _ in itertools.chain(*[collect_files_gen(src) for src in src_dirs]))
    file_gen = itertools.chain(*[collect_files_gen(src) for src in src_dirs])  # Reset the generator
    
    # Initialize progress counter and timing variables
    progress_counter = [0]  # Mutable list to update integer in place
    start_time = time.time()

    summary_lock = Lock()
    
    # Initialize thread pool executor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for relative_path, src_path in file_gen:
            if relative_path in processed_files:
                continue
            processed_files.add(relative_path)
            
            dst_path = os.path.join(dst_dir, relative_path)
            
            # Multi-threaded call to copy_file
            executor.submit(copy_file, src_path, dst_path, conflict_resolver, summary, summary_lock, dry_run, progress_counter, **kwargs)
            
            # Display real-time progress
            elapsed_time = time.time() - start_time
            progress = progress_counter[0] / total_files * 100
            estimated_time_remaining = (elapsed_time / progress_counter[0]) * (total_files - progress_counter[0]) if progress_counter[0] else 0
            print(f"\rProgress: {progress:.2f}% | Estimated Time Remaining: {estimated_time_remaining:.2f}s", end="")
    
    # Write summary to log file if specified
    if log_file_path:
        write_summary_to_log(summary, log_file_path)
    
    # print(f"Debug: Final summary: {summary}")

    return summary