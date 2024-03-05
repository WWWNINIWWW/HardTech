from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import psycopg2

app = FastAPI()


conn = psycopg2.connect(
    dbname="api_hardtech",
    user="api_hardtech_user",
    password="3fFdulANPRs6jeDIqjmiBM5tlQMSJ2GC",
    host="dpg-cnhoujgl6cac7394ttag-a",
    port="5432"
)
cursor = conn.cursor()

class DataItem(BaseModel):
    username_pc: str
    data: float
    type_temperature: str
    created_at: datetime

@app.post("/data/")
async def save_data(data_item: DataItem):
    try:
        cursor.execute("INSERT INTO usernames (username_pc) VALUES (%s) ON CONFLICT (username_pc) DO NOTHING", (data_item.username_pc,))
        conn.commit()
    except psycopg2.IntegrityError:
        pass

    cursor.execute("SELECT id FROM usernames WHERE username_pc=%s", (data_item.username_pc,))
    username_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO data_items (username_id, data, type_temperature, created_at) VALUES (%s, %s, %s, %s)",
                   (username_id, data_item.data, data_item.type_temperature, data_item.created_at))
    conn.commit()
    print(f"Received data: {data_item.data} from computer with username: {data_item.username_pc}")
    return {"message": "Data received and inserted into the database"}

@app.get("/data/{username_pc}")
async def get_data_by_username(username_pc: str):
    cursor.execute("SELECT data, type_temperature, created_at FROM data_items JOIN usernames ON data_items.username_id = usernames.id WHERE usernames.username_pc=%s", (username_pc,))
    rows = cursor.fetchall()
    data = [{"temperatura": row[0], "user": username_pc, "tipo": row[1], "created_at": row[2]} for row in rows]
    return {"data": data}

@app.get("/temperature/{username_pc}", response_model=dict[str, Any])
async def get_average_temperature(username_pc: str):
    with sqlite3.connect('example.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usernames WHERE username_pc=?", (username_pc,))
        user_id = cursor.fetchone()
        if not user_id:
            return {"message": "User not found"}

        cursor.execute("SELECT data, type_temperature, created_at FROM data_items WHERE username_id=?", (user_id[0],))
        rows = cursor.fetchall()

        daily_data = {}
        for row in rows:
            created_at = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            date_key = created_at.strftime("%Y-%m-%d")
            if date_key not in daily_data:
                daily_data[date_key] = {"total_temperature": 0, "temperature_count": 0, "date": date_key}
            daily_data[date_key]["total_temperature"] += row[0]
            daily_data[date_key]["temperature_count"] += 1

        average_temperatures = {}
        for date_key, data in daily_data.items():
            average_temperatures[date_key] = {
                "average_temperature": round(data["total_temperature"] / data["temperature_count"], 2),
                "temperature_count": data["temperature_count"],
                "date": data["date"]
            }

        return {"user": username_pc, "average_temperatures": average_temperatures}



@app.get("/usernames/")
async def get_all_usernames():
    cursor.execute("SELECT username_pc FROM usernames")
    rows = cursor.fetchall()
    usernames = [row[0] for row in rows]
    return {"usernames": usernames}
