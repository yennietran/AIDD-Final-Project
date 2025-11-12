"""Run the seed script"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the seed function
from database.seed_sample_data import seed_data

if __name__ == "__main__":
    seed_data()

