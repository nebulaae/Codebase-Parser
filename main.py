#!/usr/bin/env python3
"""
Codebase Parser Script
Analyzes project structure and generates formatted code documentation
Supports multiple programming languages (Python, JavaScript/TypeScript, Java, C++, etc.)
"""

import os
import sys
from pathlib import Path
import re
from typing import Dict, List, Set, Optional, Tuple

class CodebaseParser:
    def __init__(self, root_path: str = ".", output_file: str = "code.txt"):
        self.root_path = Path(root_path).resolve()
        self.output_file = output_file
        
        # Supported file extensions for different languages
        self.code_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.cc', '.cxx', 
            '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.kt', 
            '.swift', '.m', '.mm', '.scala', '.clj', '.hs', '.ml', '.fs',
            '.dart', '.lua', '.r', '.pl', '.sh', '.bash', '.zsh', '.fish',
            '.sql', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg'
        }
        
        # Directories to ignore
        self.ignore_dirs = {
            'node_modules', '__pycache__', '.git', '.svn', '.hg', 'build', 
            'dist', 'target', 'bin', 'obj', '.gradle', '.idea', '.vscode',
            'vendor', 'coverage', '.nyc_output', 'logs', 'tmp', 'temp',
            '.next', '.nuxt', 'out', 'public/build', 'venv', 'env', '.env'
        }
        
        # Files to ignore
        self.ignore_files = {
            '.gitignore', '.dockerignore', 'package-lock.json', 'yarn.lock',
            'Pipfile.lock', 'poetry.lock', '.DS_Store', 'Thumbs.db',
            'desktop.ini', '*.log', '*.tmp', '*.temp'
        }

    def should_ignore_path(self, path: Path) -> bool:
        """Check if a path should be ignored"""
        # Check if any parent directory is in ignore list
        for parent in path.parents:
            if parent.name in self.ignore_dirs:
                return True
        
        # Check if current directory is in ignore list
        if path.is_dir() and path.name in self.ignore_dirs:
            return True
            
        # Check if file should be ignored
        if path.is_file():
            if path.name in self.ignore_files:
                return True
            # Check for pattern matches
            for ignore_pattern in self.ignore_files:
                if '*' in ignore_pattern and path.name.endswith(ignore_pattern[1:]):
                    return True
                    
        return False

    def is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file based on extension"""
        return file_path.suffix.lower() in self.code_extensions

    def get_language_from_extension(self, extension: str) -> str:
        """Get language name from file extension"""
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', 
            '.tsx': 'TypeScript React', '.jsx': 'JavaScript React',
            '.java': 'Java', '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++',
            '.c': 'C', '.h': 'C/C++ Header', '.hpp': 'C++ Header',
            '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go',
            '.rs': 'Rust', '.kt': 'Kotlin', '.swift': 'Swift',
            '.m': 'Objective-C', '.mm': 'Objective-C++', '.scala': 'Scala',
            '.clj': 'Clojure', '.hs': 'Haskell', '.ml': 'OCaml', '.fs': 'F#',
            '.dart': 'Dart', '.lua': 'Lua', '.r': 'R', '.pl': 'Perl',
            '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh', '.fish': 'Fish',
            '.sql': 'SQL', '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML',
            '.yml': 'YAML', '.toml': 'TOML', '.ini': 'INI', '.cfg': 'Config'
        }
        return lang_map.get(extension.lower(), 'Unknown')

    def scan_directory(self, directory: Path) -> Dict[str, List[Path]]:
        """Scan directory and organize files by their parent directories"""
        structure = {}
        
        try:
            for item in directory.rglob('*'):
                if self.should_ignore_path(item):
                    continue
                
                if item.is_file() and self.is_code_file(item):
                    # Get relative path from root
                    rel_path = item.relative_to(self.root_path)
                    parent_dir = str(rel_path.parent) if rel_path.parent.name != '.' else 'root'
                    
                    if parent_dir not in structure:
                        structure[parent_dir] = []
                    structure[parent_dir].append(item)
        
        except PermissionError as e:
            print(f"Permission denied accessing: {e}")
        except Exception as e:
            print(f"Error scanning directory: {e}")
            
        return structure

    def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with proper encoding detection"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1 if UTF-8 fails
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"
        except Exception as e:
            return f"Error reading file: {e}"

    def generate_separator(self, text: str, char: str = '-', length: int = 43) -> str:
        """Generate a separator line with text"""
        return char * length + text + char * length

    def format_directory_structure(self, structure: Dict[str, List[Path]]) -> str:
        """Format the directory structure as a tree"""
        result = []
        result.append("Code Structure:")
        
        # Sort directories for consistent output
        sorted_dirs = sorted(structure.keys())
        
        for directory in sorted_dirs:
            if directory == 'root':
                result.append(".")
            else:
                # Create indented structure
                parts = directory.split(os.sep)
                for i, part in enumerate(parts):
                    indent = "  " * i
                    result.append(f"{indent}{part}")
            
            # Add files in this directory
            files = sorted(structure[directory], key=lambda x: x.name)
            for file_path in files:
                rel_path = file_path.relative_to(self.root_path)
                depth = len(rel_path.parts) - 1
                indent = "  " * (depth + 1)
                result.append(f"{indent}{file_path.name}")
        
        return "\n".join(result)

    def generate_code_output(self, structure: Dict[str, List[Path]]) -> str:
        """Generate the formatted code output with separators and content"""
        result = []
        
        # Add structure overview
        result.append(self.format_directory_structure(structure))
        result.append("\n" + "=" * 100 + "\n")
        
        # Sort directories for consistent output
        sorted_dirs = sorted(structure.keys())
        
        for directory in sorted_dirs:
            files = sorted(structure[directory], key=lambda x: x.name)
            
            for file_path in files:
                # Get file info
                rel_path = file_path.relative_to(self.root_path)
                file_name = file_path.stem  # filename without extension
                extension = file_path.suffix
                language = self.get_language_from_extension(extension)
                
                # Create section header
                section_header = f"{directory}/{file_name}"
                if directory == 'root':
                    section_header = file_name
                    
                result.append(self.generate_separator(section_header))
                result.append(f"File: {rel_path}")
                result.append("-" * 100)
                
                # Read and add file content
                content = self.read_file_content(file_path)
                if content:
                    result.append(content)
                else:
                    result.append("// Unable to read file content")
                
                result.append("\n" + "=" * 100 + "\n")
        
        return "\n".join(result)

    def get_project_stats(self, structure: Dict[str, List[Path]]) -> Dict[str, int]:
        """Get statistics about the project"""
        stats = {
            'total_files': 0,
            'total_directories': len(structure),
            'total_lines': 0,
            'languages': {}
        }
        
        for directory, files in structure.items():
            stats['total_files'] += len(files)
            
            for file_path in files:
                # Count lines
                content = self.read_file_content(file_path)
                if content and isinstance(content, str):
                    stats['total_lines'] += len(content.splitlines())
                
                # Count languages
                language = self.get_language_from_extension(file_path.suffix)
                stats['languages'][language] = stats['languages'].get(language, 0) + 1
        
        return stats

    def generate_summary(self, structure: Dict[str, List[Path]], stats: Dict[str, int]) -> str:
        """Generate a summary of the codebase"""
        summary = []
        summary.append("=" * 100)
        summary.append("CODEBASE SUMMARY")
        summary.append("=" * 100)
        summary.append(f"Total Files: {stats['total_files']}")
        summary.append(f"Total Directories: {stats['total_directories']}")
        summary.append(f"Total Lines of Code: {stats['total_lines']}")
        summary.append(f"Root Directory: {self.root_path}")
        summary.append("")
        
        summary.append("Languages Found:")
        for language, count in sorted(stats['languages'].items()):
            summary.append(f"  {language}: {count} files")
        
        summary.append("")
        summary.append("Directory Overview:")
        for directory in sorted(structure.keys()):
            file_count = len(structure[directory])
            summary.append(f"  {directory}: {file_count} files")
        
        summary.append("=" * 100)
        return "\n".join(summary)

    def parse_and_output(self) -> bool:
        """Main method to parse codebase and generate output"""
        print(f"Parsing codebase in: {self.root_path}")
        print(f"Output file: {self.output_file}")
        
        # Check if root path exists
        if not self.root_path.exists():
            print(f"Error: Directory {self.root_path} does not exist")
            return False
        
        # Scan the directory structure
        print("Scanning directory structure...")
        structure = self.scan_directory(self.root_path)
        
        if not structure:
            print("No code files found in the specified directory")
            return False
        
        # Get project statistics
        stats = self.get_project_stats(structure)
        
        print(f"Found {stats['total_files']} code files in {stats['total_directories']} directories")
        
        # Generate output
        print("Generating formatted output...")
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                # Write summary
                f.write(self.generate_summary(structure, stats))
                f.write("\n\n")
                
                # Write detailed code content
                f.write(self.generate_code_output(structure))
            
            print(f"Successfully generated: {self.output_file}")
            print(f"File size: {os.path.getsize(self.output_file)} bytes")
            return True
            
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False

    def preview_structure(self) -> None:
        """Preview the structure without generating full output"""
        print(f"Previewing structure for: {self.root_path}\n")
        
        structure = self.scan_directory(self.root_path)
        if not structure:
            print("No code files found")
            return
        
        print(self.format_directory_structure(structure))
        print(f"\nFound {sum(len(files) for files in structure.values())} code files")

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse codebase and generate formatted documentation')
    parser.add_argument('path', nargs='?', default='.', 
                       help='Root path to parse (default: current directory)')
    parser.add_argument('-o', '--output', default='code.txt',
                       help='Output file name (default: code.txt)')
    parser.add_argument('-p', '--preview', action='store_true',
                       help='Preview structure only, do not generate full output')
    parser.add_argument('--extensions', 
                       help='Comma-separated list of additional file extensions to include')
    
    args = parser.parse_args()
    
    # Create parser instance
    codebase_parser = CodebaseParser(args.path, args.output)
    
    # Add custom extensions if provided
    if args.extensions:
        custom_exts = [ext.strip() for ext in args.extensions.split(',')]
        for ext in custom_exts:
            if not ext.startswith('.'):
                ext = '.' + ext
            codebase_parser.code_extensions.add(ext.lower())
        print(f"Added custom extensions: {custom_exts}")
    
    # Run preview or full parse
    if args.preview:
        codebase_parser.preview_structure()
    else:
        success = codebase_parser.parse_and_output()
        if not success:
            sys.exit(1)

# Enhanced version with additional features
class AdvancedCodebaseParser(CodebaseParser):
    """Extended parser with additional features"""
    
    def __init__(self, root_path: str = ".", output_file: str = "code.txt"):
        super().__init__(root_path, output_file)
        self.file_stats = {}
    
    def analyze_file_complexity(self, content: str, file_path: Path) -> Dict:
        """Analyze basic complexity metrics of a file"""
        if not content or not isinstance(content, str):
            return {}
        
        lines = content.splitlines()
        stats = {
            'lines_total': len(lines),
            'lines_code': 0,
            'lines_comment': 0,
            'lines_blank': 0,
            'functions': 0,
            'classes': 0
        }
        
        # Patterns for different languages
        comment_patterns = {
            '.py': [r'^\s*#', r'^\s*"""', r'^\s*\'\'\''],
            '.js': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            '.ts': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            '.java': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            '.cpp': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            '.c': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
        }
        
        function_patterns = {
            '.py': [r'^\s*def\s+\w+', r'^\s*async\s+def\s+\w+'],
            '.js': [r'^\s*function\s+\w+', r'^\s*const\s+\w+\s*=.*=>', r'^\s*\w+\s*:\s*function'],
            '.ts': [r'^\s*function\s+\w+', r'^\s*const\s+\w+\s*=.*=>', r'^\s*\w+\s*\(.*\)\s*:\s*\w+\s*{'],
            '.java': [r'^\s*(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\('],
            '.cpp': [r'^\s*\w+\s+\w+\s*\(', r'^\s*(public|private|protected):\s*\w+'],
            '.c': [r'^\s*\w+\s+\w+\s*\('],
        }
        
        class_patterns = {
            '.py': [r'^\s*class\s+\w+'],
            '.js': [r'^\s*class\s+\w+', r'^\s*function\s+[A-Z]\w+'],
            '.ts': [r'^\s*class\s+\w+', r'^\s*interface\s+\w+', r'^\s*type\s+\w+'],
            '.java': [r'^\s*(public|private)?\s*class\s+\w+', r'^\s*interface\s+\w+'],
            '.cpp': [r'^\s*class\s+\w+', r'^\s*struct\s+\w+'],
            '.c': [r'^\s*struct\s+\w+', r'^\s*typedef\s+struct'],
        }
        
        ext = file_path.suffix.lower()
        comment_regexes = [re.compile(pattern) for pattern in comment_patterns.get(ext, [])]
        function_regexes = [re.compile(pattern) for pattern in function_patterns.get(ext, [])]
        class_regexes = [re.compile(pattern) for pattern in class_patterns.get(ext, [])]
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped:
                stats['lines_blank'] += 1
            elif any(regex.match(line) for regex in comment_regexes):
                stats['lines_comment'] += 1
            else:
                stats['lines_code'] += 1
                
                # Count functions and classes
                if any(regex.match(line) for regex in function_regexes):
                    stats['functions'] += 1
                if any(regex.match(line) for regex in class_regexes):
                    stats['classes'] += 1
        
        return stats

    def generate_enhanced_output(self, structure: Dict[str, List[Path]]) -> str:
        """Generate enhanced output with code analysis"""
        result = []
        
        # Add structure overview
        result.append(self.format_directory_structure(structure))
        result.append("\n" + "=" * 100 + "\n")
        
        # Process each directory
        sorted_dirs = sorted(structure.keys())
        
        for directory in sorted_dirs:
            files = sorted(structure[directory], key=lambda x: x.name)
            
            # Directory header
            result.append(self.generate_separator(directory.upper()))
            result.append("")
            
            for file_path in files:
                rel_path = file_path.relative_to(self.root_path)
                file_name = file_path.stem
                extension = file_path.suffix
                language = self.get_language_from_extension(extension)
                
                # File header
                file_header = f"{file_name}"
                result.append(self.generate_separator(file_header))
                result.append(f"File: {rel_path}")
                result.append(f"Language: {language}")
                
                # Read content and analyze
                content = self.read_file_content(file_path)
                if content and isinstance(content, str):
                    file_stats = self.analyze_file_complexity(content, file_path)
                    self.file_stats[str(rel_path)] = file_stats
                    
                    if file_stats:
                        result.append(f"Lines: {file_stats['lines_total']} "
                                    f"(Code: {file_stats['lines_code']}, "
                                    f"Comments: {file_stats['lines_comment']}, "
                                    f"Blank: {file_stats['lines_blank']})")
                        if file_stats['functions'] > 0:
                            result.append(f"Functions: {file_stats['functions']}")
                        if file_stats['classes'] > 0:
                            result.append(f"Classes: {file_stats['classes']}")
                
                result.append("-" * 100)
                
                # Add file content
                if content:
                    result.append(content)
                else:
                    result.append("// Unable to read file content")
                
                result.append("\n" + "=" * 100 + "\n")
        
        return "\n".join(result)

    def parse_and_output(self) -> bool:
        """Enhanced parsing with code analysis"""
        print(f"Parsing codebase in: {self.root_path}")
        print(f"Output file: {self.output_file}")
        
        if not self.root_path.exists():
            print(f"Error: Directory {self.root_path} does not exist")
            return False
        
        print("Scanning directory structure...")
        structure = self.scan_directory(self.root_path)
        
        if not structure:
            print("No code files found in the specified directory")
            return False
        
        stats = self.get_project_stats(structure)
        print(f"Found {stats['total_files']} code files in {stats['total_directories']} directories")
        
        print("Analyzing code and generating output...")
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                # Write summary
                f.write(self.generate_summary(structure, stats))
                f.write("\n\n")
                
                # Write enhanced output with analysis
                f.write(self.generate_enhanced_output(structure))
            
            print(f"Successfully generated: {self.output_file}")
            print(f"File size: {os.path.getsize(self.output_file)} bytes")
            
            # Show code analysis summary
            if self.file_stats:
                total_functions = sum(stats.get('functions', 0) for stats in self.file_stats.values())
                total_classes = sum(stats.get('classes', 0) for stats in self.file_stats.values())
                print(f"Code Analysis: {total_functions} functions, {total_classes} classes found")
            
            return True
            
        except Exception as e:
            print(f"Error writing output file: {e}")
            return False

def create_example_usage():
    """Show example usage of the script"""
    examples = """
USAGE EXAMPLES:

1. Parse current directory:
   python codebase_parser.py

2. Parse specific directory:
   python codebase_parser.py /path/to/project

3. Preview structure only:
   python codebase_parser.py --preview

4. Custom output file:
   python codebase_parser.py -o my_code_analysis.txt

5. Add custom file extensions:
   python codebase_parser.py --extensions "vue,svelte,elm"

6. Parse and analyze with enhanced features:
   python codebase_parser.py --enhanced

The script will create a code.txt file with:
- Project structure overview
- Detailed code content for each file
- Code analysis metrics (lines, functions, classes)
- Language breakdown
"""
    print(examples)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        create_example_usage()
        sys.exit(0)
    
    # Check for enhanced mode
    if '--enhanced' in sys.argv:
        sys.argv.remove('--enhanced')
        # Use enhanced parser
        if len(sys.argv) > 1:
            parser = AdvancedCodebaseParser(sys.argv[1])
        else:
            parser = AdvancedCodebaseParser()
        parser.parse_and_output()
    else:
        # Use standard main function
        main()