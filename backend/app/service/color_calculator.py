"""
Calculate accountability colors using California Dashboard 5x5 grid rules.

This module implements the California Department of Education's color calculation
logic for accountability indicators. Colors are determined by combining status
levels (current performance) and change levels (year-over-year change) using
a 5x5 grid system.

Reference: https://www.cde.ca.gov/ta/ac/cm/fivebyfivecolortables.asp
"""

# Standard thresholds for converting Mean Scale Score to Distance from Standard (DFS)
# These represent the "Met Standard" (Level 3) threshold for each grade
# Formula: DFS = Mean Scale Score - Standard Threshold
STANDARD_THRESHOLDS = {
    "ELA": {
        "3": 2432,
        "4": 2473,
        "5": 2502,
        "6": 2531,
        "7": 2552,
        "8": 2567,
        "11": 2583,
        # Aggregate uses weighted average - approximate
        "ALL": 2500,
    },
    "MATH": {
        "3": 2436,
        "4": 2485,
        "5": 2528,
        "6": 2552,
        "7": 2567,
        "8": 2586,
        "11": 2628,
        # Aggregate uses weighted average - approximate
        "ALL": 2530,
    },
}

# Status level cut points by indicator
# For academic indicators, values are Distance from Standard (DFS)
# Format: [(threshold, level), ...] - check in order, first match wins (>= threshold)
STATUS_CUTPOINTS = {
    # ELA Grades 3-8: Distance from Standard
    "ELA": [
        (45.0, 5),  # Very High: +45.0 or more
        (10.0, 4),  # High: +10.0 to +44.9
        (-5.0, 3),  # Medium: -5.0 to +9.9
        (-70.0, 2),  # Low: -70.0 to -5.1
        (float("-inf"), 1),  # Very Low: below -70.0
    ],
    # ELA Grade 11: Different cut points
    "ELA11": [
        (75.0, 5),  # Very High: +75.0 or more
        (30.0, 4),  # High: +30.0 to +74.9
        (0.0, 3),  # Medium: 0.0 to +29.9
        (-45.0, 2),  # Low: -45.0 to -0.1
        (float("-inf"), 1),  # Very Low: below -45.0
    ],
    # MATH Grades 3-8: Distance from Standard
    "MATH": [
        (35.0, 5),  # Very High: +35.0 or more
        (0.0, 4),  # High: 0.0 to +34.9
        (-25.0, 3),  # Medium: -25.0 to -0.1
        (-95.0, 2),  # Low: -95.0 to -25.1
        (float("-inf"), 1),  # Very Low: below -95.0
    ],
    # MATH Grade 11: Different cut points
    "MATH11": [
        (25.0, 5),  # Very High: +25.0 or more
        (0.0, 4),  # High: 0.0 to +24.9
        (-60.0, 3),  # Medium: -60.0 to -0.1
        (-115.0, 2),  # Low: -115.0 to -60.1
        (float("-inf"), 1),  # Very Low: below -115.0
    ],
    # Science: Science Points
    "SCI": [
        (65.0, 5),  # Very High: 65.0 or more
        (55.0, 4),  # High: 55.0 to 64.9
        (45.0, 3),  # Medium: 45.0 to 54.9
        (35.0, 2),  # Low: 35.0 to 44.9
        (float("-inf"), 1),  # Very Low: below 35.0
    ],
    # Chronic Absenteeism: Percentage (lower is better)
    "CHRONIC": [
        (float("-inf"), 5),  # Very Low: 2.5% or less - handled specially
    ],
    # Suspension Rate: Percentage (lower is better)
    "SUSP": [
        (float("-inf"), 5),  # Varies by school type - handled specially
    ],
    # Graduation Rate: Percentage (higher is better)
    "GRAD": [
        (95.0, 5),  # Very High: 95.0% or more
        (90.5, 4),  # High: 90.5% to 94.9%
        (80.0, 3),  # Medium: 80.0% to 90.4%
        (68.0, 2),  # Low: 68.0% to 79.9%
        (float("-inf"), 1),  # Very Low: below 68.0%
    ],
    # English Learner Progress: Percentage (higher is better)
    "ELPI": [
        (65.0, 5),  # Very High: 65.0% or more
        (55.0, 4),  # High: 55.0% to 64.9%
        (45.0, 3),  # Medium: 45.0% to 54.9%
        (35.0, 2),  # Low: 35.0% to 44.9%
        (float("-inf"), 1),  # Very Low: below 35.0%
    ],
    # College/Career Indicator: Percentage (higher is better)
    "CCI": [
        (70.0, 5),  # Very High: 70.0% or more
        (55.0, 4),  # High: 55.0% to 69.9%
        (35.0, 3),  # Medium: 35.0% to 54.9%
        (10.0, 2),  # Low: 10.0% to 34.9%
        (float("-inf"), 1),  # Very Low: below 10.0%
    ],
}

# Chronic Absenteeism status cut points (lower is better - reverse scale)
CHRONIC_STATUS_CUTPOINTS = [
    (2.5, 5),  # Very Low: 2.5% or less
    (5.0, 4),  # Low: 2.6% to 5.0%
    (10.0, 3),  # Medium: 5.1% to 10.0%
    (20.0, 2),  # High: 10.1% to 20.0%
    (float("inf"), 1),  # Very High: 20.1% or more
]

# Change level cut points by indicator
# Format: [(threshold, level), ...] - check in order, first match wins (>= threshold)
CHANGE_CUTPOINTS = {
    # ELA/MATH: Change in DFS points
    "ELA": [
        (15.0, 5),  # Increased Significantly: +15.0 or more
        (3.0, 4),  # Increased: +3.0 to +14.9
        (-2.9, 3),  # Maintained: -2.9 to +2.9
        (-15.0, 2),  # Declined: -15.0 to -3.0
        (float("-inf"), 1),  # Declined Significantly: below -15.0
    ],
    "MATH": [
        (15.0, 5),  # Increased Significantly: +15.0 or more
        (3.0, 4),  # Increased: +3.0 to +14.9
        (-2.9, 3),  # Maintained: -2.9 to +2.9
        (-15.0, 2),  # Declined: -15.0 to -3.0
        (float("-inf"), 1),  # Declined Significantly: below -15.0
    ],
    # Science: Change in Science Points
    "SCI": [
        (5.0, 5),  # Increased Significantly: +5.0 or more
        (2.0, 4),  # Increased: +2.0 to +4.9
        (-1.9, 3),  # Maintained: -1.9 to +1.9
        (-5.0, 2),  # Declined: -5.0 to -2.0
        (float("-inf"), 1),  # Declined Significantly: below -5.0
    ],
    # Chronic Absenteeism: Change in percentage points (decrease is better)
    "CHRONIC": [
        (-3.0, 5),  # Declined Significantly: -3.0 or more decrease
        (-0.5, 4),  # Declined: -0.5 to -2.9 decrease
        (0.4, 3),  # Maintained: -0.4 to +0.4
        (3.0, 2),  # Increased: +0.5 to +3.0
        (float("inf"), 1),  # Increased Significantly: +3.1 or more
    ],
    # Graduation Rate: Change in percentage points
    "GRAD": [
        (5.0, 5),  # Increased Significantly: +5.0 or more
        (1.0, 4),  # Increased: +1.0 to +4.9
        (-0.9, 3),  # Maintained: -0.9 to +0.9
        (-5.0, 2),  # Declined: -5.0 to -1.0
        (float("-inf"), 1),  # Declined Significantly: below -5.0
    ],
    # English Learner Progress: Change in percentage points
    "ELPI": [
        (10.0, 5),  # Increased Significantly: +10.0 or more
        (2.0, 4),  # Increased: +2.0 to +9.9
        (-1.9, 3),  # Maintained: -1.9 to +1.9
        (-10.0, 2),  # Declined: -10.0 to -2.0
        (float("-inf"), 1),  # Declined Significantly: below -10.0
    ],
    # College/Career Indicator: Change in percentage
    "CCI": [
        (9.0, 5),  # Increased Significantly: +9.0% or more
        (2.0, 4),  # Increased: +2.0% to +8.9%
        (-1.9, 3),  # Maintained: -1.9% to +1.9%
        (-9.0, 2),  # Declined: -9.0% to -2.0%
        (float("-inf"), 1),  # Declined Significantly: below -9.0%
    ],
}

# 5x5 color grids by indicator
# Grid[status_level][change_level] = color (1=red, 2=orange, 3=yellow, 4=green, 5=blue)
# Academic indicators (ELA, MATH, SCI) use the same grid pattern
ACADEMIC_COLOR_GRID: dict[int, dict[int, int | None]] = {
    5: {5: 5, 4: 5, 3: 5, 2: 4, 1: 4},  # Very High status
    4: {5: 5, 4: 4, 3: 4, 2: 4, 1: 4},  # High status
    3: {5: 4, 4: 4, 3: 3, 2: 3, 1: 3},  # Medium status
    2: {5: 3, 4: 3, 3: 2, 2: 2, 1: 2},  # Low status
    1: {5: 2, 4: 2, 3: 1, 2: 1, 1: 1},  # Very Low status
}

# Chronic Absenteeism grid (note: columns are reversed - decline is good)
CHRONIC_COLOR_GRID: dict[int, dict[int, int | None]] = {
    5: {5: 5, 4: 5, 3: 5, 2: 4, 1: 3},  # Very Low (best)
    4: {5: 5, 4: 4, 3: 4, 2: 3, 1: 2},  # Low
    3: {5: 4, 4: 4, 3: 3, 2: 2, 1: 2},  # Medium
    2: {5: 3, 4: 3, 3: 2, 2: 2, 1: 1},  # High
    1: {5: 3, 4: 2, 3: 1, 2: 1, 1: 1},  # Very High (worst)
}

# Graduation Rate grid
GRAD_COLOR_GRID: dict[int, dict[int, int | None]] = {
    5: {5: 5, 4: 5, 3: 5, 2: 5, 1: None},  # Very High - N/A for Dec Sig
    4: {5: 5, 4: 4, 3: 4, 2: 3, 1: 2},  # High
    3: {5: 4, 4: 4, 3: 3, 2: 2, 1: 2},  # Medium
    2: {5: 3, 4: 3, 3: 2, 2: 2, 1: 1},  # Low
    1: {5: 1, 4: 1, 3: 1, 2: 1, 1: 1},  # Very Low - always red
}

# ELPI grid (increase is good)
ELPI_COLOR_GRID: dict[int, dict[int, int | None]] = {
    5: {5: 5, 4: 5, 3: 5, 2: 4, 1: 3},  # Very High
    4: {5: 5, 4: 4, 3: 4, 2: 3, 1: 2},  # High
    3: {5: 4, 4: 4, 3: 3, 2: 2, 1: 2},  # Medium
    2: {5: 3, 4: 3, 3: 2, 2: 2, 1: 1},  # Low
    1: {5: 3, 4: 2, 3: 1, 2: 1, 1: 1},  # Very Low
}

# CCI grid (same as ELPI)
CCI_COLOR_GRID = ELPI_COLOR_GRID

# Map indicators to their color grids
COLOR_GRIDS: dict[str, dict[int, dict[int, int | None]]] = {
    "ELA": ACADEMIC_COLOR_GRID,
    "ELA11": ACADEMIC_COLOR_GRID,
    "MATH": ACADEMIC_COLOR_GRID,
    "MATH11": ACADEMIC_COLOR_GRID,
    "SCI": ACADEMIC_COLOR_GRID,
    "CHRONIC": CHRONIC_COLOR_GRID,
    "GRAD": GRAD_COLOR_GRID,
    "ELPI": ELPI_COLOR_GRID,
    "CCI": CCI_COLOR_GRID,
}


def convert_mean_scale_to_dfs(
    mean_scale_score: float | None,
    indicator: str,
    grade: str = "ALL",
) -> float | None:
    """Convert Mean Scale Score to Distance from Standard (DFS).

    Args:
        mean_scale_score: The mean scale score from assessment data
        indicator: ELA or MATH
        grade: Grade level (3-8, 11, or ALL for aggregate)

    Returns:
        Distance from Standard, or None if conversion not possible
    """
    if mean_scale_score is None:
        return None

    thresholds = STANDARD_THRESHOLDS.get(indicator, {})
    threshold = thresholds.get(str(grade), thresholds.get("ALL"))

    if threshold is None:
        return None

    return mean_scale_score - threshold


def calculate_status_level(indicator: str, currstatus: float | None) -> int | None:
    """Calculate status level (1-5) from current status value.

    Args:
        indicator: Indicator code (ELA, MATH, etc.)
        currstatus: Current status value (DFS for academic, percentage for others)

    Returns:
        Status level 1-5, or None if calculation not possible
    """
    if currstatus is None:
        return None

    # Handle Chronic Absenteeism specially (lower is better)
    if indicator == "CHRONIC":
        for threshold, level in CHRONIC_STATUS_CUTPOINTS:
            if currstatus <= threshold:
                return level
        return 1

    cutpoints = STATUS_CUTPOINTS.get(indicator)
    if not cutpoints:
        return None

    for threshold, level in cutpoints:
        if currstatus >= threshold:
            return level

    return 1


def calculate_change_level(indicator: str, change: float | None) -> int | None:
    """Calculate change level (1-5) from year-over-year change.

    Args:
        indicator: Indicator code (ELA, MATH, etc.)
        change: Year-over-year change value

    Returns:
        Change level 1-5, or None if calculation not possible
    """
    if change is None:
        return None

    cutpoints = CHANGE_CUTPOINTS.get(indicator)
    if not cutpoints:
        # Fall back to ELA cutpoints for indicators that share them
        cutpoints = CHANGE_CUTPOINTS.get("ELA")
    if not cutpoints:
        return None

    # Handle Chronic Absenteeism specially (decrease is good)
    if indicator == "CHRONIC":
        for threshold, level in cutpoints:
            if change <= threshold:
                return level
        return 1

    for threshold, level in cutpoints:
        if change >= threshold:
            return level

    return 1


def calculate_color(
    indicator: str, statuslevel: int | None, changelevel: int | None
) -> int | None:
    """Calculate color (1-5) from status and change levels using 5x5 grid.

    Args:
        indicator: Indicator code (ELA, MATH, etc.)
        statuslevel: Status level 1-5
        changelevel: Change level 1-5

    Returns:
        Color level 1-5 (1=red, 2=orange, 3=yellow, 4=green, 5=blue),
        or None if calculation not possible
    """
    if statuslevel is None or changelevel is None:
        return None

    grid = COLOR_GRIDS.get(indicator, ACADEMIC_COLOR_GRID)
    return grid.get(statuslevel, {}).get(changelevel)


def calculate_all(
    indicator: str,
    currstatus: float | None,
    priorstatus: float | None = None,
    is_mean_scale_score: bool = False,
    grade: str = "ALL",
) -> dict[str, float | int | None]:
    """Calculate all color-related fields for an indicator.

    Args:
        indicator: Indicator code (ELA, MATH, etc.)
        currstatus: Current status value
        priorstatus: Prior year status value (optional)
        is_mean_scale_score: If True, convert from Mean Scale Score to DFS
        grade: Grade level for DFS conversion (default ALL for aggregate)

    Returns:
        dict with keys: change, statuslevel, changelevel, color
    """
    # Convert Mean Scale Score to DFS if needed (for state assessment data)
    if is_mean_scale_score and indicator in ("ELA", "MATH"):
        currstatus = convert_mean_scale_to_dfs(currstatus, indicator, grade)
        priorstatus = convert_mean_scale_to_dfs(priorstatus, indicator, grade)

    # Calculate change
    change = None
    if currstatus is not None and priorstatus is not None:
        change = currstatus - priorstatus

    # Calculate levels
    statuslevel = calculate_status_level(indicator, currstatus)
    changelevel = calculate_change_level(indicator, change)
    color = calculate_color(indicator, statuslevel, changelevel)

    return {
        "change": change,
        "statuslevel": statuslevel,
        "changelevel": changelevel,
        "color": color,
    }
