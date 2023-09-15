# Folder Merging Package

## Description

This Python package provides utilities for merging two folders in a smart way, considering file discrepancies between them. It allows for the merging of folders with an option to overwrite or retain files with identical names.

## Features

1. **Smart Folder Merging**
   - Merge folders by considering the missing files in each folder.
   - Option to overwrite or retain files with identical names during the merge.
   
2. **File Operations**
   - Contains utilities for identifying files present in one folder but missing in another.
   - Functionality to copy files from one folder to another considering various parameters.

## Installation

To install the package, follow these steps:

1. Clone the repository: `git clone https://github.com/yourusername/folder-merging-package.git`

2. Navigate to the package directory: `cd folder-merging-package`

3. Install the package using pip: `pip install .`


## Usage

Here's a simple usage example demonstrating how to use the `smart_merge_folders` function from the `file_operations` module:

    from mypackage import file_operations
    from pathlib import Path

    # Define the paths to your folders
    folder_a = Path("/path/to/folder_a")
    folder_b = Path("/path/to/folder_b")

    # Perform a smart merge with overwrite option enabled
    file_operations.smart_merge_folders(folder_a, folder_b, overwrite=True)

## Running tests
To run the tests, navigate to the package directory and execute the following command: `pytest`
This will run all the test cases present in the tests directory and provide a summary of the test results.

