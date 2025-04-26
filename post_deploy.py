import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and log its output."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False

def main():
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_ecommerce.settings')
    
    # Clear staticfiles directory
    static_dir = os.path.join(os.getcwd(), 'staticfiles')
    if os.path.exists(static_dir):
        logger.info("Clearing staticfiles directory...")
        run_command(f"rm -rf {static_dir}/*")
    
    # Run collectstatic with verbose output
    logger.info("Running collectstatic...")
    if not run_command("python manage.py collectstatic --noinput --verbosity 2"):
        logger.error("collectstatic failed")
        sys.exit(1)
    
    logger.info("Deployment completed successfully")

if __name__ == "__main__":
    main()
