import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_csv(file_path):
    encodings = ["utf-8", "utf-8-sig", "utf-16", "latin-1"]
    df = None
    
    # Try different encodings
    for encoding in encodings:
        try:
            logger.info(f"Trying to parse CSV with encoding: {encoding}")
            # Use low_memory=False to handle mixed types in large files
            df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip')
            break
        except Exception as e:
            logger.warning(f"Failed parsing with encoding {encoding}: {e}")
            continue
            
    if df is None:
        logger.error("Could not parse CSV file with any supported encoding.")
        return []

    # Clean columns (strip spaces, lowercase)
    df.columns = [str(col).strip().lower() for col in df.columns]
    logger.info(f"CSV Columns found: {list(df.columns)}")

    # Column Mapping Aliases
    timestamp_aliases = ["timestamp", "time", "date", "datetime", "timecreated", "date and time", "time_created", "event_time", "created"]
    source_aliases = ["source", "provider", "providername", "computer", "host", "hostname", "log", "logname"]
    event_aliases = ["event", "message", "description", "info", "task category", "task", "activity", "event_id", "id", "name"]
    severity_aliases = ["severity", "level", "leveltext", "type", "criticality", "status"]

    # Auto-detection function
    def find_column(aliases, default_idx=0):
        for alias in aliases:
            # Exact match
            if alias in df.columns:
                return alias
            # Substring match
            for col in df.columns:
                if alias in col:
                    return col
        # Fallback to column index if valid
        if default_idx < len(df.columns):
            return df.columns[default_idx]
        return None

    timestamp_col = find_column(timestamp_aliases, 0)
    source_col = find_column(source_aliases, 1)
    event_col = find_column(event_aliases, 2)
    severity_col = find_column(severity_aliases, 3)

    logger.info(f"Mapped columns -> timestamp: {timestamp_col}, source: {source_col}, event: {event_col}, severity: {severity_col}")

    events = []
    for _, row in df.iterrows():
        # Extracted values
        raw_time = str(row.get(timestamp_col, "")) if timestamp_col else ""
        raw_source = str(row.get(source_col, "")) if source_col else ""
        raw_event = str(row.get(event_col, "")) if event_col else ""
        raw_severity = str(row.get(severity_col, "")) if severity_col else ""

        # Formatting values
        timestamp = raw_time.strip()
        source = raw_source.strip()
        event = raw_event.strip()
        severity = raw_severity.strip()

        # Clean up multi-line values or huge text blocks (common in Event Log 'Message' fields)
        if len(event) > 150:
            event = event[:147] + "..."

        events.append({
            "timestamp": timestamp or "Unknown",
            "source": source or "EventLog",
            "event": event or "Log Event Details",
            "severity": severity or "Medium"
        })

    logger.info(f"Successfully parsed {len(events)} events.")
    return events