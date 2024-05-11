from fastapi import FastAPI, HTTPException
import asyncpg

app = FastAPI()

# PostgreSQL database credentials
POSTGRES_USER = 'your-postgres-user'
POSTGRES_PASSWORD = 'your-postgres-password'
POSTGRES_DB = 'your-postgres-db'
POSTGRES_HOST = 'your-postgres-host'

# Connection URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

# Connect to the PostgreSQL database
async def connect_to_db():
    return await asyncpg.connect(DATABASE_URL)


@app.get("/data")
async def get_data():
    try:
        # Connect to the database
        conn = await connect_to_db()
        
        # Execute a query to retrieve data (example query)
        query = "SELECT * FROM your_table"
        result = await conn.fetch(query)
        
        # Close the database connection
        await conn.close()
        
        # Return the data as JSON
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
