import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

DB = "sensors.db"

st.set_page_config(page_title="Live Sensor Monitor", layout="wide")
st.title("📡 Live Sensor Monitor (Demo)")

def load_latest(n=300):
    con = sqlite3.connect(DB)
    df = pd.read_sql_query(f"""
        SELECT * FROM readings
        ORDER BY ts DESC
        LIMIT {n}
    """, con)
    con.close()
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.sort_values("ts")
    return df

df = load_latest()

# Simple anomaly flag using rolling mean + std
window = 30
df["vib_mean"] = df["vibration"].rolling(window).mean()
df["vib_std"] = df["vibration"].rolling(window).std()
df["anomaly"] = (df["vibration"] > (df["vib_mean"] + 3 * df["vib_std"])).fillna(False)

c1, c2, c3 = st.columns(3)
c1.metric("Latest Temp", f"{df['temp'].iloc[-1]:.2f} °C")
c2.metric("Latest Vibration", f"{df['vibration'].iloc[-1]:.2f}")
c3.metric("Anomalies (last 300)", f"{int(df['anomaly'].sum())}")

left, right = st.columns(2)

with left:
    st.subheader("Temperature (last 300 seconds)")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(df["ts"], df["temp"])
    ax.set_ylabel("°C")
    st.pyplot(fig)

with right:
    st.subheader("Vibration + Anomaly Flags")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    ax2.plot(df["ts"], df["vibration"])
    # mark anomalies
    an = df[df["anomaly"]]
    ax2.scatter(an["ts"], an["vibration"])
    ax2.set_ylabel("vibration")
    st.pyplot(fig2)

st.divider()
st.subheader("Recent rows")
st.dataframe(df.tail(50))

st.caption("Tip: refresh the page every few seconds to see new readings.")
