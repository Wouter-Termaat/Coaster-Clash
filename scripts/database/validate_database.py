"""
Comprehensive validation script for the cleaned coasters database.
"""

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

# Define the path to the database
DATABASE_PATH = Path(__file__).parent.parent.parent.parent / "database" / "data" / "coasters_master.json"

def load_database():
    """Load the coasters database."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_empty_types(data):
    """Check for entries with empty 'type' field."""
    issues = []
    for rcdb_id, coaster in data.items():
        if not coaster.get('type') or coaster.get('type', '').strip() == '':
            issues.append({
                'rcdb_id': rcdb_id,
                'name': coaster.get('name', 'N/A'),
                'park': coaster.get('park', 'N/A'),
                'issue': 'Empty type field'
            })
    return issues

def check_alpine_coasters(data):
    """Check for Alpine/Mountain coasters by name and model."""
    alpine_keywords = ['alpine coaster', 'mountain coaster', 'alpine', 'mountain']
    issues = []
    
    for rcdb_id, coaster in data.items():
        name = coaster.get('name', '').lower()
        model = coaster.get('model', '').lower()
        
        for keyword in alpine_keywords:
            if keyword in name or keyword in model:
                issues.append({
                    'rcdb_id': rcdb_id,
                    'name': coaster.get('name', 'N/A'),
                    'model': coaster.get('model', 'N/A'),
                    'manufacturer': coaster.get('manufacturer', 'N/A'),
                    'park': coaster.get('park', 'N/A'),
                    'issue': f'Contains "{keyword}"'
                })
                break
    
    return issues

def check_suspicious_manufacturers(data):
    """Check for entries with specific manufacturers that might be alpine coasters."""
    suspicious_manufacturers = ['Yamasakutalab', 'Brandauer', 'Aquatic Development Group', 'Sunkid', 'Wiegand']
    issues = []
    
    for rcdb_id, coaster in data.items():
        manufacturer = coaster.get('manufacturer', '')
        if manufacturer in suspicious_manufacturers:
            issues.append({
                'rcdb_id': rcdb_id,
                'name': coaster.get('name', 'N/A'),
                'model': coaster.get('model', 'N/A'),
                'manufacturer': manufacturer,
                'park': coaster.get('park', 'N/A'),
                'type': coaster.get('type', 'N/A')
            })
    
    return issues

def check_suspicious_patterns(data):
    """Check for entries with suspicious patterns."""
    issues = []
    
    for rcdb_id, coaster in data.items():
        # Check for missing park name
        if not coaster.get('park') or coaster.get('park', '').strip() == '':
            issues.append({
                'rcdb_id': rcdb_id,
                'name': coaster.get('name', 'N/A'),
                'issue': 'No park name'
            })
        
        # Check for entries with all critical fields empty
        critical_fields = ['name', 'park', 'type']
        empty_count = sum(1 for field in critical_fields if not coaster.get(field) or coaster.get(field, '').strip() == '')
        
        if empty_count >= 2:
            issues.append({
                'rcdb_id': rcdb_id,
                'name': coaster.get('name', 'N/A'),
                'park': coaster.get('park', 'N/A'),
                'type': coaster.get('type', 'N/A'),
                'issue': f'{empty_count} critical fields empty'
            })
    
    return issues

def check_duplicate_ids(data):
    """Check for duplicate RCDB IDs."""
    # Since data is a dict with rcdb_id as keys, duplicates would overwrite
    # But let's verify by checking if any IDs are duplicated
    ids = list(data.keys())
    duplicates = [id for id, count in Counter(ids).items() if count > 1]
    return duplicates

def sample_random_entries(data, sample_size=25):
    """Sample random entries from the database."""
    all_ids = list(data.keys())
    sample_ids = random.sample(all_ids, min(sample_size, len(all_ids)))
    
    samples = []
    for rcdb_id in sample_ids:
        coaster = data[rcdb_id]
        samples.append({
            'rcdb_id': rcdb_id,
            'name': coaster.get('name', 'N/A'),
            'park': coaster.get('park', 'N/A'),
            'manufacturer': coaster.get('manufacturer', 'N/A'),
            'model': coaster.get('model', 'N/A'),
            'type': coaster.get('type', 'N/A'),
            'status': coaster.get('status', 'N/A')
        })
    
    return samples

def analyze_database_stats(data):
    """Analyze database statistics."""
    stats = {
        'total_entries': len(data),
        'steel_count': 0,
        'wood_count': 0,
        'types': Counter(),
        'manufacturers': Counter(),
        'statuses': Counter(),
        'countries': Counter(),
        'with_coordinates': 0,
        'with_speed': 0,
        'with_height': 0,
        'with_length': 0
    }
    
    for rcdb_id, coaster in data.items():
        # Type analysis
        coaster_type = coaster.get('type', 'Unknown')
        stats['types'][coaster_type] += 1
        
        if 'steel' in coaster_type.lower():
            stats['steel_count'] += 1
        elif 'wood' in coaster_type.lower():
            stats['wood_count'] += 1
        
        # Manufacturer analysis
        manufacturer = coaster.get('manufacturer', 'Unknown')
        stats['manufacturers'][manufacturer] += 1
        
        # Status analysis
        status = coaster.get('status', 'Unknown')
        # Handle status as dict or string
        if isinstance(status, dict):
            status = status.get('state', 'Unknown')
        stats['statuses'][status] += 1
        
        # Country analysis
        country = coaster.get('country', 'Unknown')
        stats['countries'][country] += 1
        
        # Data completeness
        if coaster.get('coordinates'):
            stats['with_coordinates'] += 1
        if coaster.get('speed'):
            stats['with_speed'] += 1
        if coaster.get('height'):
            stats['with_height'] += 1
        if coaster.get('length'):
            stats['with_length'] += 1
    
    return stats

def print_report(data, issues_by_category, duplicates, samples, stats):
    """Print comprehensive validation report."""
    print("=" * 80)
    print("COMPREHENSIVE DATABASE VALIDATION REPORT")
    print("=" * 80)
    print()
    
    # Overall Summary
    print("OVERALL SUMMARY")
    print("-" * 80)
    print(f"Total Entries: {stats['total_entries']}")
    print()
    
    # Issues Summary
    total_issues = sum(len(issues) for issues in issues_by_category.values()) + len(duplicates)
    print(f"Total Issues Found: {total_issues}")
    print()
    
    # Detailed Issues
    if total_issues > 0:
        print("DETAILED ISSUES")
        print("-" * 80)
        
        for category, issues in issues_by_category.items():
            if issues:
                print(f"\n{category}: {len(issues)} issue(s)")
                for i, issue in enumerate(issues[:10], 1):  # Show first 10
                    print(f"  {i}. RCDB #{issue.get('rcdb_id', 'N/A')}")
                    print(f"     Name: {issue.get('name', 'N/A')}")
                    if 'model' in issue:
                        print(f"     Model: {issue.get('model', 'N/A')}")
                    if 'manufacturer' in issue:
                        print(f"     Manufacturer: {issue.get('manufacturer', 'N/A')}")
                    if 'park' in issue:
                        print(f"     Park: {issue.get('park', 'N/A')}")
                    if 'type' in issue:
                        print(f"     Type: {issue.get('type', 'N/A')}")
                    print(f"     Issue: {issue.get('issue', 'N/A')}")
                    print()
                
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more")
                    print()
        
        if duplicates:
            print(f"\nDuplicate RCDB IDs: {len(duplicates)}")
            for dup_id in duplicates:
                print(f"  - {dup_id}")
            print()
    else:
        print("✓ NO ISSUES FOUND - Database is clean!")
        print()
    
    # Database Statistics
    print("DATABASE STATISTICS")
    print("-" * 80)
    print()
    
    print("Coaster Types:")
    print(f"  Steel Coasters: {stats['steel_count']} ({stats['steel_count']/stats['total_entries']*100:.1f}%)")
    print(f"  Wood Coasters: {stats['wood_count']} ({stats['wood_count']/stats['total_entries']*100:.1f}%)")
    print()
    
    print("Top 10 Types:")
    for coaster_type, count in stats['types'].most_common(10):
        print(f"  {coaster_type}: {count} ({count/stats['total_entries']*100:.1f}%)")
    print()
    
    print("Top 15 Manufacturers:")
    for manufacturer, count in stats['manufacturers'].most_common(15):
        print(f"  {manufacturer}: {count} ({count/stats['total_entries']*100:.1f}%)")
    print()
    
    print("Status Distribution:")
    for status, count in stats['statuses'].most_common():
        print(f"  {status}: {count} ({count/stats['total_entries']*100:.1f}%)")
    print()
    
    print("Top 10 Countries:")
    for country, count in stats['countries'].most_common(10):
        print(f"  {country}: {count} ({count/stats['total_entries']*100:.1f}%)")
    print()
    
    print("Data Completeness:")
    print(f"  Entries with coordinates: {stats['with_coordinates']} ({stats['with_coordinates']/stats['total_entries']*100:.1f}%)")
    print(f"  Entries with speed data: {stats['with_speed']} ({stats['with_speed']/stats['total_entries']*100:.1f}%)")
    print(f"  Entries with height data: {stats['with_height']} ({stats['with_height']/stats['total_entries']*100:.1f}%)")
    print(f"  Entries with length data: {stats['with_length']} ({stats['with_length']/stats['total_entries']*100:.1f}%)")
    print()
    
    # Random Sample
    print("RANDOM SAMPLE (25 entries)")
    print("-" * 80)
    for i, sample in enumerate(samples, 1):
        print(f"{i}. RCDB #{sample['rcdb_id']}: {sample['name']}")
        print(f"   Park: {sample['park']}")
        print(f"   Type: {sample['type']}")
        print(f"   Manufacturer: {sample['manufacturer']}")
        print(f"   Model: {sample['model']}")
        print(f"   Status: {sample['status']}")
        print()
    
    # Final Verdict
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    if total_issues == 0:
        print("✓✓✓ DATABASE IS CLEAN AND READY FOR SCRAPING ✓✓✓")
        print()
        print(f"The database contains {stats['total_entries']} valid roller coaster entries.")
        print("All entries have been verified and no issues were found.")
        print("The database is ready for the RCDB scraping process.")
    else:
        print(f"⚠ ISSUES FOUND: {total_issues} entries need attention")
        print()
        print("Please review the detailed issues above before proceeding with scraping.")
    print("=" * 80)

def main():
    """Main validation function."""
    print("Loading database...")
    data = load_database()
    print(f"Loaded {len(data)} entries")
    print()
    
    print("Running validation checks...")
    
    # Run all checks
    issues_by_category = {
        'Empty Type Field': check_empty_types(data),
        'Alpine/Mountain Coasters': check_alpine_coasters(data),
        'Suspicious Manufacturers': check_suspicious_manufacturers(data),
        'Suspicious Patterns': check_suspicious_patterns(data)
    }
    
    duplicates = check_duplicate_ids(data)
    samples = sample_random_entries(data, 25)
    stats = analyze_database_stats(data)
    
    # Print comprehensive report
    print_report(data, issues_by_category, duplicates, samples, stats)

if __name__ == "__main__":
    main()
