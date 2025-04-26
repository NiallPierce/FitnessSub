import os
import subprocess
from pathlib import Path

def validate_html_files():
    # Find all HTML files in the templates directory
    html_files = list(Path('templates').rglob('*.html'))
    
    print(f"Found {len(html_files)} HTML files to validate")
    
    for html_file in html_files:
        print(f"\nValidating {html_file}...")
        try:
            # Run html5validator on the file
            result = subprocess.run(
                ['html5validator', str(html_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {html_file} is valid HTML5")
            else:
                print(f"❌ {html_file} has validation errors:")
                print(result.stderr)
                
        except FileNotFoundError:
            print("html5validator is not installed. Please install it using:")
            print("pip install html5validator")
            break

if __name__ == "__main__":
    validate_html_files() 