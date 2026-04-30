# Bug Fixes Summary

## Issues Fixed

### 1. SMS Notifier Field Mismatch (src/models.py)
**Problem:** The `SMSNotifier` class referenced fields that didn't exist in `AlertConfig`:
- `sms_provider`
- `sms_recipients`
- `sms_account_sid`
- `sms_auth_token`
- `sms_from_number`

**Fix:** Added all missing SMS-related fields to the `AlertConfig` dataclass:
```python
sms_provider: str = "twilio"
sms_recipients: list = field(default_factory=list)
sms_account_sid: str = ""
sms_auth_token: str = ""
sms_from_number: str = ""
```

Also updated `to_dict()` and `from_dict()` methods to include these new fields.

### 2. SMS Notifier Default Values (src/notifications/sms_notifier.py)
**Problem:** The SMS notifier didn't handle cases where SMS fields might be empty.

**Fix:** Added default values when initializing:
```python
self.provider = config.sms_provider or "twilio"
self.recipients = config.sms_recipients or []
```

### 3. Redfin Scraper Square Footage Parsing (src/scrapers/redfin_scraper.py)
**Problem:** The `_parse_sqft` method was incorrectly parsing square footage by removing ALL non-numeric characters, which would corrupt numbers like "1,234" to "1234" incorrectly.

**Fix:** Implemented proper regex patterns to match square footage formats:
- `1,234 sqft`
- `1234 sq ft`
- `1,234 sq. ft.`

The new implementation:
- Uses specific regex patterns to match common square footage formats
- Properly handles comma-separated numbers
- Returns `None` if no match is found instead of corrupting the data

## Test Results
All 19 tests pass:
- Property model tests (3/3)
- SearchCriteria model tests (2/2)
- Alert model tests (2/2)
- AlertConfig model tests (2/2)
- CriteriaEngine tests (3/3)
- DataStore tests (5/5)
- PropertyAlertOrchestrator tests (2/2)
- Redfin scraper tests (2/2)

## Files Modified
1. `src/models.py` - Added SMS fields to AlertConfig
2. `src/notifications/sms_notifier.py` - Added default value handling
3. `src/scrapers/redfin_scraper.py` - Fixed square footage parsing
