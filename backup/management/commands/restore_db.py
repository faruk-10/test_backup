import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Restore the PostgreSQL database from the latest backup."

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        db_name = db["NAME"]
        db_user = db["USER"]
        db_password = db["PASSWORD"]
        db_host = db["HOST"] or "localhost"
        db_port = db["PORT"] or "5432"

        os.environ["PGPASSWORD"] = db_password

        backup_file = Path.cwd() / "db_backup" / "backup_1.dump"
        if not backup_file.exists():
            self.stderr.write(self.style.ERROR("❌ backup_1.dump not found."))
            return

        self.stdout.write(self.style.WARNING(f"⚠️ Restoring from: {backup_file}"))

        # Kill other connections
        try:
            subprocess.run([
                "psql",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", "postgres",
                "-c", (
                    f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    f"WHERE datname = '{db_name}' AND pid <> pg_backend_pid();"
                )
            ], check=True)
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to terminate sessions: {e}"))
            return

        # Drop and recreate the database
        try:
            subprocess.run([
                "psql",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", "postgres",
                "-c", f"DROP DATABASE IF EXISTS {db_name};"
            ], check=True)

            subprocess.run([
                "createdb",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                db_name
            ], check=True)
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Could not drop/create database: {e}"))
            return

        # Restore using pg_restore
        try:
            subprocess.run([
                "pg_restore",
                "-U", db_user,
                "-h", db_host,
                "-p", db_port,
                "-d", db_name,
                "-F", "c",
                "--clean",
                "--if-exists",
                "--no-owner",
                str(backup_file)
            ], check=True)

            self.stdout.write(self.style.SUCCESS("✅ Database restored successfully."))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Restore failed: {e}"))
