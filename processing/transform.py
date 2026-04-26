# ---- Imports ---- #
import pandas as pd

# ---- Transformation Module ---- #
def to_dataframe(data: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    return df