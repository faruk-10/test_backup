import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.timezone import now

class Command(BaseCommand):
    help = "Push the latest database backup to a Git repository"

    def handle(self, *args, **kwargs):
        backup_dir = Path.cwd() / "db_backup"
        if not backup_dir.exists():
            self.stderr.write(self.style.ERROR("❌ Backup directory does not exist."))
            return

        # Get the latest backup file
        backups = sorted(backup_dir.glob("*.sql"), key=os.path.getmtime, reverse=True)
        if not backups:
            self.stderr.write(self.style.ERROR("❌ No backup file found."))
            return

        latest_backup = backups[0]
        git_repo_dir = Path.cwd() / "db_backup_repo"  # Change this to your Git repo directory

        if not git_repo_dir.exists():
            self.stderr.write(self.style.ERROR("❌ Git repository directory does not exist."))
            return

        # Copy the latest backup to the Git repository
        backup_filename = latest_backup.name
        destination = git_repo_dir / backup_filename
        subprocess.run(["cp", str(latest_backup), str(destination)], check=True)

        # Change directory to Git repository and perform Git operations
        try:
            subprocess.run(["git", "add", backup_filename], cwd=git_repo_dir, check=True)
            commit_message = f"Backup: {backup_filename} - {now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], cwd=git_repo_dir, check=True)
            subprocess.run(["git", "push"], cwd=git_repo_dir, check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Backup {backup_filename} pushed to Git repository."))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Git operation failed: {e}"))
