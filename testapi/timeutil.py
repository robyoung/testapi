import datetime
import re

def parse_iso8601(date_string):
    """Parse an iso8601 formatted string as a datetime.datetime object.

    >>> parse_iso8601('2012')
    datetime.datetime(2012, 1, 1, 0, 0)

    >>> parse_iso8601('2012-12')
    datetime.datetime(2012, 12, 1, 0, 0)

    >>> parse_iso8601('2012-12-12')
    datetime.datetime(2012, 12, 12, 0, 0)

    >>> parse_iso8601('2012-01-01')
    datetime.datetime(2012, 1, 1, 0, 0)

    >>> parse_iso8601('2012-12-12T10:10')
    datetime.datetime(2012, 12, 12, 10, 10)

    >>> parse_iso8601('2012-12-12T10:10:10')
    datetime.datetime(2012, 12, 12, 10, 10, 10)

    >>> parse_iso8601('invalid')
    Traceback (most recent call last):
    ...
    ValueError: Date string must be a valid iso8601 date time.
    """
    pattern = re.compile(
        r'^(?P<year>\d{4})(?:-?(?P<month>\d{2})(?:-?(?P<day>\d{2})(?:T(?P<hour>\d{2}):(?P<minute>\d{2})(?::(?P<second>\d{2}))?)?)?)?$'
    )

    match = pattern.match(date_string)
    if not match: raise ValueError('Date string must be a valid iso8601 date time.')
    matches = match.groupdict()
    matches['year']  = int(matches['year'])
    matches['month'] = int(matches['month'] or '01')
    matches['day']   = int(matches['day'] or '01')
    matches['hour'] = int(matches['hour'] or '00')
    matches['minute'] = int(matches['minute'] or '00')
    matches['second'] = int(matches['second'] or '00')
    return datetime.datetime(
        matches['year'], matches['month'], matches['day'],
        matches['hour'], matches['minute'], matches['second']
    )

