import os
import json
import shutil
import itertools
import hashlib
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import List, Dict, Union, Callable, Optional, Any, Generator
import time
import logging
from mergefiles.utils import setup_logger

SummaryDict = Dict[str, Union[int, List[str]]]

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
        return None
    else:
        return [src_path, dst_path]

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

def copy_file(
    src_path: str, 
    dst_path: str, 
    conflict_resolver: Callable[..., Union[str, List[str]]], 
    summary: SummaryDict,
    summary_lock: Lock,
    logger: logging.Logger,
    dry_run: bool = False,
    **kwargs: Any
) -> None:
    """
    Copy a single file from source to destination with error handling.

    Parameters:
    - src_path: str: Source file path
    - dst_path: str: Destination file path
    - conflict_resolver: Callable[..., Union[str, List[str]]]: Conflict resolution function
    - summary: SummaryDict: Summary of the copy action
    - summary_lock: Lock: Lock object for thread-safe updates to the summary dictionary
    - logger: logging.Logger: Logger object for logging messages
    - dry_run: bool: Whether to perform a dry run without actual copy (default: False)
    - kwargs: Any: Additional keyword arguments for the conflict resolver

    Returns:
    - None
    """
    dst_dir = os.path.dirname(dst_path)
    
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
        
    except (PermissionError, FileNotFoundError, OSError) as e:
        errors.append({"src": src_path, "dst": dst_path, "error": str(e)})
    
    # Update summary dictionary in a thread-safe manner
    with summary_lock:
        summary['files_copied'] += files_copied
        summary['directories_created'] += directories_created
        summary['conflicts'].extend(conflicts)
        summary['errors'].extend(errors)

    logger.debug(f"Updated summary: {summary}")


# def merge_directories(
#     src_dirs: List[str], 
#     dst_dir: str, 
#     conflict_resolver: Callable[..., Union[str, List[str]]] = resolve_conflict_by_hash, 
#     log_file_path: Optional[str] = None,
#     dry_run: bool = False,
#     num_threads: int = 4,
#     **kwargs: Any
# ) -> SummaryDict:
#     """
#     Merge multiple source directories into a single destination directory.

#     Parameters:
#     - src_dirs: List[str]: List of source directories
#     - dst_dir: str: Destination directory
#     - conflict_resolver: Callable[..., Union[str, List[str]]]: Conflict resolution function
#     - log_file_path: Optional[str]: Path to log file
#     - dry_run: bool: Whether to perform a dry run
#     - num_threads: int: Number of threads to use for copying
#     - kwargs: Any: Additional keyword arguments for the conflict resolver

#     Returns:
#     - SummaryDict: Summary of the merge action
#     """
#     logger = setup_logger("merge_logger", log_file_path=log_file_path)
    
#     summary: SummaryDict = {
#         'files_copied': 0,
#         'directories_created': 0,
#         'conflicts': [],
#         'errors': []
#     }
    
#     processed_files = set()
    
#     file_gen = itertools.chain(*[collect_files_gen(src) for src in src_dirs])
    
#     total_files = sum(1 for _ in itertools.chain(*[collect_files_gen(src) for src in src_dirs]))
#     file_gen = itertools.chain(*[collect_files_gen(src) for src in src_dirs])
    
#     progress_counter = [0]
#     start_time = time.time()

#     summary_lock = Lock()
    
#     with ThreadPoolExecutor(max_workers=num_threads) as executor:
#         for relative_path, src_path in file_gen:
#             if relative_path in processed_files:
#                 continue
#             processed_files.add(relative_path)
            
#             dst_path = os.path.join(dst_dir, relative_path)
            
#             # Your copy_file function call would go here
#             executor.submit(copy_file, src_path, dst_path, conflict_resolver, summary, summary_lock, dry_run, progress_counter, **kwargs)
            
#             elapsed_time = time.time() - start_time
#             progress = progress_counter[0] / total_files * 100
#             estimated_time_remaining = (elapsed_time / progress_counter[0]) * (total_files - progress_counter[0]) if progress_counter[0] else 0
#             logger.info(f"Progress: {progress:.2f}% | Estimated Time Remaining: {estimated_time_remaining:.2f}s")
    
#     logger.info(f"Merge operation completed. Summary: {summary}")

#     return summary


def merge_directories(
    src_dirs: List[str], 
    dst_dir: str, 
    conflict_resolver: Callable[..., Union[str, List[str]]] = resolve_conflict_by_hash, 
    log_file_path: Optional[str] = None,
    dry_run: bool = False,
    num_threads: int = 4,
    **kwargs: Any
) -> SummaryDict:
    """
    Merge multiple source directories into a single destination directory.

    Parameters:
    - src_dirs: List[str]: List of source directories
    - dst_dir: str: Destination directory
    - conflict_resolver: Callable[..., Union[str, List[str]]]: Conflict resolution function
    - log_file_path: Optional[str]: Path to log file
    - dry_run: bool: Whether to perform a dry run
    - num_threads: int: Number of threads to use for copying
    - kwargs: Any: Additional keyword arguments for the conflict resolver

    Returns:
    - SummaryDict: Summary of the merge action
    """
    logger = setup_logger("merge_logger", log_file_path=log_file_path)
    
    summary: SummaryDict = {
        'files_copied': 0,
        'directories_created': 0,
        'conflicts': [],
        'errors': []
    }
    
    processed_files = set()
    file_gen = itertools.chain(*[collect_files_gen(src) for src in src_dirs])
    summary_lock = Lock()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for relative_path, src_path in file_gen:
            if relative_path in processed_files:
                continue
            processed_files.add(relative_path)
            
            dst_path = os.path.join(dst_dir, relative_path)
            
            # Ensure the destination directory exists
            dst_dir_path = os.path.dirname(dst_path)
            if not os.path.exists(dst_dir_path):
                if not dry_run:
                    os.makedirs(dst_dir_path)
                    summary['directories_created'] += 1

            # File copying logic
            try:
                if not dry_run:
                    shutil.copy(src_path, dst_path)
                    summary['files_copied'] += 1
            except Exception as e:
                summary['errors'].append(str(e))
    
    logger.info(f"Merge operation completed. Summary: {summary}")

    return summary