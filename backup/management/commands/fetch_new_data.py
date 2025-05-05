import subprocess
from django.core.management.base import BaseCommand
from pathlib import Path

class Command(BaseCommand):
    help = "Fetch the latest backup data from the Git repository."

    def handle(self, *args, **options):
        backup_dir = Path.cwd() / "db_backup"
        if not backup_dir.exists():
            self.stderr.write(self.style.ERROR("❌ db_backup directory does not exist."))
            return

        try:
            # Pull latest changes from git
            subprocess.run(["git", "pull", "origin", "main"], cwd=backup_dir, check=True)
            self.stdout.write(self.style.SUCCESS("✅ Latest backup pulled from Git."))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to pull backup: {e}"))
