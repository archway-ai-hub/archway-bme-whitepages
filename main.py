#!/usr/bin/env python3
"""
Restaurant Lead Enrichment Tool

Processes restaurant business CSV files, finds actual restaurant names (DBA) from LLC names,
identifies owners via Perplexity (through OpenRouter), and matches against existing contacts.
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import aiohttp
import pandas as pd
from openai import AsyncOpenAI
from rapidfuzz import fuzz
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm


# ============================================================================
# Configuration & Data Classes
# ============================================================================

@dataclass
class Config:
    """Application configuration from environment variables."""
    google_places_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_PLACES_API_KEY", ""))
    openrouter_api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    whitepages_api_key: str = field(default_factory=lambda: os.getenv("WHITEPAGES_API_KEY", ""))
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))

    def __post_init__(self):
        self.cache_dir.mkdir(exist_ok=True)

    def validate(self):
        """Validate required API keys are present."""
        missing = []
        if not self.google_places_api_key:
            missing.append("GOOGLE_PLACES_API_KEY")
        if not self.openrouter_api_key:
            missing.append("OPENROUTER_API_KEY")
        if not self.whitepages_api_key:
            missing.append("WHITEPAGES_API_KEY")

        if missing:
            print(f"Warning: Missing API keys: {', '.join(missing)}")
            print("Some features may not work without these keys.")


@dataclass
class PersonInfo:
    """Person contact information."""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    source: str = "csv"  # csv, whitepages, or perplexity
    # Owner's personal address from Whitepages (distinct from restaurant address)
    personal_address: Optional[str] = None  # Owner's home address (street)
    personal_city: Optional[str] = None
    personal_state: Optional[str] = None
    personal_zip: Optional[str] = None
    personal_phone: Optional[str] = None  # Owner's personal phone (may differ from CSV match)
    personal_email: Optional[str] = None  # Owner's personal email


@dataclass
class RestaurantRecord:
    """Processed restaurant record."""
    fein: str = ""
    llc_name: str = ""
    restaurant_name: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    phone: str = ""
    email: str = ""
    county: str = ""
    expdate: str = ""
    website: str = ""
    owners: list[PersonInfo] = field(default_factory=list)
    persons_from_csv: list[PersonInfo] = field(default_factory=list)


# ============================================================================
# Cache Manager
# ============================================================================

class CacheManager:
    """Simple file-based cache for API responses."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from arguments."""
        key_data = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, prefix: str, *args) -> Optional[dict]:
        """Get cached value if exists."""
        key = self._get_cache_key(prefix, *args)
        path = self._get_cache_path(key)
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def set(self, prefix: str, *args, value: dict):
        """Cache a value."""
        key = self._get_cache_key(prefix, *args)
        path = self._get_cache_path(key)
        with open(path, "w") as f:
            json.dump(value, f)


# ============================================================================
# API Clients
# ============================================================================

class GooglePlacesClient:
    """Google Places API client for restaurant name resolution."""

    def __init__(self, api_key: str, cache: CacheManager):
        self.api_key = api_key
        self.cache = cache
        self.base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def find_restaurant(
        self,
        session: aiohttp.ClientSession,
        lat: float,
        lng: float,
        radius: int = 50
    ) -> Optional[dict]:
        """Find restaurant at given coordinates."""
        if not self.api_key:
            return None

        # Check cache first
        cached = self.cache.get("google_places", lat, lng, radius)
        if cached:
            return cached

        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "restaurant",
            "key": self.api_key
        }

        async with session.get(self.base_url, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

            if data.get("status") == "OK" and data.get("results"):
                result = {
                    "name": data["results"][0].get("name"),
                    "place_id": data["results"][0].get("place_id"),
                    "address": data["results"][0].get("vicinity")
                }
                self.cache.set("google_places", lat, lng, radius, value=result)
                return result

        return None


def clean_perplexity_text(text: str) -> str:
    """Clean Perplexity response text by removing markdown and citations."""
    if not text:
        return ""
    # Remove markdown bold/italic
    text = re.sub(r'\*+', '', text)
    # Remove citation references like [1], [2][3], etc.
    text = re.sub(r'\[\d+\]', '', text)
    # Remove any remaining brackets with numbers
    text = re.sub(r'\s*\[[\d,\s]+\]\s*', '', text)
    # Clean up extra whitespace
    text = ' '.join(text.split())
    return text.strip()


class PerplexityClient:
    """Perplexity API client (via OpenRouter) for restaurant name resolution and owner discovery."""

    def __init__(self, api_key: str, cache: CacheManager):
        self.api_key = api_key
        self.cache = cache
        # Use OpenRouter to access Perplexity models
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        ) if api_key else None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def resolve_restaurant_name(
        self,
        llc_name: str,
        address: str,
        city: str,
        state: str,
        website: str = ""
    ) -> Optional[str]:
        """Resolve the actual restaurant name (DBA) from LLC name."""
        if not self.client:
            return None

        cache_key = f"{llc_name}:{address}:{city}:{state}"
        cached = self.cache.get("perplexity_name", cache_key)
        if cached:
            return cached.get("name")

        prompt = f"""What is the actual restaurant name (DBA) for this business?

LLC: {llc_name}
Address: {address}, {city}, {state}
Website: {website if website else 'Unknown'}

Reply with ONLY the restaurant name (1-5 words max). No explanations, no punctuation, no quotes. Example: "FIG" or "The Belmont". If unknown, reply "UNKNOWN"."""

        try:
            response = await self.client.chat.completions.create(
                model="perplexity/sonar-pro",  # OpenRouter model path
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            name = response.choices[0].message.content.strip()
            name = clean_perplexity_text(name)  # Remove markdown/citations
            if name and name.upper() != "UNKNOWN":
                self.cache.set("perplexity_name", cache_key, value={"name": name})
                return name
        except Exception as e:
            print(f"Perplexity error resolving name for {llc_name}: {e}")

        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def find_owners(
        self,
        restaurant_name: str,
        llc_name: str,
        address: str,
        city: str,
        state: str
    ) -> list[str]:
        """Find restaurant owners using web search."""
        if not self.client:
            return []

        cache_key = f"{restaurant_name}:{llc_name}:{city}:{state}"
        cached = self.cache.get("perplexity_owners", cache_key)
        if cached:
            return cached.get("owners", [])

        prompt = f"""Who is the primary owner of this restaurant?

Restaurant: {restaurant_name}
LLC: {llc_name}
Location: {address}, {city}, {state}

Reply with ONLY the owner's full name (first and last). One name only - the main owner/founder. No titles, no explanations. If unknown, reply "UNKNOWN"."""

        try:
            response = await self.client.chat.completions.create(
                model="perplexity/sonar-pro",  # OpenRouter model path
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()

            if content.upper() == "UNKNOWN":
                return []

            # Parse owner name from response - take first valid name only
            content = clean_perplexity_text(content)
            content = re.sub(r'^[\d\.\-\*\•]+\s*', '', content)  # Remove bullets/numbers

            # Take only the first line/name
            first_line = content.split("\n")[0].strip()
            first_line = re.sub(r'\s*[\(\[].*?[\)\]]', '', first_line)  # Remove parenthetical info

            owners = []
            if first_line and len(first_line) > 2 and len(first_line) < 50 and first_line.upper() != "UNKNOWN":
                owners.append(first_line)

            self.cache.set("perplexity_owners", cache_key, value={"owners": owners})
            return owners

        except Exception as e:
            print(f"Perplexity error finding owners for {restaurant_name}: {e}")

        return []


class WhitepagesClient:
    """Whitepages Pro API client for owner personal information lookup.

    Uses Whitepages Pro 2.2 Person API to find owner's personal contact information
    (home address, personal phone) distinct from restaurant contact info.

    API Documentation:
        Endpoint: https://proapi.whitepages.com/2.2/person.json
        Auth: api_key query parameter
        Params: api_key, name, city, state_code (2-letter state code)
        Response: {"results": [...]} with locations[], phones[] arrays
    """

    def __init__(self, api_key: str, cache: CacheManager):
        self.api_key = api_key
        self.cache = cache
        self.base_url = "https://proapi.whitepages.com/2.2/person.json"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def lookup_person(
        self,
        session: aiohttp.ClientSession,
        name: str,
        city: str,
        state: str
    ) -> Optional[dict]:
        """Look up a person's personal contact info by name and location.

        Args:
            session: aiohttp ClientSession for making requests
            name: Full name of the person to look up
            city: City where the person is located
            state: 2-letter state code (e.g., "SC", "CA")

        Returns:
            Dict with personal contact info, or None if not found:
            {
                "personal_address": str,  # Street address
                "personal_city": str,
                "personal_state": str,
                "personal_zip": str,
                "personal_phone": str
            }
        """
        if not self.api_key:
            print("[Whitepages] No API key configured - skipping lookup")
            return None

        if not name or not city or not state:
            print(f"[Whitepages] Missing required params: name={name}, city={city}, state={state}")
            return None

        # Check cache first - use normalized cache key
        cache_key = f"{name.lower().strip()}:{city.lower().strip()}:{state.upper().strip()}"
        cached = self.cache.get("whitepages_person", cache_key)
        if cached:
            print(f"[Whitepages] Cache hit for {name}")
            return cached

        # Authentication via query parameter (NOT header)
        params = {
            "api_key": self.api_key,
            "name": name,
            "city": city,
            "state_code": state.upper()[:2]  # API expects 2-letter state code
        }

        print(f"[Whitepages] Looking up: {name} in {city}, {state}")

        try:
            async with session.get(self.base_url, params=params) as resp:
                if resp.status == 429:
                    print(f"[Whitepages] Rate limit exceeded")
                    return None
                if resp.status == 401:
                    print(f"[Whitepages] Authentication failed - check API key")
                    return None
                if resp.status != 200:
                    text = await resp.text()
                    print(f"[Whitepages] API error {resp.status}: {text[:200]}")
                    return None

                data = await resp.json()
                print(f"[Whitepages] Response received, parsing results...")

                # Response structure: {"results": [...]}
                results = data.get("results", [])
                if not results:
                    print(f"[Whitepages] No results found for {name}")
                    return None

                # Take first/best match
                person = results[0]

                # Initialize result structure (no email - API doesn't return it)
                result = {
                    "personal_address": None,
                    "personal_city": None,
                    "personal_state": None,
                    "personal_zip": None,
                    "personal_phone": None
                }

                # Parse location (first one)
                locations = person.get("locations", [])
                if locations:
                    loc = locations[0]
                    result["personal_address"] = loc.get("standard_address_line1", "")
                    result["personal_city"] = loc.get("city", "")
                    result["personal_state"] = loc.get("state_code", "")
                    result["personal_zip"] = loc.get("postal_code", "")
                    print(f"[Whitepages] Found address: {result['personal_address']}, {result['personal_city']}, {result['personal_state']} {result['personal_zip']}")

                # Parse phone (first one)
                phones = person.get("phones", [])
                if phones:
                    result["personal_phone"] = phones[0].get("phone_number", "")
                    print(f"[Whitepages] Found phone: {result['personal_phone']}")

                # Cache the result
                self.cache.set("whitepages_person", cache_key, value=result)
                print(f"[Whitepages] Cached result for {name}")
                return result

        except aiohttp.ClientError as e:
            print(f"[Whitepages] Connection error for {name}: {e}")
            return None
        except Exception as e:
            print(f"[Whitepages] Error for {name}: {e}")
            return None


# ============================================================================
# Data Processing
# ============================================================================

def clean_str(val) -> str:
    """Clean a value to string, handling NaN and None."""
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    if s.lower() == "nan":
        return ""
    return s


def clean_fein(val) -> str:
    """Clean FEIN value, removing decimal places from float conversion."""
    if pd.isna(val) or val is None:
        return ""
    # If it's a float that represents an int, convert properly
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    s = str(val).strip()
    if s.lower() == "nan":
        return ""
    # Remove .0 suffix if present
    if s.endswith(".0"):
        s = s[:-2]
    return s


def parse_csv_row(row: pd.Series) -> RestaurantRecord:
    """Parse a CSV row into a RestaurantRecord."""
    record = RestaurantRecord(
        fein=clean_fein(row.get("fein")),
        llc_name=clean_str(row.get("name")),
        lat=float(row["lat"]) if pd.notna(row.get("lat")) and row.get("lat") != "" else None,
        lng=float(row["long"]) if pd.notna(row.get("long")) and row.get("long") != "" else None,
        address=clean_str(row.get("address")),
        city=clean_str(row.get("city")),
        state=clean_str(row.get("state")),
        zip_code=clean_str(row.get("zip")),
        phone=clean_str(row.get("phone")),
        email=clean_str(row.get("email1")),
        county=clean_str(row.get("county")),
        expdate=clean_str(row.get("expdate")),
        website=clean_str(row.get("website"))
    )

    # Parse persons from CSV (name1-10, phone1-10)
    for i in range(1, 11):
        name_col = f"name{i}"
        phone_col = f"phone{i}"

        name = clean_str(row.get(name_col))
        phone = clean_str(row.get(phone_col))

        if name:
            record.persons_from_csv.append(PersonInfo(name=name, phone=phone if phone else None, source="csv"))

    return record


def extract_dba_from_name(llc_name: str) -> Optional[str]:
    """Extract DBA from LLC name if present (e.g., 'BUMPER CROP LLC DBA FIG')."""
    dba_match = re.search(r'\bDBA\s+(.+)$', llc_name, re.IGNORECASE)
    if dba_match:
        return dba_match.group(1).strip()
    return None


def fuzzy_match_owner(
    owner_name: str,
    persons: list[PersonInfo],
    threshold: int = 80
) -> Optional[PersonInfo]:
    """Find a matching person using fuzzy string matching."""
    owner_name_normalized = owner_name.lower().strip()

    best_match = None
    best_score = 0

    for person in persons:
        person_name_normalized = person.name.lower().strip()

        # Try different matching strategies
        scores = [
            fuzz.ratio(owner_name_normalized, person_name_normalized),
            fuzz.partial_ratio(owner_name_normalized, person_name_normalized),
            fuzz.token_sort_ratio(owner_name_normalized, person_name_normalized)
        ]

        max_score = max(scores)
        if max_score > best_score and max_score >= threshold:
            best_score = max_score
            best_match = person

    return best_match


async def process_record(
    record: RestaurantRecord,
    session: aiohttp.ClientSession,
    google_client: GooglePlacesClient,
    perplexity_client: PerplexityClient,
    whitepages_client: WhitepagesClient,
    semaphore: asyncio.Semaphore
) -> RestaurantRecord:
    """Process a single restaurant record through the enrichment pipeline."""

    async with semaphore:
        # Step 1: Resolve restaurant name
        # First check if DBA is in the LLC name
        dba_name = extract_dba_from_name(record.llc_name)

        if dba_name:
            record.restaurant_name = dba_name
        elif record.lat and record.lng:
            # Try Google Places first
            place = await google_client.find_restaurant(session, record.lat, record.lng)
            if place and place.get("name"):
                record.restaurant_name = place["name"]

        # Fall back to Perplexity if still no name
        if not record.restaurant_name:
            resolved_name = await perplexity_client.resolve_restaurant_name(
                record.llc_name,
                record.address,
                record.city,
                record.state,
                record.website
            )
            if resolved_name:
                record.restaurant_name = resolved_name

        # Default to LLC name if nothing found
        if not record.restaurant_name:
            record.restaurant_name = record.llc_name

        # Step 2: Find owners via Perplexity
        owner_names = await perplexity_client.find_owners(
            record.restaurant_name,
            record.llc_name,
            record.address,
            record.city,
            record.state
        )

        # Step 3: Match owner against CSV persons - keep only ONE owner
        best_owner = None

        for owner_name in owner_names:
            matched_person = fuzzy_match_owner(owner_name, record.persons_from_csv)

            if matched_person and matched_person.phone:
                # We have contact info from CSV - this is the best match
                best_owner = PersonInfo(
                    name=owner_name,
                    phone=matched_person.phone,
                    email=record.email if record.email and matched_person.name.lower() in record.email.lower() else None,
                    source="csv"
                )
                break  # Found owner with phone, stop looking
            elif not best_owner:
                # Keep first owner found as fallback
                best_owner = PersonInfo(name=owner_name, source="perplexity")

        # If no owner from Perplexity, use first person from CSV with phone
        if not best_owner and record.persons_from_csv:
            for person in record.persons_from_csv:
                if person.name and person.phone:
                    best_owner = person
                    break
            # If still none, just take first person
            if not best_owner and record.persons_from_csv[0].name:
                best_owner = record.persons_from_csv[0]

        if best_owner:
            record.owners.append(best_owner)

        # Step 4: Enrich owner with Whitepages personal info
        if best_owner and record.city and record.state:
            wp_result = await whitepages_client.lookup_person(
                session,
                best_owner.name,
                record.city,
                record.state
            )
            if wp_result:
                best_owner.personal_address = wp_result.get("personal_address")
                best_owner.personal_city = wp_result.get("personal_city")
                best_owner.personal_state = wp_result.get("personal_state")
                best_owner.personal_zip = wp_result.get("personal_zip")
                best_owner.personal_phone = wp_result.get("personal_phone")
                # Update source to indicate Whitepages enrichment
                if wp_result.get("personal_phone"):
                    best_owner.source = "whitepages"

        return record


def format_output_row(record: RestaurantRecord) -> dict:
    """Format a RestaurantRecord into a single output row.

    Output format prioritizes owner's personal contact info from Whitepages.
    Address/City/State/Zip are the owner's home address (where they live),
    not the restaurant address.
    """
    owner = record.owners[0] if record.owners else None

    # Build owner's personal address as combined string: "street, city, state zip"
    # Prioritize Whitepages personal address, fall back to restaurant address
    if owner and owner.personal_address:
        # Use Whitepages personal address
        addr_street = owner.personal_address
        addr_city = owner.personal_city or ""
        addr_state = owner.personal_state or ""
        addr_zip = owner.personal_zip or ""
        # Format as combined address string
        address_combined = f"{addr_street}, {addr_city}, {addr_state} {addr_zip}".strip()
    else:
        # Fall back to restaurant address
        addr_street = record.address
        addr_city = record.city
        addr_state = record.state
        addr_zip = record.zip_code
        address_combined = f"{addr_street}, {addr_city}, {addr_state} {addr_zip}".strip() if addr_street else ""

    # Phone/Email: prioritize Whitepages personal, then CSV match, then restaurant
    if owner and owner.personal_phone:
        phone = owner.personal_phone
    elif owner and owner.phone:
        phone = owner.phone
    else:
        phone = record.phone

    # Email fallback - Whitepages doesn't return email, use existing data if available
    if owner and owner.email:
        email = owner.email
    else:
        email = record.email

    return {
        "FEIN": record.fein,
        "Name": record.restaurant_name,
        "OwnerName": owner.name if owner else "",
        "Address": address_combined,
        "City": addr_city,
        "State": addr_state,
        "Zip": addr_zip,
        "Phone": phone,
        "Email": email,
        "County": record.county,
        "Expdate": record.expdate,
        "Website": record.website,
        "LLC_Name": record.llc_name,
        "ContactSource": owner.source if owner else "",
    }


# ============================================================================
# Main Pipeline
# ============================================================================

async def process_batch(
    records: list[RestaurantRecord],
    config: Config,
    batch_size: int = 10
) -> list[RestaurantRecord]:
    """Process records in parallel batches."""

    cache = CacheManager(config.cache_dir)
    google_client = GooglePlacesClient(config.google_places_api_key, cache)
    perplexity_client = PerplexityClient(config.openrouter_api_key, cache)
    whitepages_client = WhitepagesClient(config.whitepages_api_key, cache)

    # Semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(batch_size)

    async with aiohttp.ClientSession() as session:
        tasks = [
            process_record(
                record,
                session,
                google_client,
                perplexity_client,
                whitepages_client,
                semaphore
            )
            for record in records
        ]

        # Process with progress bar
        results = await tqdm_asyncio.gather(*tasks, desc="Processing records")

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Restaurant Lead Enrichment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.csv -o output.csv
  python main.py input.csv -o output.csv --batch-size 20
  python main.py input.xlsx -o output.csv

Environment Variables:
  GOOGLE_PLACES_API_KEY  - Google Places API key
  OPENROUTER_API_KEY     - OpenRouter API key (for Perplexity sonar-pro)
        """
    )

    parser.add_argument("input", help="Input CSV or Excel file")
    parser.add_argument("-o", "--output", default="output.csv", help="Output CSV file")
    parser.add_argument("--batch-size", type=int, default=10, help="Parallel batch size")
    parser.add_argument("--cache-dir", default=".cache", help="Cache directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to process (for testing)")

    args = parser.parse_args()

    # Initialize config
    config = Config(cache_dir=Path(args.cache_dir))
    config.validate()

    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    print(f"Reading input file: {args.input}")

    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(input_path)
    else:
        df = pd.read_csv(input_path)

    print(f"Loaded {len(df)} records")

    # Parse records
    print("Parsing records...")
    records = [parse_csv_row(row) for _, row in tqdm(df.iterrows(), total=len(df), desc="Parsing")]

    # Apply limit if specified
    if args.limit is not None:
        records = records[:args.limit]
        print(f"Limited to {len(records)} records")

    # Process records
    print(f"Processing records with batch size {args.batch_size}...")
    processed_records = asyncio.run(process_batch(records, config, args.batch_size))

    # Format output
    print("Formatting output...")
    output_rows = [format_output_row(record) for record in processed_records]

    # Write output
    output_df = pd.DataFrame(output_rows)
    output_df.to_csv(args.output, index=False)

    print(f"\nOutput written to: {args.output}")
    print(f"Total output rows: {len(output_rows)}")

    # Summary
    owners_found = sum(1 for r in processed_records if r.owners)
    owners_with_phone = sum(1 for r in processed_records for o in r.owners if o.phone)

    print(f"\nSummary:")
    print(f"  Records processed: {len(processed_records)}")
    print(f"  Records with owners found: {owners_found}")
    print(f"  Owners with phone numbers: {owners_with_phone}")


if __name__ == "__main__":
    main()
