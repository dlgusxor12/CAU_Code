from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

from fastapi import FastAPI

app = FastAPI(
    title="Cau Code Backend Service",
    description="Backend service for Cau Code platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Cau Code Backend Service is running."}

