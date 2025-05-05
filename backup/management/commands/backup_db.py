import os
import subprocess
from django.core.management.base import BaseCommand
from pathlib import Path
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = "Backup full PostgreSQL database and data using pg_dump"

    def handle(self, *args, **kwargs):
        db_settings = settings.DATABASES['default']

        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST'] or 'localhost'
        db_port = str(db_settings['PORT'] or '5432')

        if not db_password:
            self.stderr.write(self.style.ERROR("❌ DB_PASSWORD is not set."))
            return

        os.environ["PGPASSWORD"] = db_password

        backup_dir = Path.cwd()/ "db_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

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


        try:
            subprocess.run([
                "pg_dump",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", db_name,
                "-f", str(backup_1),
                "-F", "plain"  # plain SQL format
            ], check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Database backup created: {backup_1}"))
            call_command('push_backup_to_git')

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Backup failed: {e}"))
