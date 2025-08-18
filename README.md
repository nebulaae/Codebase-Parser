## Key Features

* Multi-language Support: Handles C++, Python, Java, JavaScript/TypeScript, and many other languages
* Structure Analysis: Creates a tree-like view of your project structure
* Code Extraction: Parses all code files and includes their content
* Formatted Output: Creates the exact separator format
* Built-in Libraries Only: Uses only Python's standard library (os, pathlib, re, etc.)

## How to Use

* Basic Usage: Place the script in your project root and run:
```
python main.py
```
* Custom Directory: Parse a specific directory:
```
python codebase_parser.py /path/to/your/project
```
* Preview Structure: See the structure without generating full output:
```
python codebase_parser.py --preview
```
* Enhanced Analysis: Get detailed code metrics:
python codebase_parser.py --preview

#### Output Format The script generates a code.txt file

Project Summary: File counts, languages, directory overview
Structure Tree: Visual representation of your project hierarchy
Code Sections: Each file with the format you requested:


## Smart Features

* Language Detection: Automatically identifies programming languages
* Ignore Patterns: Skips node_modules, .git, build folders, etc.
* Encoding Handling: Properly handles different file encodings
* Error Handling: Gracefully handles permission errors and unreadable files
* Code Analysis: Counts lines, functions, classes (in enhanced mode)

The script will work perfectly for your TypeScript/Node.js project structure and will create exactly the format you showed in your example. Just run it from your src directory or point it to your project root!