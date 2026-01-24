"""
Full Database Update
Updates ALL coasters from RCDB in one run
This will take 10-15 hours to complete
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def full_update():
    """
    Run a complete update of the entire RCDB database
    
    This will scrape RCDB IDs 1 through 20000 (covers all existing coasters)
    Expected time: 10-15 hours
    """
    
    # Check if there's existing progress
    progress_file = Path(__file__).parent / 'update_progress.json'
    has_progress = progress_file.exists()
    
    print("=" * 70)
    print("FULL RCDB DATABASE UPDATE")
    print("=" * 70)
    print()
    
    # If progress exists, show resume options
    if has_progress:
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                completed = progress.get('completed_count', 0)
                last_id = progress.get('last_completed_id', 0)
            
            print("⚠️  EXISTING PROGRESS DETECTED")
            print()
            print(f"  Last completed: RCDB #{last_id}")
            print(f"  Total processed: {completed} coasters")
            print()
            print("Choose an option:")
            print("  [1] Resume from where you left off")
            print("  [2] Start fresh (delete progress and restart)")
            print("  [3] Cancel")
            print()
            
            while True:
                choice = input("Enter choice (1/2/3): ").strip()
                
                if choice == '1':
                    print()
                    print("Resuming from previous progress...")
                    resume_mode = True
                    break
                elif choice == '2':
                    print()
                    confirm = input("Are you sure you want to start fresh? (yes/no): ").strip().lower()
                    if confirm in ['yes', 'y']:
                        progress_file.unlink()
                        print("Progress deleted. Starting from beginning...")
                        resume_mode = False
                        break
                    else:
                        print("Cancelled restart. Choose again:")
                        continue
                elif choice == '3':
                    print("Cancelled.")
                    return
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
        
        except Exception as e:
            print(f"⚠️  Could not read progress file: {e}")
            print("Starting fresh...")
            resume_mode = False
    
    else:
        print("This will update ALL coasters from RCDB")
        print()
        print("Details:")
        print("  - RCDB ID range: 1 to 25,000")
        print("  - Delay: 2 seconds per coaster")
        print("  - Estimated time: 8-12 hours")
        print("  - Auto-resume: YES (if interrupted)")
        print("  - Auto-backup: YES (every 500 coasters)")
        print()
        print("The script will:")
        print("  ✓ Create automatic backups before saving")
        print("  ✓ Save progress every 500 coasters")
        print("  ✓ Allow you to resume if interrupted (Ctrl+C)")
        print("  ✓ Show live progress in this window")
        print()
        print("⚠️  IMPORTANT:")
        print("  - Keep this window open (minimize is OK)")
        print("  - Don't let your computer sleep")
        print("  - You can press Ctrl+C to stop anytime")
        print("  - Run again to resume from where you stopped")
        print()
        print("=" * 70)
        print()
        
        response = input("Ready to start full update? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return
        
        resume_mode = False
    
    print()
    print("Starting full update...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("=" * 70)
    print()
    
    # Run the update with resume enabled
    cmd = [
        sys.executable,  # Use same Python interpreter
        'update_coasters_simple.py',
        '--start', '1',
        '--end', '25000',
        '--delay', '2.0',
        '--save-interval', '500'
    ]
    
    # Add resume flag if continuing from progress
    if resume_mode:
        cmd.append('--resume')
    
    try:
        result = subprocess.run(cmd)
        
        print()
        print("=" * 70)
        if result.returncode == 0:
            print("FULL UPDATE COMPLETE!")
            print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("Update stopped or encountered errors")
            print("You can run this script again to resume")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 70)
        print("UPDATE INTERRUPTED")
        print("=" * 70)
        print()
        print("Progress has been saved!")
        print("Run this script again to resume from where you stopped:")
        print("  python full_update.py")
        print()
        print("=" * 70)


if __name__ == "__main__":
    full_update()
