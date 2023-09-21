
# MergeFiles

## Description

`mergefiles` is a Python package that provides utilities to merge multiple directories into a single directory.

## Installation

To install the package, follow these steps:

1. Clone the repository: `git clone https://github.com/yourusername/folder-merging-package.git`

2. Navigate to the package directory: `cd folder-merging-package`

3. Install the package using pip: `pip install .`

## Usage

```python
from mergefiles.core import merge_directories

src_dirs = ["src1", "src2"]
dst_dir = "dst"
merge_directories(src_dirs, dst_dir)
```

## Features

- Merge multiple source directories into a single destination directory
- Conflict resolution strategies
- Multi-threaded file copying for improved performance

## License

None
