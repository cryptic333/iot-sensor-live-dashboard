import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Smart Machine Live Sensor Monitoring")

DB = "sensors.db"

# LOAD DATA
def load_data(n=1000):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(
        f"SELECT * FROM readings ORDER BY ts DESC LIMIT {n}", conn
    )
    conn.close()

    df["ts"] = pd.to_datetime(df["ts"])
    df = df.sort_values("ts")
    return df

df = load_data()

if df.empty:
    st.warning("No sensor data found. Please run simulate_sensor.py.")
    st.stop()

#  MACHINE SELECTOR
machines = df["machine"].unique()
selected_machine = st.selectbox("Select Machine", machines)

df = df[df["machine"] == selected_machine]

# ROLLING STATS
window = 30
df["rolling_mean"] = df["vibration"].rolling(window).mean()
df["rolling_std"] = df["vibration"].rolling(window).std()

df["upper_limit"] = df["rolling_mean"] + 3 * df["rolling_std"]
df["lower_limit"] = df["rolling_mean"] - 3 * df["rolling_std"]

df["anomaly"] = df["vibration"] > df["upper_limit"]

# METRICS
latest_temp = df["temp"].iloc[-1]
latest_vibration = df["vibration"].iloc[-1]
anomaly_count = df["anomaly"].sum()

health_score = max(0, 100 - anomaly_count)

c1, c2, c3 = st.columns(3)
c1.metric("Latest Temperature (°C)", f"{latest_temp:.2f}")
c2.metric("Latest Vibration", f"{latest_vibration:.2f}")
c3.metric("Health Score", f"{health_score}")

st.divider()

# VIBRATION TREND
st.subheader("Vibration Trend with Control Limits")

fig1, ax1 = plt.subplots(figsize=(8,3))

ax1.plot(df["ts"], df["vibration"], label="Vibration")
ax1.plot(df["ts"], df["rolling_mean"], linestyle="--", label="Rolling Mean")
ax1.plot(df["ts"], df["upper_limit"], linestyle=":", label="Upper Limit")
ax1.plot(df["ts"], df["lower_limit"], linestyle=":", label="Lower Limit")

anomalies = df[df["anomaly"]]
ax1.scatter(anomalies["ts"], anomalies["vibration"])

ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
ax1.xaxis.set_major_locator(mdates.AutoDateLocator())

plt.xticks(rotation=45)
plt.tight_layout()
ax1.legend()

st.pyplot(fig1)

# TEMPERATURE TREND
st.subheader("Temperature Trend")

fig2, ax2 = plt.subplots(figsize=(8,3))
ax2.plot(df["ts"], df["temp"])
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig2)

# RELATIONSHIP SCATTER
st.subheader("Temperature vs Vibration")

fig3, ax3 = plt.subplots(figsize=(5,3))
ax3.scatter(df["temp"], df["vibration"])
ax3.set_xlabel("Temperature (°C)")
ax3.set_ylabel("Vibration")
plt.tight_layout()

st.pyplot(fig3)

# DISTRIBUTION
st.subheader("Vibration Distribution")

fig4, ax4 = plt.subplots(figsize=(5,3))
ax4.hist(df["vibration"], bins=25)
ax4.set_xlabel("Vibration")
plt.tight_layout()

st.pyplot(fig4)

# ANOMALY TABLE
st.subheader("Recent Anomalies")

anomaly_table = df[df["anomaly"]][["ts", "temp", "vibration"]].copy()
anomaly_table["timestamp"] = anomaly_table["ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
anomaly_table = anomaly_table.drop(columns=["ts"])

st.dataframe(anomaly_table.tail(20))

# RAW DATA OPTION
with st.expander("View Raw Sensor Data"):
    st.dataframe(df.tail(50))
