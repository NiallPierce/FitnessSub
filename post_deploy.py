import os
import subprocess
from pathlib import Path

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Command '{command}' succeeded:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    # Set the working directory to the project root
    os.chdir(Path(__file__).parent)
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_ecommerce.settings')
    
    # Create staticfiles directory if it doesn't exist
    staticfiles_dir = os.path.join(os.getcwd(), 'staticfiles')
    if not os.path.exists(staticfiles_dir):
        os.makedirs(staticfiles_dir)
    
    # Run migrations
    run_command("python manage.py migrate")
    
    # Setup the default site
    run_command("python manage.py setup_site")
    
    # Collect static files with verbose output
    if run_command("python manage.py collectstatic --noinput --clear"):
        print("Static files collected successfully!")
        
        # Verify static files were collected
        if os.path.exists(staticfiles_dir):
            print(f"Static files directory exists at: {staticfiles_dir}")
            print("Contents of staticfiles directory:")
            run_command(f"ls -la {staticfiles_dir}")
            
            # Check if CSS files were collected
            css_dir = os.path.join(staticfiles_dir, 'css')
            if os.path.exists(css_dir):
                print("\nCSS files found:")
                run_command(f"ls -la {css_dir}")
            else:
                print("\nWarning: CSS directory not found in staticfiles!")
        else:
            print("Warning: Static files directory was not created!")
    else:
        print("Failed to collect static files!")