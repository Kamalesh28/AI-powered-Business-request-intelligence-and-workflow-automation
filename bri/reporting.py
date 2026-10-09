from __future__ import annotations

import pandas as pd


def to_frame(rows: list[dict]) -> pd.DataFrame:
    columns = ["request_id", "department", "status", "submitted_at_utc", "is_synthetic", "processing_mode", "proposed_category", "proposed_priority", "reviewed", "corrected"]
    frame = pd.DataFrame(rows, columns=columns)
    if not frame.empty:
        frame["submitted_at_utc"] = pd.to_datetime(frame["submitted_at_utc"], utc=True)
    return frame


def kpis(frame: pd.DataFrame) -> dict[str, float | int]:
    requests = len(frame)
    reviewed = int(frame["reviewed"].sum()) if requests else 0
    corrected = int(frame["corrected"].sum()) if requests else 0
    return {
        "requests": requests,
        "review_rate": reviewed / requests if requests else 0.0,
        "correction_rate": corrected / reviewed if reviewed else 0.0,
    }


def distributions(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if frame.empty:
        empty = pd.DataFrame(columns=["label", "count"])
        return {"category": empty, "priority": empty, "mode": empty, "trend": pd.DataFrame(columns=["date", "count"])}
    def counts(column: str) -> pd.DataFrame:
        return frame[column].fillna("Unclassified").value_counts().rename_axis("label").reset_index(name="count")
    trend = frame.assign(date=frame["submitted_at_utc"].dt.date.astype(str)).groupby("date").size().reset_index(name="count")
    return {"category": counts("proposed_category"), "priority": counts("proposed_priority"), "mode": counts("processing_mode"), "trend": trend}
