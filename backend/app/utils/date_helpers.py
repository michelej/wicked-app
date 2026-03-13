from datetime import datetime, timedelta, date
from typing import List, Optional


def calculate_charge_date(
    start_date: datetime, 
    end_date: datetime, 
    day_of_month: Optional[int] = None,
    specific_date: Optional[date] = None,
    frequency: str = "monthly"
) -> datetime:
    """
    Calculate the charge date for a recurring expense within a budget period.
    
    Args:
        start_date: Budget start date
        end_date: Budget end date
        day_of_month: Day of the month to charge (1-31) - for monthly/annual/quarterly
        specific_date: Specific date for one-time expenses
        frequency: Frequency type (monthly, annual, quarterly, one-time)
    
    Returns:
        Calculated charge date within the budget period
    """
    # For one-time expenses, use the specific date if provided
    if frequency == "one-time" and specific_date:
        charge_datetime = datetime.combine(specific_date, datetime.min.time()).replace(hour=12, minute=0, second=0)
        # Only include if the specific date is within the budget period
        if start_date <= charge_datetime <= end_date:
            return charge_datetime
        else:
            # Return None or start_date if outside range
            return None
    
    # For recurring expenses (monthly, annual, quarterly)
    if day_of_month is None:
        raise ValueError("day_of_month is required for recurring expenses")
    
    # Start with the month of start_date
    year = start_date.year
    month = start_date.month
    
    # Try to create the date with the given day
    try:
        charge_date = datetime(year, month, day_of_month, 12, 0, 0)
    except ValueError:
        # If day doesn't exist in this month (e.g., Feb 31), use last day of month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        charge_date = next_month - timedelta(days=1)
        charge_date = charge_date.replace(hour=12, minute=0, second=0, microsecond=0)
    
    # If charge date is before start_date, move to next month
    if charge_date < start_date:
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        
        try:
            charge_date = datetime(year, month, day_of_month, 12, 0, 0)
        except ValueError:
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
            charge_date = next_month - timedelta(days=1)
            charge_date = charge_date.replace(hour=12, minute=0, second=0, microsecond=0)
    
    # If charge date is after end_date, return start_date
    if charge_date > end_date:
        charge_date = start_date.replace(hour=12, minute=0, second=0, microsecond=0)
    
    return charge_date


def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Generate a list of dates between start_date and end_date (inclusive).
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        List of datetime objects for each day in the range
    """
    dates = []
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def is_date_in_range(date: datetime, start_date: datetime, end_date: datetime) -> bool:
    """
    Check if a date is within a given range.
    
    Args:
        date: Date to check
        start_date: Start of range
        end_date: End of range
    
    Returns:
        True if date is within range, False otherwise
    """
    return start_date <= date <= end_date
