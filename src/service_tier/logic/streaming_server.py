"""
Podcast Streaming Server

This module implements a FastAPI server that provides real-time streaming of podcast audio
when a user clicks to listen. It uses WebSockets for real-time communication and
generates audio on-demand using OpenAI's TTS API.
"""

import os
import asyncio
import json
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
import psycopg2 


# Add the parent directory to the Python module search path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
load_dotenv()

# Import your existing modules
from logic.pulse_output import PulseOutput
import common.sqs
import common.s3

# Initialize FastAPI app
app = FastAPI(title="Podcast Streaming Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure API keys
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Temporary directory for audio files
TEMP_BASE = "/tmp"

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Initialize models
summary_model = genai.GenerativeModel('gemini-1.5-flash')
script_model = genai.GenerativeModel('gemini-2.0-flash')

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_audio_chunk(self, chunk: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(chunk)

    async def send_text(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


def update_db(user_id, episode_title, email_description, episode_number, episode_type, mp3_file_url):
    try:
        conn = psycopg2.connect(dsn=db_access_url)
        cursor = conn.cursor()

        articles_list = [{
            'title': row['title'],
            'description': row['description'],
            'url': row['url']
        } for _, row in email_description.iterrows()]

        cursor.execute("""
            INSERT INTO podcasts (title, user_id, articles, episode_number, episode_type, audio_file_url, date, completed)
            VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s)
            RETURNING id
        """, (episode_title, user_id, json.dumps(articles_list), episode_number, episode_type, mp3_file_url, datetime.now(), False))
        
        podcast_id = cursor.fetchone()[0]

        # Update user's podcast array with the new podcast id
        cursor.execute("""
            UPDATE users 
            SET episode = episode + 1,
                delivered = %s
            WHERE id = %s
        """, (datetime.now(), user_id))

        conn.commit()
        print(f"Successfully updated podcast and user tables for user {user_id}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.websocket("/ws/podcast")
async def stream_podcast(websocket: WebSocket):
    await websocket.accept()
    try:
        print("CONNECTED")
        
        # Wait for the client to send the user ID and script
        data = await websocket.receive_json()
        
        # Extract user ID and script from the received data
        user_id = data.get("user_id")
        turns = data.get("script")
        
        if not user_id or not turns:
            await websocket.send_json({"type": "error", "content": "Missing user_id or script"})
            return
            
        print(f"Received request from user: {user_id}")
        
        if not turns:
            await websocket.send_json({"type": "error", "content": "Invalid script"})
            return

        client = OpenAI(api_key=OPENAI_API_KEY)

        for index, sentence in enumerate(turns):
            host = 1 if index % 2 == 0 else 2
            voice = 'nova' if host == 1 else 'onyx'

            # Send transcript
            await websocket.send_json({
                "type": "transcript",
                "turn": index,
                "host": host,
                "text": sentence
            })

            # Generate and stream audio
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=sentence,
                    response_format='mp3'
                )

                # Use regular for loop with iter_bytes()
                for chunk in response.iter_bytes(chunk_size=4096):
                    await websocket.send_bytes(chunk)
                    await asyncio.sleep(0.01)  # Small delay to prevent overwhelming

            except Exception as e:
                print(f"Error in turn {index}: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "turn": index,
                    "message": str(e)
                })
                break

        await websocket.send_json({"type": "complete"})

    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        await websocket.close()

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
