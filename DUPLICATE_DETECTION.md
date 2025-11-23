# Duplicate Detection Feature

## Overview

Twiga Scan now includes automatic duplicate detection to identify when Lightning addresses, Bitcoin addresses, invoices, or LNURL payments have been scanned multiple times. This helps users identify potentially suspicious payment requests that are being reused.

## Features

### 1. **Automatic Duplicate Detection**
- Tracks all scanned payment identifiers (Lightning addresses, Bitcoin addresses, BOLT11 invoices, LNURL)
- Case-insensitive matching (user@example.com = User@Example.COM)
- Immediate warnings on duplicate detection

### 2. **Usage Tracking**
- Counts how many times each identifier has been scanned
- Records first time identifier was seen
- Provides historical context for each scan

### 3. **Graduated Warning Levels**

#### Standard Duplicate Warning
Shown when an address/invoice is scanned 2+ times:
```
⚠️ This address has been scanned 2 time(s) before. First seen: 2025-11-23T12:34:56
```

#### High Frequency Warning
Shown when an address/invoice is scanned 3+ times:
```
🚨 HIGH FREQUENCY: This address has been used multiple times. Exercise caution.
```

## API Response

When scanning a payment identifier, the response now includes:

```json
{
  "scan_id": "uuid",
  "content_type": "LIGHTNING_ADDRESS",
  "parsed_data": {...},
  "auth_status": "Verified",
  "warnings": [
    "⚠️ This address has been scanned 2 time(s) before. First seen: 2025-11-23T12:34:56"
  ],
  "is_duplicate": true,
  "usage_count": 2,
  "first_seen": "2025-11-23T12:34:56.123456"
}
```

### New Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_duplicate` | boolean | `true` if this identifier has been scanned before |
| `usage_count` | integer | Total number of times this identifier has been scanned (including current scan) |
| `first_seen` | string (ISO 8601) | Timestamp when this identifier was first scanned |

## Supported Payment Types

Duplicate detection works for:

1. **Lightning Addresses** (`user@domain.com`)
   - Normalized identifier: lowercase email address

2. **Bitcoin Addresses** (BIP21 URIs)
   - Normalized identifier: lowercase Bitcoin address

3. **BOLT11 Invoices** (Lightning invoices)
   - Normalized identifier: lowercase invoice string

4. **LNURL** (Lightning URL payment requests)
   - Normalized identifier: lowercase URL or LNURL string

## Database Schema

### New Fields in `scan_logs` Table

```sql
normalized_identifier VARCHAR(500) INDEXED
    -- Normalized version of address/invoice for duplicate detection
    
first_seen TIMESTAMP
    -- First time this identifier was seen in the system
    
usage_count INTEGER DEFAULT 1
    -- Number of times this identifier has been scanned
```

### Migration

To apply the database migration:

```bash
cd backend
python -m alembic upgrade head
```

## Use Cases

### 1. Phishing Detection
If a malicious actor creates a QR code and distributes it to multiple victims, the system will flag it after the first scan:

```
First victim scans: ✅ No warning
Second victim scans: ⚠️ Duplicate warning
Third victim scans: 🚨 HIGH FREQUENCY warning
```

### 2. Reused Payment Requests
Merchants who reuse the same Lightning address for multiple customers will trigger warnings, encouraging them to generate unique payment requests.

### 3. Suspicious Patterns
Addresses that appear frequently across different scanning sessions can be flagged for investigation.

## Security Considerations

### Privacy
- Identifiers are stored as lowercase strings (not hashed) for exact matching
- No personally identifiable information beyond the payment identifier itself is stored
- All scans are recorded with timestamps for audit purposes

### False Positives
Duplicate warnings may occur in legitimate scenarios:
- Personal Lightning addresses used repeatedly by the owner
- Business addresses advertised publicly
- Static QR codes for donations

Users should evaluate warnings in context.

## Testing

Run duplicate detection tests:

```bash
cd backend
python -m pytest test_duplicate_detection.py -v
```

### Test Coverage

- ✅ Lightning address duplicate detection
- ✅ Bitcoin address duplicate detection  
- ✅ High frequency warnings (3+ scans)
- ✅ Case-insensitive matching
- ✅ Different addresses not marked as duplicates

## Frontend Integration

To display duplicate warnings in the UI, check the response fields:

```typescript
interface ScanResponse {
  scan_id: string;
  content_type: string;
  parsed_data: object;
  auth_status: string;
  warnings: string[];
  is_duplicate: boolean;       // NEW
  usage_count: number;          // NEW
  first_seen: string | null;   // NEW
}

// Example usage
if (response.is_duplicate) {
  showWarningBanner(`This address has been scanned ${response.usage_count} time(s)`);
  
  if (response.usage_count >= 3) {
    showCriticalAlert('HIGH FREQUENCY: Exercise caution!');
  }
}
```

## Configuration

No configuration is required. Duplicate detection is enabled automatically for all scans.

## Performance

- **Index**: `normalized_identifier` is indexed for fast lookups
- **Query Performance**: O(1) lookup for existing identifiers
- **Storage**: Minimal overhead (~500 bytes per scan for identifier storage)

## Future Enhancements

Potential improvements for future versions:

1. **Time-based decay**: Reduce warning severity for old duplicates
2. **Whitelist**: Allow users to mark trusted addresses to suppress warnings
3. **Geographic patterns**: Correlate duplicate scans with IP locations
4. **Rate limiting**: Flag addresses scanned too frequently within a time window
5. **Export**: Generate reports of high-frequency addresses
6. **Admin dashboard**: View most scanned identifiers across all users

## Troubleshooting

### Duplicate warnings not appearing
1. Verify migration was applied: `python -m alembic current`
2. Check database has new columns: 
   ```sql
   PRAGMA table_info(scan_logs);
   ```
3. Ensure API response includes new fields

### False negatives (duplicates not detected)
- Verify identifier normalization is working (check `normalized_identifier` in database)
- Confirm case sensitivity is handled (all identifiers should be lowercase)

### Performance issues
- Check index exists: 
   ```sql
   SELECT * FROM sqlite_master WHERE type='index' AND name='ix_scan_logs_normalized_identifier';
   ```

## API Examples

### Example 1: First Scan (No Duplicate)

**Request:**
```bash
POST /api/scan/
{
  "content": "user@strike.me"
}
```

**Response:**
```json
{
  "scan_id": "123e4567-e89b-12d3-a456-426614174000",
  "content_type": "LIGHTNING_ADDRESS",
  "is_duplicate": false,
  "usage_count": 1,
  "first_seen": "2025-11-23T12:00:00.000000",
  "warnings": []
}
```

### Example 2: Duplicate Scan

**Request:**
```bash
POST /api/scan/
{
  "content": "user@strike.me"
}
```

**Response:**
```json
{
  "scan_id": "223e4567-e89b-12d3-a456-426614174000",
  "content_type": "LIGHTNING_ADDRESS",
  "is_duplicate": true,
  "usage_count": 2,
  "first_seen": "2025-11-23T12:00:00.000000",
  "warnings": [
    "⚠️ This address has been scanned 2 time(s) before. First seen: 2025-11-23T12:00:00"
  ]
}
```

### Example 3: High Frequency

**Request:**
```bash
POST /api/scan/
{
  "content": "user@strike.me"
}
```

**Response (4th scan):**
```json
{
  "scan_id": "323e4567-e89b-12d3-a456-426614174000",
  "content_type": "LIGHTNING_ADDRESS",
  "is_duplicate": true,
  "usage_count": 4,
  "first_seen": "2025-11-23T12:00:00.000000",
  "warnings": [
    "🚨 HIGH FREQUENCY: This address has been used multiple times. Exercise caution.",
    "⚠️ This address has been scanned 4 time(s) before. First seen: 2025-11-23T12:00:00"
  ]
}
```

## License

Same as parent project (see LICENSE file)
