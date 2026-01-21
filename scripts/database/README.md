# RCDB Database Updater

Automated system for updating your CoasterRanker database from RCDB.

## 📁 Folder Structure

```
scripts/database/
├── src/              # Python scripts - RUN FROM HERE
│   ├── rcdb_scraper.py          # Scrapes RCDB website
│   ├── database_merger_simple.py # Merges data into database
│   ├── update_coasters_simple.py # Main update script
│   ├── full_update.py            # One-click full database update
│   ├── run_batches.py            # Automated batch runner
│   ├── test_merger.py            # Safe testing (uses copies)
│   ├── test_single_coaster.py    # Test individual coasters
│   └── test_batch.py             # Test batch of 10 coasters
│
├── docs/             # Documentation - READ THESE
│   ├── USAGE.md                  # Complete step-by-step guide
│   ├── COMMANDS.md               # PowerShell command reference
│   └── README_IMPLEMENTATION.md  # System overview
│
└── requirements.txt  # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
cd "C:\Users\Wouter Termaat\OneDrive - Topicus\Documenten\Privé\CoasterRanker\scripts\database"
pip install -r requirements.txt
```

### 2. Go to Scripts Folder
```powershell
cd src
```

### 3. Test First (SAFE - uses database copies)
```powershell
python test_merger.py
```

### 4. Run Your First Real Batch
```powershell
python update_coasters_simple.py --start 1 --end 200
```

### 5. Or Run Full Database Update
```powershell
python full_update.py
```

## 📖 Documentation

- **[USAGE.md](docs/USAGE.md)** - Complete guide with all steps
- **[COMMANDS.md](docs/COMMANDS.md)** - Copy-paste PowerShell commands
- **[README_IMPLEMENTATION.md](docs/README_IMPLEMENTATION.md)** - System overview

## ⚡ Most Used Commands

**Test safely:**
```powershell
cd "C:\Users\Wouter Termaat\OneDrive - Topicus\Documenten\Privé\CoasterRanker\scripts\database\src"
python test_merger.py
```

**Update 200 coasters (~10 minutes):**
```powershell
cd "C:\Users\Wouter Termaat\OneDrive - Topicus\Documenten\Privé\CoasterRanker\scripts\database\src"
python update_coasters_simple.py --start 1 --end 200
```

**Full database update (~10-15 hours):**
```powershell
cd "C:\Users\Wouter Termaat\OneDrive - Topicus\Documenten\Privé\CoasterRanker\scripts\database\src"
python full_update.py
```

**Resume after interruption:**
```powershell
cd "C:\Users\Wouter Termaat\OneDrive - Topicus\Documenten\Privé\CoasterRanker\scripts\database\src"
python update_coasters_simple.py --start 1 --end 5000 --resume
```

## ✅ What It Does

1. **Downloads** coaster data from RCDB website
2. **Updates** your existing coasters with fresh data
3. **Adds** new coasters you don't have yet
4. **Preserves** your manually split coasters (Joris, Winjas, etc.)
5. **Creates** automatic backups before saving

## ⏱️ Time Estimates

- 200 coasters: ~10-15 minutes
- 500 coasters: ~30-45 minutes
- 1,000 coasters: ~1-1.5 hours
- Full database (15,000): ~10-15 hours

## ⚠️ Important Notes

- ✅ **Always test first** - Run `test_merger.py` before your first real update
- ✅ **Automatic backups** - Created before each save
- ✅ **Can resume** - Press Ctrl+C to stop, run again with `--resume` to continue
- ✅ **Preserves your splits** - Your 246 manually split coasters stay intact
- ⚠️ **Not background** - PowerShell window must stay open (minimize is OK)
- ⚠️ **Disable sleep** - For overnight runs, prevent computer from sleeping

## 🆘 Need Help?

See [docs/USAGE.md](docs/USAGE.md) for complete documentation with:
- Step-by-step guide
- Troubleshooting
- Error handling
- Best practices

---

**All scripts are in `src/` folder. All documentation is in `docs/` folder.**

Run from `src/` folder:
```powershell
cd "C:\Users\Wouter Termaat\OneDrive - Topicus\Documenten\Privé\CoasterRanker\scripts\database\src"
```
