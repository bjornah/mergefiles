import argparse
from typing import Any, Callable, List, Union, Optional
from mergefiles.core import merge_directories, resolve_conflict_by_hash, keep_both_files, keep_files_from_preferred_src
from mergefiles.utils import setup_logger

def main() -> None:
    """
    Main function to serve as the entry point for the CLI.

    Example:
    ```
    # To merge directories with default options
    merge_directories --src_dirs /path/to/src1 /path/to/src2 --dst_dir /path/to/dst

    # To specify conflict resolver and log file path
    merge_directories --src_dirs /path/to/src1 /path/to/src2 --dst_dir /path/to/dst --conflict_resolver keep_both_files --log_file_path merge.log
    ```
    """
    parser = argparse.ArgumentParser(description="Merge multiple directories into a destination directory.")
    
    parser.add_argument("--src_dirs", type=str, nargs="+", required=True, help="List of source directories to merge.")
    parser.add_argument("--dst_dir", type=str, required=True, help="Destination directory where the merged content will be stored.")
    parser.add_argument("--conflict_resolver", type=str, default="resolve_conflict_by_hash", help="Conflict resolution function to use. Default is 'resolve_conflict_by_hash'.")
    parser.add_argument("--log_file_path", type=str, default=None, help="Path to the log file. Logs will be stored here if specified.")
    parser.add_argument("--dry_run", action="store_true", help="Perform a dry run without actual copying.")
    parser.add_argument("--num_threads", type=int, default=4, help="Number of threads for file copying. Default is 4.")
    parser.add_argument("--resolver_args", type=str, nargs='*', help="Key-value pairs for additional conflict resolver arguments. E.g., preferred_src=/path/to/src")

    args = parser.parse_args()
    
    # Parse the resolver_args into a dictionary
    resolver_args = {}
    if args.resolver_args:
        for arg in args.resolver_args:
            key, value = arg.split('=')
            resolver_args[key] = value

    conflict_resolvers = {
        "resolve_conflict_by_hash": resolve_conflict_by_hash,
        "keep_both_files": keep_both_files,
        "keep_files_from_preferred_src": keep_files_from_preferred_src
    }
    conflict_resolver = conflict_resolvers.get(args.conflict_resolver, resolve_conflict_by_hash)
    
    summary = merge_directories(
        src_dirs=args.src_dirs, 
        dst_dir=args.dst_dir, 
        conflict_resolver=conflict_resolver, 
        log_file_path=args.log_file_path,
        dry_run=args.dry_run,
        num_threads=args.num_threads
    )
    
    print("Merge operation completed. Summary:", summary)

if __name__ == "__main__":
    main()
