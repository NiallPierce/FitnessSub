import os
import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Command '{command}' succeeded:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed:")
        print(e.stderr)
        raise

if __name__ == "__main__":
    # Run migrations
    run_command("python manage.py migrate")
    
    # Setup the default site
    run_command("python manage.py setup_site")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput")