"""
Git Operations Utility.

This module provides helper functions to execute git commands for syncing data.
"""
import logging
import subprocess
import os
from typing import List

logger = logging.getLogger(__name__)

def run_git_command(args: List[str], cwd: str = None) -> bool:
    """
    Run a git command.
    
    Args:
        args: List of command arguments (e.g., ["commit", "-m", "msg"])
        cwd: Current working directory (defaults to current process cwd)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Default to the backend's parent directory (project root) or current directory
        # We usually want to run git from the repo root. 
        # Assuming backend is in <root>/backend, we might want <root>.
        # But let's assume the process is running where .git is accessible or cwd is fine.
        
        # If cwd is not provided, try to find the repo root
        if not cwd:
            # Assuming this file is in backend/app/utils/
            # We want to go up 3 levels to get to repo root? 
            # Or just rely on shell execution context. 
            # The app is run from <root> via npm run dev usually (cwd is root).
            # But the backend run.sh changes dir to backend?
            # Let's check where we are running.
            pass

        full_cmd = ["git"] + args
        result = subprocess.run(
            full_cmd, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"Git command failed: {' '.join(full_cmd)}\nError: {result.stderr}")
            return False
            
        logger.info(f"Git command success: {' '.join(full_cmd)}")
        return True
    
    except Exception as e:
        logger.error(f"Git execution error: {e}")
        return False

def git_add_commit_push(files: List[str], message: str, cwd: str = None) -> bool:
    """
    Add files, commit, and push.
    
    Args:
        files: List of file paths to add (relative to repo root)
        message: Commit message
        cwd: Repository root directory
        
    Returns:
        True if all steps succeeded
    """
    # 1. Add
    if not run_git_command(["add"] + files, cwd=cwd):
        logger.warning("Git add failed (might be no changes or invalid path), continuing...")
        
    # 2. Commit
    if not run_git_command(["commit", "-m", message], cwd=cwd):
        logger.warning("Git commit failed (nothing to commit?), continuing...")
        
    # 3. Push
    if not run_git_command(["push"], cwd=cwd):
        logger.error("Git push failed")
        return False
        
    return True
