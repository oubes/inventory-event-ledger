# Inventory Event Ledger Pipeline

## Overview

This is a lightweight batch data pipeline for processing inventory event logs.
It reads raw log files, parses each event into structured records, performs daily aggregation per item, and exports the results into per-item CSV files.

The project is designed for a client use case focused on inventory movement reporting.

---

## Pipeline Flow

```text
Log File
  ↓
Read (file ingestion)
  ↓
Parse (line validation + splitting)
  ↓
Transform (DataFrame creation)
  ↓
Aggregation (group by item/day/operation)
  ↓
Export (CSV per item)
```

---

## Input Format

Each log line must follow this structure:

```text
YYYY-MM-DD HH:MM:SS: OPERATION ITEM_ID QUANTITY
```

### Example:

```text
2026-04-18 10:15:00: IN Cover100 50
2026-04-18 11:00:00: OUT Cover100 20
```

---

## Output

The pipeline generates one CSV file per `item_id` inside the output directory.

### Example structure:

```text
outputs/
├── Cover100_aggregated.csv
├── charger18_aggregated.csv
├── charger30_aggregated.csv
```

---

## Output Schema

Each CSV contains:

| item_id | datetime | operation | quantity |
| ------- | -------- | --------- | -------- |

---

## Core Functionality

### 1. Log Reading

Reads raw log file and filters empty lines.

### 2. Parsing

Each line is parsed into structured fields:

* date
* time
* operation
* item_id
* quantity

Invalid lines are skipped with error logging.

### 3. Transformation

Combines `date + time` into a single `datetime` field and builds a pandas DataFrame.

### 4. Aggregation

Daily aggregation per item and operation:

```python
groupby([
    "item_id",
    pd.Grouper(key="datetime", freq="D"),
    "operation"
])["quantity"].sum()
```

### 5. Export

* One CSV per `item_id`
* Sorted by datetime
* Logs file path after saving

---

## Configuration

### .env

```text
FILE_PATH=path/to/inventory.log
```

---

## Requirements

```text
pandas==2.2.2
python-dotenv==1.0.1
```

---

## Run

```bash
python main.py
```
