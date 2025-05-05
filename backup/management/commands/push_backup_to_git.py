import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.management import call_command

class Command(BaseCommand):
    help = "Push the latest database backup to a Git repository"

    def handle(self, *args, **kwargs):
        call_command('delete_old_backups')
        backup_dir = Path.cwd() / "db_backup"
        if not backup_dir.exists():
            self.stderr.write(self.style.ERROR("❌ Backup directory does not exist."))
            return

        # Get the latest backup file
        backups = sorted(backup_dir.glob("*.dump"), key=os.path.getmtime, reverse=True)
        if not backups:
            self.stderr.write(self.style.ERROR("❌ No backup file found."))
            return

        latest_backup = backups[0]
        git_repo_dir = Path.cwd()  # Use the current directory where the git repo is initialized

        # Check if the Git repository exists (i.e., if it's a valid Git directory)
        if not (git_repo_dir / ".git").exists():
            self.stderr.write(self.style.ERROR("❌ Not a Git repository directory."))
            return

        # Copy the latest backup directly into the Git repository
        backup_filename = latest_backup.name

        # Change directory to Git repository and perform Git operations
        try:
            subprocess.run(["git", "add", "."], cwd=git_repo_dir, check=True)
            commit_message = f"Backup: {backup_filename} - {now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], cwd=git_repo_dir, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=git_repo_dir, check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Backup {backup_filename} pushed to Git repository."))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Git operation failed: {e}"))
