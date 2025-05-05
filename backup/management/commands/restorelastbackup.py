import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Restore the latest backup SQL file to the PostgreSQL database"

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
        backups = sorted(backup_dir.glob("*.sql"), key=os.path.getmtime, reverse=True)

        if not backups:
            self.stderr.write(self.style.ERROR("❌ No backup file found."))
            return

        latest_backup = backups[0]

        self.stdout.write(f"⚠️  Restoring from: {latest_backup}")
        
        try:
            subprocess.run([
                "psql",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", db_name,
                "-f", str(latest_backup)
            ], check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Database restored from: {latest_backup.name}"))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Restore failed: {e}"))
