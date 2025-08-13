"""

Git Integration Plugin (Python)

Provides Git repository management capabilities for CLI applications

"""



import asyncio

import json

import subprocess

import sys

from pathlib import Path

from typing import Dict, List, Optional, Any

from dataclasses import dataclass

from enum import Enum





class GitStatus(Enum):

    """Git repository status states"""

    CLEAN = "clean"

    MODIFIED = "modified" 

    STAGED = "staged"

    CONFLICTED = "conflicted"

    UNTRACKED = "untracked"





@dataclass

class GitFileStatus:

    """Git file status information"""

    path: str

    status: GitStatus

    staged: bool = False

    modified: bool = False





@dataclass

class GitCommit:

    """Git commit information"""

    hash: str

    author: str

    date: str

    message: str

    files_changed: int





class GitPlugin:

    """Git integration plugin for CLI applications"""

    

    def __init__(self, repo_path: Optional[Path] = None):

        self.repo_path = repo_path or Path.cwd()

        self.git_executable = self._find_git_executable()

    

    def _find_git_executable(self) -> str:

        """Find git executable in system PATH"""

        import shutil

        git_path = shutil.which('git')

        if not git_path:

            raise RuntimeError("Git executable not found in PATH")

        return git_path

    

    async def init_repository(self, bare: bool = False) -> bool:

        """Initialize a new git repository"""

        cmd = [self.git_executable, "init"]

        if bare:

            cmd.append("--bare")

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def clone_repository(self, url: str, target_dir: Optional[Path] = None) -> bool:

        """Clone a remote repository"""

        cmd = [self.git_executable, "clone", url]

        if target_dir:

            cmd.append(str(target_dir))

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def get_status(self) -> List[GitFileStatus]:

        """Get repository status"""

        cmd = [self.git_executable, "status", "--porcelain=v1"]

        

        try:

            result = await self._run_git_command(cmd)

            if result.returncode != 0:

                return []

            

            file_statuses = []

            for line in result.stdout.decode().strip().split('\n'):

                if not line:

                    continue

                

                status_code = line[:2]

                file_path = line[3:]

                

                # Parse git status codes

                staged = status_code[0] != ' '

                modified = status_code[1] != ' '

                

                if status_code.startswith('??'):

                    status = GitStatus.UNTRACKED

                elif status_code.startswith('UU'):

                    status = GitStatus.CONFLICTED

                elif staged:

                    status = GitStatus.STAGED

                elif modified:

                    status = GitStatus.MODIFIED

                else:

                    status = GitStatus.CLEAN

                

                file_statuses.append(GitFileStatus(

                    path=file_path,

                    status=status,

                    staged=staged,

                    modified=modified

                ))

            

            return file_statuses

            

        except Exception:

            return []

    

    async def add_files(self, files: List[str] = None) -> bool:

        """Add files to staging area"""

        cmd = [self.git_executable, "add"]

        if files:

            cmd.extend(files)

        else:

            cmd.append(".")

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def commit(self, message: str, author: Optional[str] = None) -> bool:

        """Create a commit"""

        cmd = [self.git_executable, "commit", "-m", message]

        if author:

            cmd.extend(["--author", author])

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def push(self, remote: str = "origin", branch: str = "main") -> bool:

        """Push commits to remote repository"""

        cmd = [self.git_executable, "push", remote, branch]

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def pull(self, remote: str = "origin", branch: str = "main") -> bool:

        """Pull commits from remote repository"""

        cmd = [self.git_executable, "pull", remote, branch]

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def get_log(self, limit: int = 10) -> List[GitCommit]:

        """Get commit history"""

        cmd = [

            self.git_executable, "log",

            f"--max-count={limit}",

            "--pretty=format:%H|%an|%ad|%s|%n",

            "--date=iso",

            "--numstat"

        ]

        

        try:

            result = await self._run_git_command(cmd)

            if result.returncode != 0:

                return []

            

            commits = []

            output_lines = result.stdout.decode().strip().split('\n')

            

            i = 0

            while i < len(output_lines):

                line = output_lines[i].strip()

                if not line or '|' not in line:

                    i += 1

                    continue

                

                parts = line.split('|')

                if len(parts) >= 4:

                    commit_hash = parts[0]

                    author = parts[1]

                    date = parts[2]

                    message = parts[3]

                    

                    # Count file changes

                    files_changed = 0

                    i += 1

                    while i < len(output_lines) and output_lines[i] and not '|' in output_lines[i]:

                        if output_lines[i].strip():

                            files_changed += 1

                        i += 1

                    

                    commits.append(GitCommit(

                        hash=commit_hash,

                        author=author,

                        date=date,

                        message=message,

                        files_changed=files_changed

                    ))

                else:

                    i += 1

            

            return commits

            

        except Exception:

            return []

    

    async def create_branch(self, branch_name: str, checkout: bool = True) -> bool:

        """Create a new branch"""

        cmd = [self.git_executable, "branch", branch_name]

        

        try:

            result = await self._run_git_command(cmd)

            if result.returncode != 0:

                return False

            

            if checkout:

                return await self.checkout_branch(branch_name)

            

            return True

        except Exception:

            return False

    

    async def checkout_branch(self, branch_name: str) -> bool:

        """Checkout a branch"""

        cmd = [self.git_executable, "checkout", branch_name]

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def get_current_branch(self) -> Optional[str]:

        """Get current branch name"""

        cmd = [self.git_executable, "branch", "--show-current"]

        

        try:

            result = await self._run_git_command(cmd)

            if result.returncode == 0:

                return result.stdout.decode().strip()

            return None

        except Exception:

            return None

    

    async def get_remote_url(self, remote: str = "origin") -> Optional[str]:

        """Get remote repository URL"""

        cmd = [self.git_executable, "remote", "get-url", remote]

        

        try:

            result = await self._run_git_command(cmd)

            if result.returncode == 0:

                return result.stdout.decode().strip()

            return None

        except Exception:

            return None

    

    async def is_repository(self) -> bool:

        """Check if current directory is a git repository"""

        cmd = [self.git_executable, "rev-parse", "--is-inside-work-tree"]

        

        try:

            result = await self._run_git_command(cmd)

            return result.returncode == 0

        except Exception:

            return False

    

    async def _run_git_command(self, cmd: List[str]) -> subprocess.CompletedProcess:

        """Run a git command asynchronously"""

        process = await asyncio.create_subprocess_exec(

            *cmd,

            cwd=self.repo_path,

            stdout=asyncio.subprocess.PIPE,

            stderr=asyncio.subprocess.PIPE

        )

        

        stdout, stderr = await process.communicate()

        

        return subprocess.CompletedProcess(

            args=cmd,

            returncode=process.returncode,

            stdout=stdout,

            stderr=stderr

        )

    

    def get_plugin_info(self) -> Dict[str, Any]:

        """Get plugin information for marketplace"""

        return {

            "name": "git-integration",

            "version": "1.0.0",

            "author": "Goobits Framework",

            "description": "Git repository management and integration",

            "language": "python",

            "dependencies": [],

            "capabilities": [

                "repository_init",

                "status_checking", 

                "commit_management",

                "branch_operations",

                "remote_operations",

                "history_viewing"

            ],

            "commands": {

                "git-status": "Show repository status with enhanced formatting",

                "git-quick-commit": "Quick commit with automatic staging",

                "git-branch-info": "Show current branch and remote information",

                "git-sync": "Synchronize with remote repository"

            }

        }





# CLI Integration hooks for Goobits

async def on_git_status(*args, **kwargs):

    """CLI hook for git status command"""

    plugin = GitPlugin()

    

    if not await plugin.is_repository():

        print("❌ Not a git repository")

        return

    

    print("📊 Repository Status:")

    status = await plugin.get_status()

    

    if not status:

        print("✅ Working tree clean")

        return

    

    # Group files by status

    status_groups = {}

    for file_status in status:

        if file_status.status not in status_groups:

            status_groups[file_status.status] = []

        status_groups[file_status.status].append(file_status.path)

    

    # Display grouped status

    status_icons = {

        GitStatus.STAGED: "✅",

        GitStatus.MODIFIED: "📝", 

        GitStatus.UNTRACKED: "❓",

        GitStatus.CONFLICTED: "⚠️"

    }

    

    for status_type, files in status_groups.items():

        icon = status_icons.get(status_type, "📄")

        print(f"\n{icon} {status_type.value.title()}:")

        for file in files:

            print(f"  {file}")





async def on_git_quick_commit(*args, **kwargs):

    """CLI hook for quick commit command"""

    plugin = GitPlugin()

    

    if not await plugin.is_repository():

        print("❌ Not a git repository")

        return

    

    # Get commit message from arguments

    message = " ".join(args) if args else "Quick commit"

    

    print("🚀 Performing quick commit...")

    

    # Add all files

    if await plugin.add_files():

        print("✅ Files staged")

    else:

        print("❌ Failed to stage files")

        return

    

    # Commit

    if await plugin.commit(message):

        print(f"✅ Committed: {message}")

    else:

        print("❌ Failed to create commit")





async def on_git_branch_info(*args, **kwargs):

    """CLI hook for branch info command"""

    plugin = GitPlugin()

    

    if not await plugin.is_repository():

        print("❌ Not a git repository")

        return

    

    print("🌿 Branch Information:")

    

    # Current branch

    current_branch = await plugin.get_current_branch()

    if current_branch:

        print(f"  Current: {current_branch}")

    

    # Remote URL

    remote_url = await plugin.get_remote_url()

    if remote_url:

        print(f"  Remote: {remote_url}")





async def on_git_sync(*args, **kwargs):

    """CLI hook for git sync command"""

    plugin = GitPlugin()

    

    if not await plugin.is_repository():

        print("❌ Not a git repository")

        return

    

    print("🔄 Synchronizing with remote...")

    

    # Pull latest changes

    if await plugin.pull():

        print("✅ Pulled latest changes")

    else:

        print("⚠️ Failed to pull (may be up to date)")

    

    # Push local commits

    if await plugin.push():

        print("✅ Pushed local commits")

    else:

        print("⚠️ Failed to push (may be up to date)")

    

    print("🎉 Sync complete!")





if __name__ == "__main__":

    # Example usage

    async def demo():

        plugin = GitPlugin()

        

        if await plugin.is_repository():

            print("Git repository detected")

            

            # Show status

            status = await plugin.get_status()

            print(f"Files with changes: {len(status)}")

            

            # Show recent commits

            commits = await plugin.get_log(5)

            print(f"Recent commits: {len(commits)}")

            for commit in commits[:3]:

                print(f"  {commit.hash[:8]}: {commit.message}")

        else:

            print("Not a git repository")

    

    asyncio.run(demo())