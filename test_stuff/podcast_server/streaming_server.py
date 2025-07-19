"""
Podcast Streaming Server

This module implements a FastAPI server that provides real-time streaming of podcast audio
when a user clicks to listen. It uses WebSockets for real-time communication and
generates audio on-demand using OpenAI's TTS API.
"""

import os
import asyncio
import time
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from openai import OpenAI
import psycopg2 

import s3
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

db_access_url = os.environ.get('DB_ACCESS_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Temporary directory for audio files
TEMP_BASE = "/tmp"

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

def update_db(mp3_file_url, podcast_id):
    try:
        conn = psycopg2.connect(dsn=db_access_url)
        cursor = conn.cursor()

        if podcast_id:
            # Update existing podcast with the mp3_file_url
            cursor.execute("""
                UPDATE podcasts 
                SET audio_file_url = %s
                WHERE id = %s
            """, (mp3_file_url, podcast_id))
            
            conn.commit()
            print(f"Successfully updated audio_file_url for podcast {podcast_id}")
            return podcast_id

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
        podcast_id = data.get("podcast_id")
        episode = data.get("episode")
        turns = data.get("script")
        
        if not podcast_id or not turns:
            await websocket.send_json({"type": "error", "content": "Require user_id, script, episode, podcast_id"})
            return
        start_time = time.time()
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create a temporary file to store the full MP3
        temp_mp3_path = os.path.join(TEMP_BASE, f"podcast.mp3")
        full_audio_bytes = bytearray()
        connection_active = True
        current_turn_index = 0

        # Process all turns
        while current_turn_index < len(turns):
            sentence = turns[current_turn_index]
            host = 1 if current_turn_index % 2 == 0 else 2
            voice = 'nova' if host == 1 else 'onyx'

            # Generate and stream audio
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=sentence,
                    response_format='mp3'
                )
                print(f"Turn {current_turn_index} processed")

                # Collect all audio bytes
                audio_bytes = bytearray()
                
                # Use regular for loop with iter_bytes()
                for chunk in response.iter_bytes(chunk_size=16384):
                    audio_bytes.extend(chunk)
                    
                    # Only send to client if connection is still active
                    if connection_active:
                        try:
                            await websocket.send_bytes(chunk)
                            await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
                        except Exception as e:
                            print(f"Failed to send audio chunk: {str(e)}")
                            connection_active = False
                
                # Add to the full audio bytes regardless of connection status
                full_audio_bytes.extend(audio_bytes)
                
                # Move to the next turn
                current_turn_index += 1

            except Exception as e:
                print(f"Error in turn {current_turn_index}: {str(e)}")
                if connection_active:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "turn": current_turn_index,
                            "message": str(e)
                        })
                    except:
                        connection_active = False
                # Still increment the turn index to continue with the next turn
                current_turn_index += 1

        print(f"Completed. Total time taken: {time.time() - start_time} seconds")
        # Only send completion message if connection is still active
        if connection_active:
            try:
                await websocket.send_json({"type": "complete"})
            except:
                print("Failed to send completion message")

        # Streaming done, save to database
        try:
            # Save the full audio bytes to a temporary file
            with open(temp_mp3_path, 'wb') as f:
                f.write(full_audio_bytes)
            print(f"Saved podcast to {temp_mp3_path}")
            

            s3.save(user_id, episode, 'PODCAST', temp_mp3_path)

            s3_url = s3.get_s3_url(user_id, episode, "PODCAST")
            # Update the database with the MP3 file URL
            update_db(s3_url, podcast_id)
            print(f"Saved full podcast MP3 to database for podcast {podcast_id}")
        except Exception as e:
            print(f"Error saving podcast to database: {str(e)}")

    except WebSocketDisconnect:
        print("Client disconnected normally")
        # Continue processing the script even after client disconnects
        connection_active = False
        
        # Process the remaining turns
        while current_turn_index < len(turns):
            sentence = turns[current_turn_index]
            host = 1 if current_turn_index % 2 == 0 else 2
            voice = 'nova' if host == 1 else 'onyx'

            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=sentence,
                    response_format='mp3'
                )
                print(f"Turn {current_turn_index} processed after disconnect")

                # Collect all audio bytes
                audio_bytes = bytearray()
                
                # Use regular for loop with iter_bytes()
                for chunk in response.iter_bytes(chunk_size=4096):
                    audio_bytes.extend(chunk)
                
                # Add to the full audio bytes
                full_audio_bytes.extend(audio_bytes)
                
                # Move to the next turn
                current_turn_index += 1

            except Exception as e:
                print(f"Error in turn {current_turn_index} after disconnect: {str(e)}")
                # Still increment the turn index to continue with the next turn
                current_turn_index += 1
        
        print(f"Completed after disconnect. Total time taken: {time.time() - start_time} seconds")
        # Save the full MP3 to the database after processing all turns
        try:
            # Save the full audio bytes to a temporary file
            with open(temp_mp3_path, 'wb') as f:
                f.write(full_audio_bytes)
            print(f"Saved podcast to {temp_mp3_path}")
            

            s3.save(user_id, episode, 'PODCAST', temp_mp3_path)

            s3_url = s3.get_s3_url(user_id, episode, "PODCAST")
            # Update the database with the MP3 file URL
            update_db(s3_url, podcast_id)
            
            print(f"Saved full podcast MP3 to database after disconnect for podcast {podcast_id}")
        except Exception as e:
            print(f"Error saving podcast to database after disconnect: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        await websocket.close()

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn streaming_server:app
