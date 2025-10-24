
import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Visuals – Study Hours", page_icon="📊", layout="wide")
st.title("📊 Study Hours Visuals")

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "data.csv"
JSON_PATH = BASE / "data.json"


if not JSON_PATH.exists():
    default_payload = {
        "plans": {
            "Balanced": {"Mon": 2, "Tue": 2, "Wed": 2, "Thu": 2, "Fri": 2, "Sat": 2, "Sun": 2},
            "Weekday Heavy": {"Mon": 3, "Tue": 3, "Wed": 3, "Thu": 3, "Fri": 3, "Sat": 1, "Sun": 1},
            "Weekend Warrior": {"Mon": 1, "Tue": 1, "Wed": 1, "Thu": 1, "Fri": 1, "Sat": 4, "Sun": 4}
        },
        
    }
    JSON_PATH.write_text(json.dumps(default_payload, indent=2))


if CSV_PATH.exists():
    df = pd.read_csv(CSV_PATH)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
else:
    df = pd.DataFrame(columns=["date", "hours"])

with open(JSON_PATH, "r") as f:
    targets = json.load(f)

if "date_range" not in st.session_state:
    if not df.empty:
        st.session_state.date_range = (df["date"].min().date(), df["date"].max().date())
    else:
        st.session_state.date_range = (pd.Timestamp.today().date(), pd.Timestamp.today().date())

if "selected_plan" not in st.session_state:
    st.session_state.selected_plan = "Balanced"

if "min_hours" not in st.session_state:
    st.session_state.min_hours = 0.0


with st.sidebar:
    st.header("Filters")
    if not df.empty:
        min_d, max_d = df["date"].min().date(), df["date"].max().date()
    else:
        min_d = max_d = pd.Timestamp.today().date()

    st.session_state.date_range = st.date_input("Date range", value=st.session_state.date_range, min_value=min_d, max_value=max_d)
    st.session_state.min_hours = st.number_input("Minimum hours to include", min_value=0.0, max_value=24.0, step=0.5, value=float(st.session_state.min_hours))
    st.markdown("---")
    st.session_state.selected_plan = st.selectbox("Target Plan (from JSON)", options=list(targets.get("plans", {}).keys()), index=list(targets.get("plans", {}).keys()).index(st.session_state.selected_plan) if targets.get("plans") else 0)


df_filtered = df.copy()
if not df_filtered.empty:
    start, end = st.session_state.date_range
    df_filtered = df_filtered[(df_filtered["date"].dt.date >= start) & (df_filtered["date"].dt.date <= end)]
    df_filtered = df_filtered[df_filtered["hours"] >= st.session_state.min_hours]


st.subheader("Graph 1 (Dynamic): Study Hours Over Time")

if df_filtered.empty:
    st.info("No data to show yet. Add entries on the Survey page.")
else:
    line_df = df_filtered.sort_values("date").set_index("date")[["hours"]]
    st.line_chart(line_df)
    

st.subheader("Graph 2 (Static): Average Hours by Weekday")
if df.empty:
    st.info("Need some data first.")
else:
    tmp = df.copy()
    tmp["weekday"] = tmp["date"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    avg_by_day = tmp.groupby("weekday", as_index=False)["hours"].mean()

    avg_by_day["weekday"] = pd.Categorical(avg_by_day["weekday"], categories=order, ordered=True)
    avg_by_day = avg_by_day.sort_values("weekday")
    chart_df = avg_by_day.set_index("weekday")
    st.bar_chart(chart_df)
    

st.subheader("Graph 3 (Dynamic): Weekly Targets vs Actuals")
plans = targets.get("plans", {})
if not plans:
    st.warning("No plans found in data.json. Add a 'plans' object with weekday targets.")
else:
    chosen = st.session_state.selected_plan
    target_map = plans.get(chosen, {})
  
    if df.empty:
        st.info("Add some CSV data to compare against targets.")
    else:
        df2 = df.copy()
        df2["weekday"] = df2["date"].dt.day_name()
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        actual = df2.groupby("weekday", as_index=False)["hours"].sum()
        # Normalize index to all weekdays
        actual["weekday"] = pd.Categorical(actual["weekday"], categories=order, ordered=True)
        actual = actual.set_index("weekday").reindex(order).fillna(0.0)
        actual = actual.rename(columns={"hours": "actual_hours"})

        # Targets
        targets_df = pd.DataFrame({"weekday": order, "target_hours": [float(target_map.get(day[:3] if day[:3] in target_map else day[:3].title() if False else target_map.get(day[:3], target_map.get(day, 0))) ) for day in order]})
        targets_df = targets_df.set_index("weekday")

        compare = pd.concat([actual, targets_df], axis=1).fillna(0.0)

        st.dataframe(compare)

        st.bar_chart(compare)
       

st.markdown("---")