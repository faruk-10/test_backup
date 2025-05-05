import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    help = "Create a PostgreSQL database backup and keep the last two versions."

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        db_name = db["NAME"]
        db_user = db["USER"]
        db_password = db["PASSWORD"]
        db_host = db["HOST"] or "localhost"
        db_port = db["PORT"] or "5432"

        if not db_password:
            self.stderr.write(self.style.ERROR("❌ DB_PASSWORD is not set in settings."))
            return

        os.environ["PGPASSWORD"] = db_password

        backup_dir = Path.cwd() / "db_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_1 = backup_dir / "backup_1.dump"
        backup_2 = backup_dir / "backup_2.dump"

        if backup_2.exists():
            backup_2.unlink()
            self.stdout.write(self.style.WARNING("🗑️ Deleted old backup_2.dump"))

        if backup_1.exists():
            backup_1.rename(backup_2)
            self.stdout.write(self.style.SUCCESS("🔁 Renamed backup_1.dump to backup_2.dump"))

        try:
            subprocess.run([
                "pg_dump",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", db_name,
                "-f", str(backup_1),
                "-F", "c"  # custom format
            ], check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Backup created: {backup_1}"))
            call_command('push_backup_to_git')
            

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Backup failed: {e}"))
