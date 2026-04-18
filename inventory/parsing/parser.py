import datetime

def split_log_line(line: str) -> dict:
    parts = line.split(" ")

    if len(parts) != 5:
        raise ValueError(f"Invalid log line format: {line}")

    date, time, operation, item_id, quantity = parts

    return {
        "datetime": datetime.datetime.strptime(
            f"{date} {time.rstrip(':')}", "%Y-%m-%d %H:%M:%S"
        ),
        "operation": operation,
        "item_id": item_id,
        "quantity": int(quantity)
    }