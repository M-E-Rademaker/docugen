"""Sample Python file with proper NumPy-style documentation."""


def add_numbers(a, b):
    """
    Add two numbers together.

    This function takes two numeric values and returns their sum.
    It handles both integers and floating-point numbers.

    Parameters
    ----------
    a : int or float
        The first number to add
    b : int or float
        The second number to add

    Returns
    -------
    int or float
        The sum of a and b

    Examples
    --------
    >>> add_numbers(2, 3)
    5
    >>> add_numbers(2.5, 3.7)
    6.2
    """
    return a + b


def multiply_list(numbers):
    """
    Multiply all numbers in a list.

    Parameters
    ----------
    numbers : list of int or float
        List of numbers to multiply together

    Returns
    -------
    int or float
        Product of all numbers in the list

    Raises
    ------
    ValueError
        If the list is empty

    Examples
    --------
    >>> multiply_list([2, 3, 4])
    24
    """
    if not numbers:
        raise ValueError("List cannot be empty")
    result = 1
    for num in numbers:
        result *= num
    return result