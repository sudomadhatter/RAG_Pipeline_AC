import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load GCP credentials and environment configuration
env_path = Path(__file__).parent.parent / "auth_keys" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from pipeline.curriculum import CurriculumPipeline
from pipeline.library import LibraryPipeline
import config

def print_status():
    """Prints the current counts of new/active/superseded files."""
    print("\n--- Pipeline Status ---")
    
    def count_files(directory):
        if not directory.exists():
            return 0
        return sum(1 for _ in directory.rglob('*') if _.is_file())

    print("DB1: Curriculum")
    print(f"  New:        {count_files(config.CURRICULUM_NEW)}")
    print(f"  Active:     {count_files(config.CURRICULUM_ACTIVE)}")
    print(f"  Superseded: {count_files(config.CURRICULUM_SUPERSEDED)}")
    
    print("\nDB2: Library")
    print(f"  New:        {count_files(config.LIBRARY_NEW)}")
    print(f"  Active:     {count_files(config.LIBRARY_ACTIVE)}")
    print(f"  Superseded: {count_files(config.LIBRARY_SUPERSEDED)}")
    print("-----------------------\n")

def main():
    parser = argparse.ArgumentParser(description="AviationChat Ingestion Pipeline CLI")
    
    parser.add_argument(
        "target", 
        choices=["curriculum", "library", "all", "validate", "status"],
        help="Target pipeline to run"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Simulate the pipeline run without making GCP calls or moving files"
    )

    args = parser.parse_args()

    # Pre-flight check: ensure we are in the right working directory or config is valid
    if not config.CURRICULUM_ROOT.exists() and not config.LIBRARY_ROOT.exists():
        print("Initializing directory structures according to architecture...")
        config.CURRICULUM_NEW.mkdir(parents=True, exist_ok=True)
        config.CURRICULUM_ACTIVE.mkdir(parents=True, exist_ok=True)
        config.CURRICULUM_SUPERSEDED.mkdir(parents=True, exist_ok=True)
        config.LIBRARY_NEW.mkdir(parents=True, exist_ok=True)
        config.LIBRARY_ACTIVE.mkdir(parents=True, exist_ok=True)
        config.LIBRARY_SUPERSEDED.mkdir(parents=True, exist_ok=True)
        print("Directory structures created. Drop your files into `pipeline/curriculum/new/` or `pipeline/library/new/`.")

    if args.target == "status":
        print_status()
        sys.exit(0)

    pipelines = []
    
    if args.target in ["curriculum", "all", "validate"]:
        pipelines.append(CurriculumPipeline())
        
    if args.target in ["library", "all", "validate"]:
        pipelines.append(LibraryPipeline())
        
    is_dry = args.dry_run or args.target == "validate"
    
    for pipe in pipelines:
        pipe.execute(is_dry_run=is_dry)

if __name__ == "__main__":
    main()
