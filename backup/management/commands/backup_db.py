import os
import subprocess
from django.core.management.base import BaseCommand
from pathlib import Path
from django.core.management import call_command

class Command(BaseCommand):
    help = "Backup full PostgreSQL database and data using pg_dump"

    def handle(self, *args, **kwargs):
        db_name = os.environ.get("DB_NAME", "autoupdate")
        db_user = os.environ.get("DB_USER", "admin")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "5432")

        if not db_password:
            self.stderr.write(self.style.ERROR("❌ DB_PASSWORD is not set."))
            return

        os.environ["PGPASSWORD"] = db_password

        backup_dir = Path.cwd()/ "db_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{db_name}_1.sql"
        filepath = backup_dir / filename

        try:
            subprocess.run([
                "pg_dump",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", db_name,
                "-f", str(filepath),
                "-F", "plain"  # plain SQL format
            ], check=True)

            self.stdout.write(self.style.SUCCESS(f"✅ Database backup created: {filepath}"))
            call_command('push_backup_to_git')

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Backup failed: {e}"))
