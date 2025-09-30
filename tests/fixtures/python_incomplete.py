"""Sample Python file with incomplete documentation."""


def calculate_area(width, height):
    """Calculate area."""
    return width * height


def process_data(data, options=None):
    """Process some data.

    Parameters
    ----------
    data : list
        Input data

    Returns
    -------
    dict
    """
    if options is None:
        options = {}
    return {"processed": True, "count": len(data)}