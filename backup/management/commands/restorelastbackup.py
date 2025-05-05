import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Pull latest backup and restore the latest backup SQL file to the PostgreSQL database"

    def handle(self, *args, **kwargs):
        db_name = os.environ.get("DB_NAME", "autoupdate")
        db_user = os.environ.get("DB_USER", "admin")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "5432")

        if not db_password:
            self.stderr.write(self.style.ERROR("❌ DB_PASSWORD not set."))
            return

        os.environ["PGPASSWORD"] = db_password

        backup_dir = Path.cwd() / "db_backup"
        backup_1 = backup_dir / "backup_1.sql"
        backup_2 = backup_dir / "backup_2.sql"

        # Delete backup_2 if it exists
        if backup_2.exists():
            backup_2.unlink()
            self.stdout.write(self.style.WARNING("🗑️ Deleted old backup_2.sql"))

        # Rename backup_1 to backup_2 if it exists
        if backup_1.exists():
            backup_1.rename(backup_2)
            self.stdout.write(self.style.SUCCESS("🔁 Renamed backup_1.sql to backup_2.sql"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ backup_1.sql not found, skipping rename"))


        # Step 1: Git pull to get the latest backup files
        try:
            subprocess.run(["git", "pull", "origin", "main"])
            self.stdout.write(self.style.SUCCESS("✅ Pulled latest backup files from Git repository."))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Git pull failed: {e}"))
            return

        # Step 2: Get latest backup file
        if not backup_1:
            self.stderr.write(self.style.ERROR("❌ No backup file found."))
            return
        
        self.stdout.write(f"⚠️  Restoring from: {backup_1}")
        
        # Step 3: Restore the backup using psql
        try:
            subprocess.run([
                "psql",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", db_name,
                "-f", str(backup_1)
            ], check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Database restored from: {backup_1}"))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Restore failed: {e}"))


