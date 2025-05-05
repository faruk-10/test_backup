import os
from pathlib import Path
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Delete old backup files if more than 5 backups exist."

    def handle(self, *args, **kwargs):
        backup_dir = Path.cwd() / "db_backup"
        if not backup_dir.exists():
            self.stderr.write(self.style.ERROR("❌ Backup directory does not exist."))
            return

        # Get all SQL backup files in the directory
        backups = sorted(backup_dir.glob("*.sql"), key=os.path.getmtime)

        # Check if there are more than 5 backup files
        if len(backups) > 5:
            files_to_delete = backups[:-3]  # Select the oldest files to delete

            # Delete the old backup files
            for file in files_to_delete:
                try:
                    file.unlink()  # Delete the file
                    self.stdout.write(self.style.SUCCESS(f"✅ Deleted old backup file: {file.name}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Failed to delete file {file.name}: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ No old backup files to delete."))
