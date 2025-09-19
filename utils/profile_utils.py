def houres_between_dates(start_date, end_date=None):
    if end_date is None:
        from datetime import datetime, timezone
        end_date = datetime.now(timezone.utc)
    delta = end_date.timestamp() - start_date.timestamp()
    return delta / 3600