import os
import time
import asyncio

from fastapi import FastAPI
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
async_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")).aio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
class Question(BaseModel):
    question : str

freq = {}

@app.get("/")
def home():
    return{"message":"application is running"}

@app.post("/ask")
async def ask_question(data:Question):
    if data.question in freq :
        return {"question":data.question,
                "answer":freq[data.question],
                "latency":0.0,
                "repeated/cached":True} 

    start = time.time()
    response = await async_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"You are a helpful assistant.Answer the following questions:{data.question}"
    )
    freq[data.question] = response.text
    latency = time.time()-start
    return {"question":data.question,
            "answer":response.text,
            "latency":round(latency,2),
            "repeated/cached":False}   