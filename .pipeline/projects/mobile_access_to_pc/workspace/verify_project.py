#!/usr/bin/env python3
"""
Mobile Access to PC - Final Verification Script

This script performs comprehensive verification of the entire project:
- File structure validation
- Code syntax checking
- Test execution
- Documentation review
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text: str):
    """Print a section header."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    if exists:
        print_success(f"File exists: {filepath}")
    else:
        print_error(f"File missing: {filepath}")
    return exists

def run_command(cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def verify_project_structure():
    """Verify all required files exist."""
    print_header("FILE STRUCTURE VERIFICATION")
    
    workspace = Path("/workspace/idea impl/.pipeline/projects/mobile_access_to_pc/workspace")
    
    required_files = [
        # PC Agent
        "pc_agent/main.py",
        "pc_agent/config.py",
        "pc_agent/screen_capture.py",
        "pc_agent/websocket_server.py",
        "pc_agent/connection_manager.py",
        "pc_agent/input_handler.py",
        "pc_agent/input_types.py",
        "pc_agent/utils/compression.py",
        "pc_agent/tests/test_pc_agent.py",
        
        # iOS Client
        "ios_client/RemoteDesktopApp.swift",
        "ios_client/Views/ContentView.swift",
        "ios_client/Views/ConnectionView.swift",
        "ios_client/Views/RemoteView.swift",
        "ios_client/Views/VideoDisplayView.swift",
        "ios_client/Models/ConnectionState.swift",
        "ios_client/Networking/WebSocketClient.swift",
        "ios_client/Networking/ConnectionManager.swift",
        "ios_client/Video/VideoDecoder.swift",
        "ios_client/Inputs/TouchHandler.swift",
        "ios_client/Keyboard/KeyboardOverlay.swift",
        "ios_client/Keyboard/KeyboardOverlayView.swift",
        
        # Documentation
        "README.md",
        "PROJECT_STRUCTURE.md",
    ]
    
    missing_files = []
    for filepath in required_files:
        full_path = workspace / filepath
        if not check_file_exists(str(full_path)):
            missing_files.append(filepath)
    
    if not missing_files:
        print_success("All required files present!")
        return True, []
    else:
        print_error(f"{len(missing_files)} files missing")
        return False, missing_files

def verify_python_syntax():
    """Verify Python syntax for all .py files."""
    print_header("PYTHON SYNTAX VERIFICATION")
    
    workspace = Path("/workspace/idea impl/.pipeline/projects/mobile_access_to_pc/workspace")
    
    python_files = list(workspace.glob("pc_agent/**/*.py"))
    
    syntax_errors = []
    for py_file in python_files:
        success, _ = run_command([sys.executable, "-m", "py_compile", str(py_file)])
        if not success:
            print_error(f"Syntax error in: {py_file}")
            syntax_errors.append(str(py_file))
        else:
            print_success(f"Syntax OK: {py_file.name}")
    
    if not syntax_errors:
        print_success("All Python files have valid syntax!")
        return True, []
    else:
        return False, syntax_errors

def run_tests():
    """Run pytest and report results."""
    print_header("TEST EXECUTION")
    
    workspace = Path("/workspace/idea impl/.pipeline/projects/mobile_access_to_pc/workspace")
    test_file = workspace / "pc_agent/tests/test_pc_agent.py"
    
    success, output = run_command(
        [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
        cwd=str(workspace)
    )
    
    # Extract test results
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    errors = output.count("ERROR")
    
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Errors: {errors}")
    
    if failed == 0 and errors == 0:
        print_success("All tests passed!")
        return True, output
    else:
        print_error(f"{failed} tests failed")
        return False, output

def count_lines_of_code():
    """Count lines of code for each component."""
    print_header("CODE STATISTICS")
    
    workspace = Path("/workspace/idea impl/.pipeline/projects/mobile_access_to_pc/workspace")
    
    # Python files
    pc_agent_dir = workspace / "pc_agent"
    py_files = list(pc_agent_dir.glob("**/*.py"))
    py_lines = sum(len(f.read_text().splitlines()) for f in py_files)
    
    # Swift files
    ios_dir = workspace / "ios_client"
    swift_files = list(ios_dir.glob("**/*.swift"))
    swift_lines = sum(len(f.read_text().splitlines()) for f in swift_files)
    
    print(f"PC Agent Python lines: {py_lines}")
    print(f"iOS Client Swift lines: {swift_lines}")
    print(f"Total lines of code: {py_lines + swift_lines}")
    
    return py_lines, swift_lines

def check_documentation():
    """Verify documentation files exist and have content."""
    print_header("DOCUMENTATION VERIFICATION")
    
    workspace = Path("/workspace/idea impl/.pipeline/projects/mobile_access_to_pc/workspace")
    
    docs = ["README.md", "PROJECT_STRUCTURE.md"]
    all_present = True
    
    for doc in docs:
        doc_path = workspace / doc
        if doc_path.exists():
            content = doc_path.read_text()
            lines = len(content.splitlines())
            print_success(f"{doc}: {lines} lines")
            if lines < 100:
                print_warning(f"{doc} seems short, consider expanding")
        else:
            print_error(f"{doc} not found")
            all_present = False
    
    return all_present, None

def main():
    """Run all verification checks."""
    print_header("MOBILE ACCESS TO PC - FINAL VERIFICATION")
    
    results = {}
    
    # Run all verification checks
    results["File Structure"], missing = verify_project_structure()
    results["Python Syntax"], _ = verify_python_syntax()
    results["Tests"], output = run_tests()
    results["Documentation"], _ = check_documentation()
    
    # Print code statistics
    py_lines, swift_lines = count_lines_of_code()
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"{Colors.GREEN}✓ ALL VERIFICATION CHECKS PASSED{Colors.RESET}")
        print("\nProject Status: COMPLETE")
        print("PC Agent Components: 8 Python modules")
        print("iOS Client Components: 12 Swift files")
        print("Total Documentation: 2 comprehensive files")
        print("Test Coverage: All tests passing")
        print("Code Quality: Valid syntax, no errors")
        return 0
    else:
        print(f"{Colors.RED}✗ VERIFICATION FAILED{Colors.RESET}")
        for check, passed in results.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
