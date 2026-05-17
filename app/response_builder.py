import pandas as pd


def build_response(action: str, result_df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    """
    Преобразует результат QueryEngine в финальный JSON-ответ.
    """
    if action == "unknown":
        return {
            "type": "unknown",
            "message": "Query is not related to GNSS data analysis"
        }
    if result_df is None or result_df.empty:
        return {
            "type": action,
            "result": None,
            "message": "No data found"
        }

    builder_map = {
        "max_speed": _build_max_speed,
        "pos_type_19": _build_gps_problems,
        "hour_16_19": _build_time_interval,
        "strong_negative_acceleration": _build_braking_events,
        "geo_bounds": _build_geo_points,
    }

    builder = builder_map.get(action)

    if not builder:
        raise ValueError(f"Unknown action for response builder: {action}")

    return builder(result_df, full_df)


def _build_max_speed(result_df: pd.DataFrame, full_df: pd.DataFrame):

    row = result_df.iloc[0]

    return {
        "max_speed": round(row["horizontal_speed"] * 3.6, 2),
        "units": "km/h",
        "timestamp": row["_timestamp_local"],
        "latitude": row["latitude"],
        "longitude": row["longitude"]
    }


def _build_gps_problems(df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    total = len(df)
    total_all = len(full_df)

    percentage = round((total / total_all) * 100, 2) if total_all else 0

    points = df.head(50)[[
        "_timestamp_local",
        "latitude",
        "longitude",
        "horizontal_speed"
    ]].copy()

    points["horizontal_speed"] = (points["horizontal_speed"] * 3.6).round(2)

    return {
        "total_points": total,
        "percentage_of_trip": percentage,
        "points": points.to_dict(orient="records")
    }


def _build_time_interval(df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    points = df.head(50)[[
        "_timestamp_local",
        "latitude",
        "longitude"
    ]]

    return {
        "total_points": len(df),
        "interval": "16-19",
        "points": points.to_dict(orient="records")
    }


def _build_braking_events(df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_braking_events": 0,
            "events": []
        }

    total = len(df)
    max_dec = round(df["acceleration"].min(), 2)
    avg_dec = round(df["acceleration"].mean(), 2)

    events = df.head(50)[[
        "_timestamp_local",
        "latitude",
        "longitude",
        "acceleration",
        "horizontal_speed"
    ]].copy()

    events["horizontal_speed"] = (events["horizontal_speed"] * 3.6).round(2)
    events["acceleration"] = events["acceleration"].round(2)

    return {
        "total_braking_events": total,
        "max_deceleration": max_dec,
        "avg_deceleration": avg_dec,
        "events": events.to_dict(orient="records")
    }


def _build_geo_points(df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    points = df.head(50)[[
        "_timestamp_local",
        "latitude",
        "longitude",
        "horizontal_speed"
    ]].copy()

    points["horizontal_speed"] = (points["horizontal_speed"] * 3.6).round(2)

    return {
        "total_points": len(df),
        "points": points.to_dict(orient="records")
    }
