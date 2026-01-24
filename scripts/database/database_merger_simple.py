"""
Simple Database Merger
Merges scraped RCDB data with existing database using rcdb_to_custom_mapping.json
Preserves your existing split coasters and custom IDs
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Union
from datetime import datetime


class DatabaseMerger:
    """Merges scraped data into existing database"""
    
    def __init__(self, database_path: str, mapping_path: str):
        self.database_path = Path(database_path)
        self.mapping_path = Path(mapping_path)
        self.database: Dict[str, Dict] = {}  # custom_id -> coaster data
        self.mapping: Dict[str, str] = {}  # rcdb_id -> custom_id
        
        self._load_files()
    
    def _load_files(self):
        """Load database and mapping files"""
        # Load database
        if self.database_path.exists():
            with open(self.database_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
            print(f"✓ Loaded {len(self.database)} coasters from database")
        
        # Load mapping
        if self.mapping_path.exists():
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                self.mapping = json.load(f)
            print(f"✓ Loaded {len(self.mapping)} mappings")
    
    def _is_alpine_coaster(self, coaster: Dict) -> bool:
        """Check if coaster is an Alpine/Mountain coaster (to be filtered out)"""
        model = coaster.get('model', '')
        manufacturer = coaster.get('manufacturer', '')
        
        return (
            model == 'Alpine Coaster' or
            model == 'Mountain Coaster' or
            manufacturer == 'Yamasakutalab'
        )
    
    def _is_alpine_coaster(self, coaster: Dict) -> bool:
        """Check if coaster is an Alpine/Mountain coaster (to be filtered out)"""
        model = coaster.get('model', '')
        manufacturer = coaster.get('manufacturer', '')
        
        return (
            model == 'Alpine Coaster' or
            model == 'Mountain Coaster' or
            manufacturer == 'Yamasakutalab'
        )
    
    def merge_coasters(self, scraped_coasters: List[Dict]) -> Dict:
        """
        Merge list of scraped coasters into database
        
        Args:
            scraped_coasters: List of coaster dicts from scraper
            
        Returns:
            Stats about merge operation
        """
        updated_count = 0
        added_count = 0
        preserved_splits = 0
        updated_ids = []
        added_ids = []
        skipped_count = 0
        filtered_alpine = 0
        
        # Group scraped coasters by RCDB ID to detect splits
        rcdb_groups = {}
        for coaster in scraped_coasters:
            # Filter out alpine/mountain coasters
            if self._is_alpine_coaster(coaster):
                filtered_alpine += 1
                continue
            
            rcdb_id = str(coaster.get('rcdbId'))
            if rcdb_id:
                if rcdb_id not in rcdb_groups:
                    rcdb_groups[rcdb_id] = []
                rcdb_groups[rcdb_id].append(coaster)
        
        # Process each RCDB ID group
        for rcdb_id, coasters_in_group in rcdb_groups.items():
            is_split = len(coasters_in_group) > 1
            
            if is_split:
                # Split coaster - match by track name
                result = self._merge_split_coaster(rcdb_id, coasters_in_group)
                updated_count += result['updated']
                added_count += result['added']
                skipped_count += result['skipped']
                updated_ids.extend(result['updated_ids'])
                added_ids.extend(result['added_ids'])
                if result['updated'] > 0:
                    preserved_splits += 1
            else:
                # Single coaster - use simple mapping
                coaster = coasters_in_group[0]
                
                # Check if we have a custom ID for this RCDB ID
                if rcdb_id in self.mapping:
                    custom_id = self.mapping[rcdb_id]
                    
                    # Check if multiple tracks exist with this rcdbId (manual split or scraper missed split)
                    existing_with_same_rcdb = [
                        cid for cid, c in self.database.items() 
                        if str(c.get('rcdbId')) == rcdb_id
                    ]
                    
                    if len(existing_with_same_rcdb) > 1:
                        # Multiple tracks exist but scraped as single
                        # This happens when scraper doesn't detect split or coaster was manually split
                        print(f"⚠️  RCDB {rcdb_id} has {len(existing_with_same_rcdb)} tracks but scraped as single")
                        print(f"   Updating all tracks: {existing_with_same_rcdb}")
                        
                        # Update ALL tracks with this rcdbId
                        for track_id in existing_with_same_rcdb:
                            existing_name = self.database[track_id].get('name')
                            self._update_coaster(track_id, coaster)
                            
                            # Preserve original track name (Left/Right suffix)
                            if existing_name:
                                self.database[track_id]['name'] = existing_name
                            
                            # Add/update split protection fields
                            track_name = self._extract_track_name(existing_name)
                            siblings = [tid for tid in existing_with_same_rcdb if tid != track_id]
                            
                            self.database[track_id]['isSplitTrack'] = True
                            self.database[track_id]['splitGroup'] = rcdb_id
                            self.database[track_id]['trackName'] = track_name
                            self.database[track_id]['splitSiblings'] = siblings
                            
                            updated_count += 1
                            updated_ids.append(track_id)
                        
                        preserved_splits += 1
                    elif custom_id in self.database:
                        # Normal single coaster update
                        self._update_coaster(custom_id, coaster)
                        updated_count += 1
                        updated_ids.append(custom_id)
                    else:
                        # Mapping exists but coaster not in database (orphaned mapping)
                        print(f"⚠️  Warning: Mapping exists for RCDB {rcdb_id} → {custom_id} but coaster not in database")
                        skipped_count += 1
                else:
                    # New coaster - need to assign custom ID
                    custom_id = self._assign_new_id(coaster)
                    self.database[custom_id] = coaster
                    self.database[custom_id]['id'] = custom_id
                    self.mapping[rcdb_id] = custom_id
                    added_count += 1
                    added_ids.append(custom_id)
        
        return {
            "updated": updated_count,
            "added": added_count,
            "preserved_splits": preserved_splits,
            "skipped": skipped_count,
            "filtered_alpine": filtered_alpine,
            "total_coasters": len(self.database),
            "updated_ids": updated_ids,
            "added_ids": added_ids
        }
    
    def _merge_split_coaster(self, rcdb_id: str, scraped_tracks: List[Dict]) -> Dict:
        """
        Merge split coaster (dueling/racing) by matching track names
        Adds protection fields: isSplitTrack, splitGroup, trackName, splitSiblings
        
        Args:
            rcdb_id: RCDB ID (same for all tracks)
            scraped_tracks: List of track data from scraper
            
        Returns:
            Stats about this split coaster merge
        """
        updated_ids = []
        added_ids = []
        skipped = 0
        
        # Find all existing coasters with this RCDB ID in database
        existing_with_rcdb = {
            custom_id: coaster 
            for custom_id, coaster in self.database.items() 
            if str(coaster.get('rcdbId')) == rcdb_id
        }
        
        # Try to match scraped tracks to existing tracks by name
        matched_pairs = []  # (custom_id, scraped_track)
        
        for scraped_track in scraped_tracks:
            scraped_name = scraped_track.get('name', '')
            matched_id = None
            
            # Try exact name match first
            for custom_id, existing in existing_with_rcdb.items():
                if existing.get('name') == scraped_name:
                    matched_id = custom_id
                    break
            
            # If no exact match, try partial match (for name variations)
            if not matched_id:
                for custom_id, existing in existing_with_rcdb.items():
                    existing_name = existing.get('name', '')
                    # Check if track name is in existing name or vice versa
                    if scraped_name and existing_name and (
                        scraped_name in existing_name or existing_name in scraped_name
                    ):
                        matched_id = custom_id
                        break
            
            if matched_id:
                matched_pairs.append((matched_id, scraped_track))
            else:
                # New track - will add it
                matched_pairs.append((None, scraped_track))
        
        # Collect all custom IDs for this split group (for splitSiblings)
        all_track_ids = []
        for matched_id, scraped_track in matched_pairs:
            if matched_id:
                all_track_ids.append(matched_id)
            else:
                # Will create new ID
                new_id = self._assign_new_id(scraped_track)
                all_track_ids.append(new_id)
        
        # Now update/add each track with split protection fields
        for i, (matched_id, scraped_track) in enumerate(matched_pairs):
            # Extract track name from full coaster name
            track_name = self._extract_track_name(scraped_track.get('name', ''))
            
            # Calculate siblings (all other tracks)
            siblings = [tid for tid in all_track_ids if tid != (matched_id or all_track_ids[i])]
            
            # Add split protection fields to scraped data
            scraped_track['isSplitTrack'] = True
            scraped_track['splitGroup'] = rcdb_id
            scraped_track['trackName'] = track_name
            scraped_track['splitSiblings'] = siblings
            
            if matched_id:
                # Update existing track
                self._update_coaster(matched_id, scraped_track, preserve_split=True)
                updated_ids.append(matched_id)
            else:
                # Add new track
                custom_id = all_track_ids[i]
                self.database[custom_id] = scraped_track
                self.database[custom_id]['id'] = custom_id
                added_ids.append(custom_id)
            
            # Ensure mapping exists (map to first track's ID by convention)
            if rcdb_id not in self.mapping:
                self.mapping[rcdb_id] = all_track_ids[0]
        
        return {
            "updated": len(updated_ids),
            "added": len(added_ids),
            "skipped": skipped,
            "updated_ids": updated_ids,
            "added_ids": added_ids
        }
    
    def _extract_track_name(self, full_name: str) -> str:
        """
        Extract track name from full coaster name
        E.g., 'Joris en de Draak - Water' -> 'Water'
        """
        # Common patterns: "Name - Track", "Name (Track)"
        if ' - ' in full_name:
            return full_name.split(' - ')[-1].strip()
        elif '(' in full_name and ')' in full_name:
            # Extract text in last parentheses
            parts = full_name.split('(')
            if len(parts) > 1:
                return parts[-1].replace(')', '').strip()
        # Fallback: return the last word
        words = full_name.split()
        return words[-1] if words else full_name
    
    def _update_coaster(self, custom_id: str, scraped_data: Dict, preserve_split: bool = False):
        """Update existing coaster with scraped data"""
        existing = self.database[custom_id]
        
        # Fields to update from RCDB
        update_fields = [
            'name', 'parkName', 'city', 'country', 'status', 'opened',
            'manufacturer', 'model', 'type', 'design',
            'height', 'drop', 'angle', 'verticalAngle', 'speed', 'length', 'inversions', 'elements', 'duration'
        ]
        
        for field in update_fields:
            if field in scraped_data and scraped_data[field]:
                existing[field] = scraped_data[field]
        
        # Always update rcdbId
        if 'rcdbId' in scraped_data:
            existing['rcdbId'] = scraped_data['rcdbId']
        
        # Add/preserve split protection fields if this is a split coaster
        if preserve_split or scraped_data.get('isSplitTrack'):
            existing['isSplitTrack'] = scraped_data.get('isSplitTrack', True)
            existing['splitGroup'] = scraped_data.get('splitGroup', existing.get('splitGroup'))
            existing['trackName'] = scraped_data.get('trackName', existing.get('trackName'))
            existing['splitSiblings'] = scraped_data.get('splitSiblings', existing.get('splitSiblings', []))
    
    def _is_split_coaster(self, rcdb_id: str) -> bool:
        """Check if this RCDB ID has other tracks (manual splits)"""
        # Count how many custom IDs map to this RCDB ID
        count = sum(1 for rid in self.mapping.values() if self.mapping.get(rid) == rcdb_id)
        return count > 1
    
    def _assign_new_id(self, coaster: Dict) -> str:
        """Assign new custom ID for coaster"""
        # Try to extract country and park from coaster data
        # This is a simplified version - in production you'd have proper mapping
        
        # For now, use a simple sequential ID
        # Find highest ID number
        max_id = 0
        for custom_id in self.database.keys():
            if custom_id.startswith('C') and len(custom_id) >= 10:
                try:
                    # Extract numeric parts
                    num = int(custom_id[7:])
                    if num > max_id:
                        max_id = num
                except ValueError:
                    pass
        
        # Generate new ID (this is simplified - real version would use proper country/park codes)
        new_id = f"C999{max_id + 1:06d}"
        return new_id
    
    def save(self, backup: bool = True):
        """
        Save database and mapping to files
        
        Args:
            backup: If True, create backup before saving
        """
        if backup:
            self._create_backup()
        
        # Save database
        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved database: {self.database_path}")
        
        # Save mapping
        with open(self.mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, indent=2)
        print(f"✓ Saved mapping: {self.mapping_path}")
    
    def _create_backup(self):
        """Create timestamped backup of database files in backup folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup folder if it doesn't exist
        backup_dir = self.database_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup database
        if self.database_path.exists():
            backup_path = backup_dir / f"coasters_master.json.backup_{timestamp}"
            shutil.copy(self.database_path, backup_path)
            print(f"✓ Created backup: {backup_path}")
        
        # Backup mapping
        if self.mapping_path.exists():
            backup_path = backup_dir / f"rcdb_to_custom_mapping.json.backup_{timestamp}"
            shutil.copy(self.mapping_path, backup_path)
            print(f"✓ Created backup: {backup_path}")


if __name__ == "__main__":
    print("Database Merger - Use test_merger.py for testing")
