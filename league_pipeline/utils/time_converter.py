from typing import Union

def unix_time_converter(time: Union[float,int] , time_from: str = "mili", time_to: str = "s"):
    """
    Convert between different time units for Unix timestamps.
    
    Args:
        time: The time value to convert
        time_from: Source unit ("mili", "s", "min", "h", "d")
        time_to: Target unit ("mili", "s", "min", "h", "d")
    
    Returns:
        Converted time value as int
    """
    result = None
    
    if time_from == "mili":
        if time_to == "s":
            result = time / 1000
        elif time_to == "min":
            result = time / 1000 / 60
        elif time_to == "h":
            result = time / 1000 / 3600
        elif time_to == "d":
            result = time / 1000 / 86400
        elif time_to == "mili":
            return time
    
    elif time_from == "s":
        if time_to == "mili":
            return time * 1000
        elif time_to == "min":
            result = time / 60
        elif time_to == "h":
            result = time / 3600
        elif time_to == "d":
            result = time / 86400
        elif time_to == "s":
            return time
    
    elif time_from == "min":
        if time_to == "mili":
            return time * 60 * 1000
        elif time_to == "s":
            return time * 60
        elif time_to == "h":
            result = time / 60
        elif time_to == "d":
            result = time / 1440
        elif time_to == "min":
            return time
    
    elif time_from == "h":
        if time_to == "mili":
            return time * 3600 * 1000
        elif time_to == "s":
            return time * 3600
        elif time_to == "min":
            return time * 60
        elif time_to == "d":
            result = time / 24
        elif time_to == "h":
            return time
    
    elif time_from == "d":
        if time_to == "mili":
            return time * 86400 * 1000
        elif time_to == "s":
            return time * 86400
        elif time_to == "min":
            return time * 1440
        elif time_to == "h":
            return time * 24
        elif time_to == "d":
            return time
    
    if result is not None:
        return int(result)
    
    raise ValueError(f"Invalid time units: from '{time_from}' to '{time_to}'")

