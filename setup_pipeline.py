import os
from pathlib import Path
import subprocess
import sys

def setup_pipeline():
    """Set up the complete pipeline for the pharmaceutical sales dashboard"""
    print("Setting up the pharmaceutical sales dashboard pipeline...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Create necessary directories if they don't exist
    directories = ['data', 'logs']
    for directory in directories:
        os.makedirs(project_root / directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Install requirements
    print("\nInstalling requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Set up the database
    print("\nSetting up the database...")
    from pharma_dashboard.data.db_setup import create_database
    create_database()
    
    # Import data
    print("\nImporting data...")
    from pharma_dashboard.data.import_data import import_data
    import_data(project_root / "data")
    
    print("\nSetup completed successfully!")
    print("\nTo run the dashboard, use the command:")
    print("streamlit run pharma_dashboard/dashboard.py")

if __name__ == "__main__":
    setup_pipeline() 