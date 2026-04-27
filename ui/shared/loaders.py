from pathlib import Path
import pandas as pd

BASE_OUTPUT = Path("outputs")


def load_full_dataset():
    path = BASE_OUTPUT / "aggregated_selling"

    if not path.exists():
        return None

    frames = []

    for sub in ["days", "months"]:
        sub_path = path / sub

        if not sub_path.exists():
            continue

        for file in sub_path.glob("*.csv"):
            df = pd.read_csv(file)
            df["source_file"] = file.stem
            df["granularity"] = sub
            frames.append(df)

    if not frames:
        return None

    df = pd.concat(frames, ignore_index=True)

    if "start_datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["start_datetime"], errors="coerce")

    return df


def load_dataset(category: str, subfolder: str):
    path = BASE_OUTPUT / category / subfolder

    if not path.exists():
        return None

    files = list(path.glob("*.csv"))
    if not files:
        return None

    return {f.stem: pd.read_csv(f) for f in sorted(files)}


def load_single_file(category: str, filename: str):
    path = BASE_OUTPUT / category / filename

    if not path.exists():
        return None

    return pd.read_csv(path)