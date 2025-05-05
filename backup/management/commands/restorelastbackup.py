import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Pulls latest backup from Git, rotates backup files, and restores database from backup_1.sql"

    def handle(self, *args, **kwargs):
        db_settings = settings.DATABASES['default']

        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST'] or 'localhost'
        db_port = str(db_settings['PORT'] or '5432')

        if not db_password:
            self.stderr.write(self.style.ERROR("❌ DB_PASSWORD not set."))
            return

        os.environ["PGPASSWORD"] = db_password

        backup_dir = Path.cwd() / "db_backup"
        backup_1 = backup_dir / "backup_1.sql"


        # Drop the database
        subprocess.run([
            "psql", "-U", db_user, "-h", db_host, "-p", db_port,
            "-c", f"DROP DATABASE IF EXISTS {db_name};"
        ], check=True)

        print(f"✅ Database {db_name} dropped.")

        # Recreate the database
        subprocess.run([
            "psql", "-U", db_user, "-h", db_host, "-p", db_port,
            "-c", f"CREATE DATABASE {db_name};"
        ], check=True)

        print(f"✅ Database {db_name} created.")
        
        # Git pull to fetch latest backup
        try:
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            self.stdout.write(self.style.SUCCESS("✅ Pulled latest backup files from Git."))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"❌ Git pull failed: {e}"))
            return

        # Check again if backup_1 exists after pull
        if not backup_1.exists():
            self.stderr.write(self.style.ERROR("❌ backup_1.sql not found after pull. Cannot restore."))
            return

        self.stdout.write(self.style.WARNING(f"⚠️ Restoring from: {backup_1}"))

        # Restore using psql
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
