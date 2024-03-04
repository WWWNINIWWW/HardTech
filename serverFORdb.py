import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import psycopg2
from datetime import datetime

app = FastAPI()

DATABASE_URL = "postgres://api_hardtech_user:3fFdulANPRs6jeDIqjmiBM5tlQMSJ2GC@dpg-cnhoujgl6cac7394ttag-a/api_hardtech"
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS usernames
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username_pc TEXT UNIQUE)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS data_items
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username_id INTEGER, data REAL, type_temperature TEXT, created_at TEXT,
             FOREIGN KEY(username_id) REFERENCES usernames(id))''')
conn.commit()

class DataItem(BaseModel):
    username_pc: str
    data: float
    type_temperature: str
    created_at: datetime = Field(default_factory=datetime.now)

@app.post("/data/")
async def save_data(data_item: DataItem):
    username_pc = data_item.username_pc
    data = data_item.data
    type_temperature = data_item.type_temperature
    created_at = datetime.now()

    cursor.execute("INSERT OR IGNORE INTO usernames (username_pc) VALUES (?)", (username_pc,))
    conn.commit()

    cursor.execute("SELECT id FROM usernames WHERE username_pc=?", (username_pc,))
    username_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO data_items (username_id, data, type_temperature, created_at) VALUES (?, ?, ?, ?)", (username_id, data, type_temperature, created_at))
    conn.commit()

    print(f"Received data: {data} from computer with username: {username_pc}")
    return {"message": "Data received and inserted into the database"}

@app.get("/data/{username_pc}", response_model=List[DataItem])
async def get_data_by_username(username_pc: str):
    cursor.execute("SELECT data, type_temperature, created_at FROM data_items JOIN usernames ON data_items.username_id = usernames.id WHERE usernames.username_pc=?", (username_pc,))
    rows = cursor.fetchall()
    return [{"data": row[0], "username_pc": username_pc, "type_temperature": row[1], "created_at": row[2]} for row in rows]


@app.get("/temperature/{username_pc}")
async def get_average_temperature(username_pc: str):
    cursor.execute("SELECT data, created_at FROM data_items JOIN usernames ON data_items.username_id = usernames.id WHERE usernames.username_pc=?", (username_pc,))
    rows = cursor.fetchall()

    temperatures_by_day = {}
    for row in rows:
        temperature = float(row[0])
        created_at = row[1]
        day = created_at.split(' ')[0] 
        if day in temperatures_by_day:
            temperatures_by_day[day].append(temperature)
        else:
            temperatures_by_day[day] = [temperature]

    average_temperatures = {}
    for day, temps in temperatures_by_day.items():
        average_temperature = sum(temps) / len(temps) if temps else 0
        average_temperatures[day] = {
            "average_temperature": round(average_temperature, 2),
            "temperature_count": len(temps),
            "date": day
        }

    return {"user": username_pc, "average_temperatures": average_temperatures}


@app.get("/usernames/", response_model=List[str])
async def get_all_usernames():
    cursor.execute("SELECT username_pc FROM usernames")
    rows = cursor.fetchall()
    return [row[0] for row in rows]
