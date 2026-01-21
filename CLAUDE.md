# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Restaurant Lead Enrichment Tool - A Python CLI that processes restaurant business CSV/Excel files, resolves actual restaurant names (DBA) from LLC names, identifies owners, and matches against existing contact data.

## Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the tool
python main.py input.csv -o output.csv --batch-size 10

# Run with API keys inline (if not exported)
OPENROUTER_API_KEY="sk-or-..." GOOGLE_PLACES_API_KEY="..." python main.py input.csv -o output.csv

# Clear cache to force fresh API calls
rm -rf .cache
```

## Required Environment Variables

- `GOOGLE_PLACES_API_KEY` - Google Places Nearby Search API
- `OPENROUTER_API_KEY` - OpenRouter API key (accesses Perplexity sonar-pro model)
- `WHITEPAGES_API_KEY` - Whitepages Pro API key for owner personal info enrichment

## Architecture

Single-file CLI (`main.py`) with async parallel processing:

1. **Data Classes**: `Config`, `PersonInfo`, `RestaurantRecord` - core data structures
2. **CacheManager**: File-based MD5-hashed cache in `.cache/` to avoid duplicate API calls
3. **API Clients**:
   - `GooglePlacesClient` - Nearby Search for restaurant name resolution (uses lat/long)
   - `PerplexityClient` - Via OpenRouter for name resolution fallback and owner discovery
   - `WhitepagesClient` - Owner personal info enrichment (address, phone, email)
4. **Processing Pipeline** (`process_record`):
   - Extract DBA from LLC name if present (regex)
   - Try Google Places if coordinates exist
   - Fall back to Perplexity for name resolution
   - Find owner via Perplexity
   - Fuzzy match owner against CSV persons (rapidfuzz, 80% threshold)
   - Enrich owner info via Whitepages lookup (called for every owner found)
5. **Async batch processing** with semaphore-limited concurrency

## Input CSV Expected Columns

`fein, name, lat, long, address, city, state, zip, phone, county, expdate, website, email1, name1-10, phone1-10`

## Output CSV Columns

`FEIN, Name, OwnerName, Address, City, State, Zip, Phone, Email, County, Expdate, Website, LLC_Name, ContactSource`

One row per input record with single best owner match.

## Test Input File

**Primary test file**: `/Users/samruben/Downloads/InsuranceX_50+.csv`

Use this file for all testing going forward:
```bash
python main.py /Users/samruben/Downloads/InsuranceX_50+.csv -o output.csv --limit 10 -v
```

## Whitepages Configuration

Whitepages enrichment is now enabled in the pipeline and called for every owner discovered.

### How It Works

The input CSV contains **restaurant** address/phone, NOT the owner's personal info. The pipeline finds the owner's personal address, phone, and email via Whitepages for direct outreach.

### Whitepages API Details

- **Endpoint**: `https://api.whitepages.com/v1/person/`
- **Authentication**: X-Api-Key header (not query parameter)
- **Parameters**: `name` (required; city/state filtering applied locally)
- **Returns**: Personal address, phone, emails for the owner
- **Key lookup parameter**: Owner name + city + state (matched locally for accuracy)

### Complete Enrichment Pipeline

```
Step 1: Resolve Restaurant Name
  - Google Places (if lat/long) → Perplexity fallback

Step 2: Find Owner Name
  - Perplexity: "Who owns [restaurant] in [city], [state]?"

Step 3: Whitepages Lookup
  - Query: owner name
  - Results filtered by city + state match
  - Returns: owner's personal address, phone, email

Step 4: Output combined data
  - Restaurant info + owner personal contact details
```

## Web Application Architecture

The project includes a React frontend and FastAPI backend for web-based processing.

### Frontend (React + Vite)

Located in `frontend/` directory.

```bash
# Local development
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

**Key files:**
- `src/App.jsx` - Main application component
- `src/api.js` - API client functions
- `src/components/JobHistory.jsx` - Job list with download/delete buttons
- `src/components/JobStatus.jsx` - Progress display during processing

**Environment variables** (in Vercel):
- `VITE_API_URL` - Backend API URL (e.g., `https://bme-leadgen.onrender.com`)
- `VITE_APP_PASSWORD` - Password for frontend access

### Backend (FastAPI)

Main file: `api.py`

```bash
# Local development
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Key endpoints:**
- `POST /api/upload` - Upload CSV/Excel file
- `POST /api/jobs/{job_id}/start` - Start processing
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs/{job_id}/results` - Download results
- `GET /api/jobs` - List jobs for session
- `DELETE /api/jobs/{job_id}` - Delete a specific job
- `DELETE /api/jobs?session_id=X` - Delete all jobs for session
- `GET /api/health` - Health check (shows CORS config)

**Environment variables** (in Render):
- `CORS_ORIGINS` - Comma-separated allowed origins (e.g., `https://your-frontend.vercel.app,http://localhost:5173`)
- `REDIS_URL` - Redis connection URL for job persistence
- `GOOGLE_PLACES_API_KEY`, `OPENROUTER_API_KEY`, `WHITEPAGES_API_KEY` - API keys

### Deployment

**Render (Backend):**
- Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- NOT `streamlit run ...` (that's the old Streamlit app)

**Vercel (Frontend):**
- Auto-deploys from `frontend/` directory
- Set environment variables in Vercel dashboard

### Job Storage

Jobs are stored in Redis with 7-day TTL:
- `job:{uuid}:meta` - Job metadata (status, filename, progress)
- `job:{uuid}:results` - GZIP-compressed results
- `job:{uuid}:progress` - Current progress
- `user:{session_id}:jobs` - List of job IDs per user

Falls back to in-memory storage if Redis unavailable (local dev).

## Recent Fixes (January 2026)

### CORS Configuration
- Added whitespace stripping for `CORS_ORIGINS` env var
- Changed to `allow_methods=["*"]` and `allow_headers=["*"]` for broader compatibility
- Health endpoint now shows configured CORS origins for debugging

### Empty Row Filtering
- CSV files with empty rows (common in Excel exports) are now filtered
- Rows where `name` column is empty/null are skipped
- Prevents processing thousands of empty rows

### Delete Job Feature
- Added `DELETE /api/jobs/{job_id}` endpoint
- Added `DELETE /api/jobs?session_id=X` to delete all jobs
- Frontend has trash icon button on each job in history
- Confirmation dialog before deletion
