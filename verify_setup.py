#!/usr/bin/env python3
"""
Verification script for MCP Examples repository.

Checks that all required files exist and dependencies can be imported.
Run this after installation to verify setup.
"""

import sys
from pathlib import Path

def check_file_exists(path: Path, description: str) -> bool:
    """Check if a file exists."""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (NOT FOUND)")
        return False

def check_import(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✓ {module_name} can be imported")
        return True
    except ImportError:
        print(f"✗ {module_name} cannot be imported")
        return False

def main():
    print("=" * 60)
    print("MCP Examples Repository - Setup Verification")
    print("=" * 60)
    print()

    repo_root = Path(__file__).parent
    all_checks_passed = True

    # Check core files
    print("Checking core files...")
    core_files = [
        (repo_root / "README.md", "Main README"),
        (repo_root / "LICENSE", "License file"),
        (repo_root / "requirements.txt", "Root requirements"),
        (repo_root / ".gitignore", "Gitignore file"),
    ]

    for path, desc in core_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False
    print()

    # Check documentation
    print("Checking documentation...")
    doc_files = [
        (repo_root / "docs" / "what-is-mcp.md", "What is MCP guide"),
        (repo_root / "docs" / "setup-guide.md", "Setup guide"),
        (repo_root / "docs" / "testing-with-claude.md", "Testing guide"),
    ]

    for path, desc in doc_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False
    print()

    # Check Docker Dev Assistant
    print("Checking Docker Dev Assistant...")
    docker_files = [
        (repo_root / "docker-dev-assistant" / "server.py", "Server script"),
        (repo_root / "docker-dev-assistant" / "README.md", "README"),
        (repo_root / "docker-dev-assistant" / "requirements.txt", "Requirements"),
        (repo_root / "docker-dev-assistant" / "docker-compose.yml", "Docker Compose example"),
    ]

    for path, desc in docker_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False
    print()

    # Check Personal Knowledge Base
    print("Checking Personal Knowledge Base...")
    kb_files = [
        (repo_root / "personal-knowledge-base" / "server.py", "Server script"),
        (repo_root / "personal-knowledge-base" / "README.md", "README"),
        (repo_root / "personal-knowledge-base" / "requirements.txt", "Requirements"),
        (repo_root / "personal-knowledge-base" / "sample-notes" / "projects.md", "Sample note: projects"),
        (repo_root / "personal-knowledge-base" / "sample-notes" / "ideas.md", "Sample note: ideas"),
        (repo_root / "personal-knowledge-base" / "sample-notes" / "learnings.md", "Sample note: learnings"),
    ]

    for path, desc in kb_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False
    print()

    # Check Smart Day Planner
    print("Checking Smart Day Planner...")
    planner_files = [
        (repo_root / "smart-day-planner" / "server.py", "Server script"),
        (repo_root / "smart-day-planner" / "README.md", "README"),
        (repo_root / "smart-day-planner" / "requirements.txt", "Requirements"),
        (repo_root / "smart-day-planner" / ".env.example", "Environment template"),
        (repo_root / "smart-day-planner" / "config.yaml", "Configuration file"),
    ]

    for path, desc in planner_files:
        if not check_file_exists(path, desc):
            all_checks_passed = False
    print()

    # Check Python dependencies
    print("Checking Python dependencies...")
    dependencies = [
        "mcp",
    ]

    for dep in dependencies:
        if not check_import(dep):
            all_checks_passed = False
            print(f"  → Install with: pip install -r requirements.txt")
    print()

    # Optional dependencies
    print("Checking optional dependencies...")
    optional_deps = {
        "chromadb": "Required for Personal Knowledge Base",
        "sentence_transformers": "Required for Personal Knowledge Base",
        "aiohttp": "Required for Smart Day Planner",
        "yaml": "Required for Smart Day Planner",
    }

    for dep, purpose in optional_deps.items():
        if check_import(dep):
            print(f"  {purpose}")
        else:
            print(f"  {purpose} - Not installed (optional)")
    print()

    # Final status
    print("=" * 60)
    if all_checks_passed:
        print("✓ All checks passed! Repository is set up correctly.")
        print()
        print("Next steps:")
        print("1. Read docs/setup-guide.md for installation instructions")
        print("2. Start with docker-dev-assistant/")
        print("3. Configure Claude Desktop to use the servers")
    else:
        print("✗ Some checks failed. Please review the output above.")
        print()
        print("Common fixes:")
        print("- Run: pip install -r requirements.txt")
        print("- Check that all files were cloned correctly")
        print("- Ensure you're in the correct directory")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
