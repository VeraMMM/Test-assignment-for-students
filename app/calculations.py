import numpy as np
import pandas as pd


def add_horizontal_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    # Горизонтальная скорость (м/с)
    horizontal_speed = sqrt(north_velocity² + east_velocity²)
    """

    df["horizontal_speed"] = np.sqrt(
        df["north_velocity"] ** 2 + df["east_velocity"] ** 2
    )
    return df


def add_acceleration(df: pd.DataFrame) -> pd.DataFrame:
    """
    # Ускорение (м/с²) — производная скорости по времени
    acceleration = diff(horizontal_speed) / diff(timestamp)
    a = delta_u/delta_t
    """

    delta_time = df["_timestamp"].diff().dt.total_seconds() # sec
    delta_speed = df["horizontal_speed"].diff()
    df["acceleration"] = delta_speed / delta_time
    df["acceleration"] = df["acceleration"].fillna(0)
    return df


def add_hour_utc_plus_3(df: pd.DataFrame) -> pd.DataFrame:
    """
    Добавляет колонку hour с учетом UTC+3, не просто сдвиг
    """

    df["_timestamp_local"] = df["_timestamp"].dt.tz_convert("Europe/Moscow")
    df["hour"] = df["_timestamp_local"].dt.hour

    return df


def process_gnss_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Салон веселый причесончик
    """

    df = add_horizontal_speed(df)
    df = add_acceleration(df)
    df = add_hour_utc_plus_3(df)

    return df