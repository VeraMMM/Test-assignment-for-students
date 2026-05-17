from pathlib import Path
import pandas as pd



REQUIRED_COLUMNS = [
    "_timestamp",
    "north_velocity",
    "east_velocity",
    "latitude",
    "longitude",
    "pos_type__type",
]

def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
        Тут мы загружаем файл, проверяем существует ли он, что он не пустой,
         что нужным колонки на месте, приводим типы данных и сорт по времени.
         Пока просто utc=True, потом будет +3.
         _timestamp уже datetime
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("CSV file is empty")

    _validate_columns(df)

    df = _prepare_types(df)
    df = _sort_by_timestamp(df)
    return df


def _validate_columns(df: pd.DataFrame) -> None:

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _prepare_types(df: pd.DataFrame) -> pd.DataFrame:

    df["_timestamp"] = pd.to_datetime(df["_timestamp"], utc=True)
    df["north_velocity"] = df["north_velocity"].astype(float)
    df["east_velocity"] = df["east_velocity"].astype(float)

    return df

def _sort_by_timestamp(df: pd.DataFrame) -> pd.DataFrame:

    return df.sort_values("_timestamp").reset_index(drop=True)