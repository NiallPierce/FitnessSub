import os
import sys
import subprocess
import time
from pathlib import Path
from django.core.management import execute_from_command_line

def run_command(command, timeout=300):
    """Run a command with a timeout and return its output."""
    try:
        print(f"Running command: {command}")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait for the process to complete with timeout
        stdout, stderr = process.communicate(timeout=timeout)
        
        if process.returncode != 0:
            print(f"Error running command: {command}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds: {command}")
        process.kill()
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    # Set the working directory to the project root
    os.chdir(Path(__file__).parent)
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_ecommerce.settings')
    
    # Verify S3 configuration
    required_s3_vars = [
        'USE_AWS',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME'
    ]
    
    missing_vars = [var for var in required_s3_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"Warning: Missing required S3 configuration variables: {', '.join(missing_vars)}")
    
    # Debug information
    print("Current working directory:", os.getcwd())
    print("Environment variables:")
    for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME', 'USE_AWS']:
        print(f"{key}: {'Set' if key in os.environ else 'Not set'}")
    
    # Run migrations
    print("Running migrations...")
    if not run_command("python manage.py migrate --noinput"):
        print("Migrations failed")
        return 1
    
    # Create superuser if it doesn't exist
    print("Creating superuser if needed...")
    if not run_command("python manage.py create_superuser_if_not_exists"):
        print("Superuser creation failed")
        return 1
    
    # Collect static files with timeout and retry
    print("Collecting static files...")
    
    # First, clear the staticfiles directory
    if os.path.exists('staticfiles'):
        print("Clearing staticfiles directory...")
        run_command("rm -rf staticfiles/*")
    
    # Temporarily disable S3 during collectstatic
    os.environ['DISABLE_S3_DURING_COLLECTSTATIC'] = '1'
    
    # Run collectstatic with verbose output
    if not run_command("python manage.py collectstatic --noinput --clear -v 2", timeout=600):
        print("Failed to collect static files")
        return 1
    
    # Re-enable S3 after collectstatic
    del os.environ['DISABLE_S3_DURING_COLLECTSTATIC']
    
    print("Post-deploy script completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())