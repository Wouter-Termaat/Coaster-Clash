"""
Update only SBNO coasters from RCDB
"""

import json
import time
from rcdb_scraper import RCDBScraper
from database_merger_simple import DatabaseMerger

# Load current SBNO coasters
with open('../../database/data/coasters_master.json', 'r', encoding='utf-8') as f:
    coasters_dict = json.load(f)

coasters = list(coasters_dict.values())
sbno_coasters = [c for c in coasters if c.get('status') == 'SBNO']
sbno_rcdb_ids = sorted([int(c['rcdbId']) for c in sbno_coasters if c.get('rcdbId')])

print(f"Found {len(sbno_rcdb_ids)} SBNO coasters to re-scrape")

# Initialize scraper and merger
scraper = RCDBScraper()
merger = DatabaseMerger(
    database_path='../../database/data/coasters_master.json',
    mapping_path='../../database/data/rcdb_to_custom_mapping.json'
)

# Re-scrape each SBNO coaster
successful = 0
failed = 0
status_changes = []
all_scraped_coasters = []

for i, rcdb_id in enumerate(sbno_rcdb_ids, 1):
    print(f"[{i}/{len(sbno_rcdb_ids)}] RCDB {rcdb_id}: ", end='', flush=True)
    
    try:
        # Scrape the coaster
        coaster_data = scraper.fetch_coaster(rcdb_id)
        
        if coaster_data and not isinstance(coaster_data, list) and not coaster_data.get('filtered'):
            # Single coaster
            old_status = None
            custom_id = merger.mapping.get(str(rcdb_id))
            if custom_id and custom_id in merger.database:
                old_status = merger.database[custom_id].get('status')
            
            new_status = coaster_data.get('status', 'Operating')
            print(f"✓ {coaster_data.get('name', 'unknown')} - Status: {old_status} → {new_status}")
            
            if old_status != new_status:
                status_changes.append({
                    'rcdb_id': rcdb_id,
                    'name': coaster_data.get('name'),
                    'old': old_status,
                    'new': new_status
                })
            
            all_scraped_coasters.append(coaster_data)
            successful += 1
        elif isinstance(coaster_data, list):
            # Split coaster
            print(f"✓ Split coaster ({len(coaster_data)} tracks)")
            all_scraped_coasters.extend(coaster_data)
            successful += 1
        else:
            print("✗ Not found or filtered")
            failed += 1
        
        # Delay between requests
        time.sleep(1.5)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        failed += 1

# Merge all scraped coasters into database
print("\nMerging all scraped coasters into database...")
merge_result = merger.merge_coasters(all_scraped_coasters)

# Save final database
print("\nSaving database...")
merger.save()

print("\n" + "="*70)
print("UPDATE COMPLETE!")
print("="*70)
print(f"Successful: {successful}")
print(f"Failed: {failed}")
print(f"Status changes: {len(status_changes)}")

if status_changes:
    print("\nCoasters with status changes:")
    for change in status_changes:
        print(f"  - RCDB {change['rcdb_id']}: {change['name']}")
        print(f"    {change['old']} → {change['new']}")
