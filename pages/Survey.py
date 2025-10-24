
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

st.set_page_config(page_title="Survey – Study Hours", page_icon="📝", layout="centered")
st.title("📝 Study Hours Survey")

DATA_PATH = Path(__file__).resolve().parent / "data.csv"


if not DATA_PATH.exists():
    df_init = pd.DataFrame(columns=["date", "hours"])
    df_init.to_csv(DATA_PATH, index=False)

if "pending_entries" not in st.session_state:
    st.session_state.pending_entries = []  

with st.form("hours_form", clear_on_submit=False):
    d = st.date_input("Date", value=date.today(), help="Pick the day you studied.")
    h = st.number_input("How many hours did you study?", min_value=0.0, max_value=24.0, step=0.5, value=1.0)
    submitted = st.form_submit_button("Add Entry")

if submitted:
    row = {"date": pd.to_datetime(d).date().isoformat(), "hours": float(h)}
    
    st.session_state.pending_entries.append(row)
    
    try:
        df = pd.read_csv(DATA_PATH)
    except Exception:
        df = pd.DataFrame(columns=["date", "hours"])
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)
    st.success(f"Saved: {row['date']} – {row['hours']} hour(s)")


if st.session_state.pending_entries:
    st.subheader("This Session's Added Entries")
    st.dataframe(pd.DataFrame(st.session_state.pending_entries))


st.subheader("All Logged Study Hours (data.csv)")
try:
    df_all = pd.read_csv(DATA_PATH)

    if not df_all.empty:
        df_all["date"] = pd.to_datetime(df_all["date"]).dt.date
    st.dataframe(df_all)
except FileNotFoundError:
    st.info("No data yet – add your first entry above!")
