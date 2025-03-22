#!/usr/bin/env python3
"""
Lists all code files in the project.
"""

import sys
from pathlib import Path
from typing import Callable, Optional, Tuple
import typer
from rich.console import Console
from rich.progress import track
from collections import Counter


"""
Usage:

python scripts/list_code_files.py --root foo/ --exclude node_modules --extensions py,js,ts
python scripts/list_code_files.py -x .py .js -e node_modules
"""

# Define default directories to exclude
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    ".cursor",
}

# Define default code file extensions
DEFAULT_CODE_EXTENSIONS = {
    # Python
    ".py",
    # JavaScript/TypeScript
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    # Web
    ".html",
    ".css",
    ".scss",
    ".sass",
    # Templates
    ".jinja",
    ".svelte",
    # Configuration
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    # Shell scripts
    ".sh",
    ".bash",
    # Markdown
    ".md",
    ".mdx",
    ".mdc",
    # SQL
    ".sql",
    # Docker
    "Dockerfile",
    ".dockerignore",
    # Git
    ".gitignore",
    # Miscellaneous
    ".env.example",
    ".flake8",
    ".ini",
}

# Initialize console
console = Console()

# Create Typer app
app = typer.Typer(
    help="Lists all code files in the project, with options to filter by file extension and exclude directories.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)


def is_code_file(path: Path, extensions: set[str]) -> bool:
    """
    Determines if a file is a code file based on its extension.

    Args:
        path: The file path to check.
        extensions: set of file extensions to consider as code files.

    Returns:
        True if the file is a code file, False otherwise.
    """
    # Check if the file has a code extension
    if path.suffix.lower() in extensions:
        return True

    # Check for files without extensions but with specific names
    if path.name in extensions:
        return True

    return False


def filter_code_files(
    all_files: list[Path], exclude_dirs: set[str], extensions: set[str]
) -> list[Path]:
    code_files = []
    for path in track(all_files, description="Scanning files"):
        if path.is_dir():
            continue
        # Skip excluded directories
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        # Check if it's a code file
        if is_code_file(path, extensions):
            code_files.append(path)
    return code_files


def find_code_files(
    root_dir: Path,
    exclude_dirs: set[str],
    extensions: set[str],
    sort_key: Callable[[Path], str] = lambda x: x.suffix + str(x).lower(),
) -> list[Path]:
    # lambda x: (x.suffix + str(x))
    all_files = list(root_dir.rglob("*"))
    filtered_files = filter_code_files(all_files, exclude_dirs, extensions)
    sorted_files = sorted(filtered_files, key=sort_key)
    return sorted_files


def count_extensions(code_files: list[Path]) -> dict[str, int]:
    """
    Dictionary mapping extensions to counts.
    """
    return Counter(
        file.suffix.lower() if file.suffix else file.name for file in code_files
    )


def print_summary(code_files: list[Path], extensions_count: dict[str, int]) -> None:
    """
    e.g.
    Found 100 code files with these extensions:
    py: 50
    js: 30
    ts: 20
    """
    console.print(
        "\n[green]Found {count} code files with these extensions:[/green]".format(
            count=len(code_files)
        )
    )
    for ext, count in sorted(
        extensions_count.items(), key=lambda x: x[1], reverse=True
    ):
        console.print(f"[cyan]{ext}:[/cyan] {count} files")


def print_files(root_dir: Path, code_files: list[Path]) -> None:
    console.print("\n[green]All code files:[/green]")
    for file in code_files:
        rel_path = file.relative_to(root_dir)
        console.print(f"{rel_path}")


def setup_search(
    root: str, exclude: Optional[list[str]], extensions: Optional[list[str]]
) -> Tuple[Path, set[str], set[str]]:
    root_dir = Path(root).resolve()
    exclude_dirs = set(exclude) if exclude else DEFAULT_EXCLUDE_DIRS
    file_extensions = set(extensions) if extensions else DEFAULT_CODE_EXTENSIONS

    console.print(f"[green]Searching for code files in {root_dir}...[/green]")
    console.print(f"[yellow]Excluding directories: {', '.join(exclude_dirs)}[/yellow]")
    console.print(
        f"[yellow]Including extensions: {', '.join(sorted(file_extensions))}[/yellow]"
    )
    return root_dir, exclude_dirs, file_extensions


@app.command()
def list_files(
    root: str = typer.Option(".", "--root", "-r", help="Root directory to search"),
    exclude: Optional[list[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Directories to exclude from the search (default: git, node_modules, etc.)",
    ),
    extensions: Optional[list[str]] = typer.Option(
        None,
        "--extensions",
        "-x",
        help="File extensions to include in the search (default: py, js, ts, etc.)",
    ),
    summary: bool = typer.Option(
        False,
        "--summary",
        "-s",
        help="Print summary of file extensions",
    ),
) -> int:
    root_dir, exclude_dirs, file_extensions = setup_search(root, exclude, extensions)
    code_files = find_code_files(root_dir, exclude_dirs, file_extensions)

    if summary:
        extensions_count = count_extensions(code_files)
        print_summary(code_files, extensions_count)

    print_files(root_dir, code_files)
    return 0


if __name__ == "__main__":
    app()
