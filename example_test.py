def calculate_average(numbers):
    return sum(numbers) / len(numbers) if numbers else 0

def find_maximum(data):
    if not data:
        return None
    return max(data)