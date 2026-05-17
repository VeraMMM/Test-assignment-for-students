from dataclasses import dataclass
from typing import Callable, Dict
import pandas as pd

# R_COLUMNS = [
#         "_timestamp_local",
#         "latitude",
#         "longitude",
#         "horizontal_speed",
#         "acceleration"
#     ]
# def format_result(df: pd.DataFrame) -> pd.DataFrame:
#     return df[R_COLUMNS]

def max_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает строку_и с максимальной horizontal_speed
    """
    if df.empty:
        return df

    max_value = df["horizontal_speed"].max()
    return df[df["horizontal_speed"] == max_value]


def filter_pos_type_19(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает строки где pos_type__type == 19
    "Плохое качество позиционирования"
    """
    return df[df["pos_type__type"] == 19]


def filter_hour_between_16_19(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает строки где hour между 16 и 19 включительно (print(df["hour"].unique()) вывел 11,12,13,14)
    "Сумерки"
    """
    return df[df["hour"].between(16, 19)]


def filter_strong_negative_acceleration(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает строки где acceleration < -2
    "Резко тормозил"
    """
    return df[df["acceleration"] < -2]


def filter_geo_bounds(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает строки:
    latitude 55.5–60
    longitude 30–37.5
    "Трасса М11"
    """
    return  df[
        (df["latitude"].between(55.5, 60)) &
        (df["longitude"].between(30, 37.5))
        ]






@dataclass
class QueryEngine:
    queries: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]]

    @classmethod
    def default(cls) -> "QueryEngine":
        return cls(
            queries={
                "max_speed": max_speed,
                "pos_type_19": filter_pos_type_19,
                "hour_16_19": filter_hour_between_16_19,
                "strong_negative_acceleration": filter_strong_negative_acceleration,
                "geo_bounds": filter_geo_bounds,
            }
        )

    def run(self, query_name: str, df: pd.DataFrame) -> pd.DataFrame:
        if query_name not in self.queries:
            raise ValueError(f"Unknown query: {query_name}")
        return self.queries[query_name](df)