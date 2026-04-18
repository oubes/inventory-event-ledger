import pandas as pd

def to_dataframe(data: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    return df