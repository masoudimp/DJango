"""Prepare the local environment and start the assignment with one command."""

import argparse
from pathlib import Path
import subprocess
import sys
import venv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000, help="Local server port (default: 8000)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    if sys.version_info < (3, 12):
        parser.error("Python 3.12 or newer is required")

    project = Path(__file__).resolve().parent
    environment = project / ".venv"
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    if not python.exists():
        print("Creating the project virtual environment…", flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)

    def run(*arguments):
        subprocess.run([str(python), *arguments], cwd=project, check=True)

    print("Checking/installing dependencies…", flush=True)
    run("-m", "pip", "install", "--disable-pip-version-check", "-r", "requirements.txt")
    run("manage.py", "migrate", "--noinput")
    print(f"Dashboard: http://127.0.0.1:{args.port}/", flush=True)
    print(f"Admin: http://127.0.0.1:{args.port}/admin/ (demo login: admin / admin)", flush=True)
    run("manage.py", "runserver", f"127.0.0.1:{args.port}", "--noreload")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except (subprocess.CalledProcessError, OSError) as error:
        print(f"Startup failed: {error}", file=sys.stderr)
        sys.exit(1)
