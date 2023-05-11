# -*- coding: utf-8 -*-

"""
Functions for helping streamline methods of the `Search` class.
"""

from datetime import date, timedelta


def convert_to_datetime(date_string: str, date_name: str) -> date:
    """
    Function that converts a string representing a date to a
    `datetime.date` object.

    Parameters
    ----------
    date_string : str
        One of `'today'`, `'yesterday'`, or an ISO-formatted
        (`'YYYY-MM-DD'`) string.
    date_name : str
        Name corresponding to the date being converted. Used for
        specificity in error messages.

    Returns
    -------
    datetime.date
        The date `date_string` converted to a `datetime.date` object.
    """
    # Get today's date and yesterday's date
    today     = date.today()
    yesterday = today - timedelta(days=1)

    # Check input date format and convert to datetime.date
    if date_string == "today":
        return today
    elif date_string == "yesterday":
        return yesterday
    else:
        try:
            date_string = date.fromisoformat(date_string)
            return date_string
        except ValueError:
            raise ValueError(f"invalid input for `{date_name}', "
                             "expected 'today', 'yesterday', or str "
                             "formatted as 'YYYY-MM-DD'.")

   
def elapsed_time(time: float) -> str:
    """
    Function that converts a float representing a time in seconds to a
    string showing the elapsed time in hours, minutes, and seconds.

    Parameters
    ----------
    elapsed_time : float
        Float of elapsed time in seconds.

    Returns
    -------
    str
        String of elapsed time in hours, minutes, and seconds.
    """
    # Validate time input
    if time < 0.0:
        raise ValueError("invalid input for `time`, "
                         "expected float equal to or greater than 0.0.")

    # Formatting for times less than a minute
    if time < 60.0:
        return f"{time:.1f} sec"
    
    # Formatting for times less than an hour
    elif time < 3600.0:
        m, s = divmod(time, 60)
        return f"{int(m)} min {s:.1f} sec"
    
    # Formatting for times over an hour
    else:
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        return f"{int(h)} hr {int(m)} min {s:.1f} sec"
    