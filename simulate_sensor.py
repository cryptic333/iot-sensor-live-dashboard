import sqlite3
import time
import random
from datetime import datetime, UTC

DB = "sensors.db"

def setup():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            ts TEXT,
            machine TEXT,
            temp REAL,
            vibration REAL
        )
    """)
    con.commit()
    con.close()

def insert_reading(machine, temp, vibration):
    con = sqlite3.connect(DB)
    cur = con.cursor()

    timestamp = datetime.now(UTC).isoformat()

    cur.execute(
        "INSERT INTO readings VALUES (?, ?, ?, ?)",
        (timestamp, machine, temp, vibration)
    )
    con.commit()
    con.close()

setup()

machine = "CUT_1"
temp = 55.0
vib = 2.0

print("✅ Writing sensor data to sensors.db (Ctrl+C to stop)")

while True:
    # small random walk
    temp += random.uniform(-0.2, 0.2)
    vib += random.uniform(-0.05, 0.05)

    # sometimes inject an anomaly
    if random.random() < 0.01:
        vib += random.uniform(1.5, 3.0)

    insert_reading(machine, temp, vib)
    time.sleep(1)
