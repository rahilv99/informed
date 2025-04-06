"""
Podcast Streaming Server

This module implements a FastAPI server that provides real-time streaming of podcast audio
when a user clicks to listen. It uses WebSockets for real-time communication and
generates audio on-demand using OpenAI's TTS API.
"""

import os
import re
import asyncio
import json
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from openai import OpenAI
import io
from pydub import AudioSegment

# Import your existing modules
# Assuming these are available in your environment
# from logic.pulse_output import PulseOutput
# import common.sqs
# import common.s3

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
GOOGLE_API_KEY = 'AIzaSyAVXbH_jtqfbzKrL3vwmdxvgMylijtkOjs'
OPENAI_API_KEY = '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'

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Initialize models
summary_model = genai.GenerativeModel('gemini-1.5-flash')
script_model = genai.GenerativeModel('gemini-2.0-flash')

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, podcast_id: str):
        await websocket.accept()
        if podcast_id not in self.active_connections:
            self.active_connections[podcast_id] = []
        self.active_connections[podcast_id].append(websocket)

    def disconnect(self, websocket: WebSocket, podcast_id: str):
        if podcast_id in self.active_connections:
            if websocket in self.active_connections[podcast_id]:
                self.active_connections[podcast_id].remove(websocket)
            if not self.active_connections[podcast_id]:
                del self.active_connections[podcast_id]

    async def send_audio_chunk(self, chunk: bytes, podcast_id: str):
        if podcast_id in self.active_connections:
            for connection in self.active_connections[podcast_id]:
                await connection.send_bytes(chunk)

manager = ConnectionManager()

# Models
class PodcastRequest(BaseModel):
    user_id: str
    episode: str
    plan: str = "free"

class PodcastMetadata(BaseModel):
    user_id: str
    episode: str
    title: str
    description: str
    duration: Optional[int] = None

# Database simulation
# In a real implementation, this would be replaced with a proper database
podcast_scripts = {}
podcast_metadata = {}

# Helper functions from your original code
def clean_text_for_conversational_tts(input_text):
    """
    Cleans text for Text-to-Speech by:
    - Replacing '\n' with spaces.
    - Removing Markdown-style formatting like '**bold**'.
    """
    # Match and extract statements for both HOST 1 and HOST 2.
    pattern = r"HOST [12]([^\n]+)"
    statements = re.findall(pattern, input_text)

    output_text = []
    for statement in statements:
        # Remove :
        statement = statement.replace(':', '')
        # Replace '\n' with a space
        statement = statement.replace('\n', ' ')
        # remove '& 1' or '& 2'
        statement = re.sub(r'& \d', '', statement)
        # Remove Markdown-style (*)
        statement = re.sub(r'\*\*\:', '', statement)
        statement = re.sub(r'\*', '', statement)
        # Ensure no extra spaces
        statement = re.sub(r'\s+', ' ', statement).strip()
        
        if statement != '':
          output_text.append(statement)

    return output_text

def summarize(title, text, use='summary'):
    if use == 'title':
        prompt = f"Create a title for the podcast based on the title of the academic articles discussed. The title should be attention-grabbing, professional, and informative.\
                    Only include the generated title itself; avoid any introductions, explanations, or meta-comments. This generated title will be in an email newsletter.\
            Titles: {text}"
    else:  # email header case
        prompt = f"Provide a succinct TLDR summary about the academic article titled '{title}'.\
            Highlight the key details that help the user decide whether the source is worth reading. Only include the summary itself;\
            avoid any introductions, explanations, or meta-comments. This summary will be in an email newsletter. Make the summary attention-grabbing and informative.\
            Keep it less than 100 tokens.\
            Text: {text}"
    
    response = summary_model.generate_content(prompt,
                                            generation_config=genai.GenerationConfig(
                                                max_output_tokens=100,
                                                temperature=0.25))
    return response.text

def academic_segment(text, title, plan='free'):
    if plan == 'free':
        tokens = 150
    else:  # premium
        tokens = 200

    system_prompt = f"""
        You are a professional podcast script writer for "Auxiom," a podcast that breaks down complex government documents from the last week. Your task is to write a single, engaging segment of a script for a text-to-speech model. This segment will feature a dialogue between **HOST 1** and **HOST 2**, discussing the key takeaways from the provided document.

        **FORMAT:**

        * Mark each conversational turn with **HOST 1** or **HOST 2**.
        * This is an intermediate segment. Do not include introductions, summaries, or meta-comments. Jump directly into the dialogue.
        * Focus on extracting and explaining the core information from the document.

        **EXTRACT FROM TEXT:**

        * Identify and discuss key decisions made.
        * Present and explain opinions expressed by specific individuals.
        * Analyze and explain the potential implications of the document's contents.
        * Be sure to include any metrics like money or deadlines.
        * Limit repeated thoughts

        **SPEECH TIPS:**

        * Hosts are charismatic, professional, and genuinely interested in the topic.
        * Use short, clear sentences suitable for text-to-speech. Avoid complex phrasing, jargon, and acronyms (unless absolutely necessary and explained).
        * Aim for a natural, dynamic conversational flow.
        * Incorporate filler words ("uh," "like," "you know") and occasional repetitions for a more human-like sound.
        * Prioritize clarity and accessibility. Imagine you are explaining this to someone with little prior knowledge of the subject.
        * Clearly attribute opinions to specific individuals.
        * Explain the potential impact of decisions made in the document.
        * Create a dynamic range of responses.

        **Example:**

        **HOST 1:** Another bill came up this week discussing...
        **HOST 2:** I read that Senator Jones said a lot about...
        **HOST 1:** Right, I mean he is a big proponent of ... 
        **HOST 2:** Sounds like it will be a big step for ...
        **HOST 1:** - This impacts all the countries in ...

        Remember: This segment must be exactly {tokens} tokens long. Produce approximately {tokens} tokens.

        Article: {title}
        Text: {text}"""

    response = script_model.generate_content(system_prompt,
                                          generation_config=genai.GenerationConfig(
                                              max_output_tokens=tokens*2,
                                              temperature=0.3))
    return response.text

def review_script(script, tokens):
    prompt = f"Review the script for the podcast episode, for input to a text-to-speech model. Refine any wording that may be difficult for a text-to-speech model.\
              Make sure the content flows well and is engaging. Ensure the structure is marked with **HOST 1** and **HOST 2** at each conversational turn. \
              Remove or replace acronyms where necessary. Delete quotation marks. Do not add any unecessary phrases; this will be fed directly to a text-to-speech model.\
        Script: {script}"

    response = script_model.generate_content(prompt, generation_config=genai.GenerationConfig(
                                        max_output_tokens=tokens*2,
                                        temperature=0.10))
    return response.text

def make_script(texts, titles, name, plan='free'):
    if plan == 'plus':
        tokens = 1500
    else:  # free
        tokens = 900
        texts = texts[:3]

    segments = []
    for i in range(len(texts)):
        segments.append(academic_segment(texts[i], titles[i], plan))
    
    print('Processed ', len(segments), ' articles')
    
    system_prompt = f"""
    You are a senior editor for a podcast "Auxiom," a podcast that breaks down complex government documents from the last week. Your task is to take the segments written by other agents, refine their content, and merge them into a consistent flow.
    INPUT
    - Your agents have written multiple segments, with 1 document discussed in each
    - The scripts should be marked with **HOST 1** and **HOST 2** for each conversational turn
    - Make the output conversation {tokens} tokens long.
    TASK
    - Merge the components, ensure the format is consistent (as above)
    - Refine the content to be more engaging
    - Allow each segment and equal amount of time
    - CLOSE WITH: 'Thanks for listening, stay tuned for more episodes.'
    SPEECH TIPS
    - Since this is for a text-to-speech model, use short sentences, omit any non-verbal cues, complex sentences/phrases, or acronyms.
    
    Example: 
    **HOST 1**: Welcome back to Auxiom! This past week there has been ...
    **HOST 2 **: That's right. Recently a bill came up for...
    **HOST 1:** I read that Senator Jones said a lot about...
    **HOST 2:** Right, I mean he is a big proponent of ... 
    **HOST 1:** Sounds like it will be a big step for ...
    **HOST 2:** - This impacts all the countries in ...
    ...
    **HOST 1**: Moving on, there is a new executive order/congressional hearing/bill/court case/etc...
    ...
    **HOST 2**: I'm glad you mention that. There's another executive order/congressional hearing/bill/court case/etc...
    ...
    **HOST 1**: We hope you have a great day, stay tuned for more episodes.

    Remember: This segment must be exactly {tokens} tokens long. Produce approximately {tokens} tokens.

Articles: """
    for i in range(len(segments)):
        system_prompt += f" Article {i} - {titles[i]}: {segments[i]}"     
       
    response = script_model.generate_content(system_prompt, 
                                      generation_config=genai.GenerationConfig(
                                        max_output_tokens=tokens*2,
                                        temperature=0.25))
    
    ret = review_script(response.text, tokens)

    return ret

def generate_script(all_data, name, plan='free'):
    # Generate script
    texts = all_data['text'].tolist()
    titles = all_data['title'].tolist()
    script = make_script(texts, titles, name, plan)
    return script

def generate_email_headers(all_data):
    def _clean_summary_text(text):
        text = re.sub(r'\*', '', text)
        return re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\\', '')).strip()

    podcast_description = all_data[['title', 'url', 'text']].copy()

    # Ensure this remains a DataFrame
    podcast_description['description'] = podcast_description.apply(
        lambda row: _clean_summary_text(summarize(row['title'], row['text'], use='email')),
        axis=1
    )
    
    titles = podcast_description['title'].tolist()
    titles = ", ".join(titles)
    episode_title = summarize("", titles, use='title')
    episode_title = _clean_summary_text(episode_title)

    return podcast_description, episode_title

# API Endpoints
@app.post("/api/podcasts/generate")
async def generate_podcast(request: PodcastRequest):
    """
    Generate a podcast script and store it for later streaming.
    This endpoint doesn't generate audio yet, just prepares the script.
    """
    try:
        # In a real implementation, you would retrieve data from your database
        # For now, we'll create dummy data
        all_data = pd.DataFrame({
            'title': ['Sample Article 1', 'Sample Article 2', 'Sample Article 3'],
            'url': ['http://example.com/1', 'http://example.com/2', 'http://example.com/3'],
            'text': [
                'This is sample text for article 1. It contains important information.',
                'This is sample text for article 2. It discusses key findings.',
                'This is sample text for article 3. It presents conclusions and recommendations.'
            ]
        })
        
        if request.plan == 'free':
            all_data = all_data.head(3)
        
        # Generate script
        script = generate_script(all_data, "User", plan=request.plan)
        
        # Store script for later streaming
        podcast_id = f"{request.user_id}_{request.episode}"
        podcast_scripts[podcast_id] = script
        
        # Generate metadata
        email_description, episode_title = generate_email_headers(all_data)
        
        # Ensure email_description is a DataFrame
        if isinstance(email_description, pd.DataFrame) and not email_description.empty:
            description = email_description['description'].iloc[0]
        else:
            description = ""

        # Store metadata
        podcast_metadata[podcast_id] = {
            "user_id": request.user_id,
            "episode": request.episode,
            "title": episode_title,
            "description": description,
        }
        
        return {"podcast_id": podcast_id, "title": episode_title}
    
    except Exception as e:
        # Log the exception details
        print(f"Error generating podcast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating podcast: {str(e)}")

@app.get("/api/podcasts/{podcast_id}")
async def get_podcast_metadata(podcast_id: str):
    """
    Get metadata for a podcast.
    """
    if podcast_id not in podcast_metadata:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    return podcast_metadata[podcast_id]

@app.websocket("/ws/podcast/{podcast_id}")
async def stream_podcast(websocket: WebSocket, podcast_id: str):
    """
    Stream a podcast to the client when they connect.
    """
    await manager.connect(websocket, podcast_id)
    
    try:
        if podcast_id not in podcast_scripts:
            await websocket.send_json({"error": "Podcast not found"})
            await websocket.close()
            return
        
        # Get the script
        script = podcast_scripts[podcast_id]
        
        # Clean the script for TTS
        turns = clean_text_for_conversational_tts(script)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Send metadata
        await websocket.send_json({
            "type": "metadata",
            "turns": len(turns),
            "title": podcast_metadata.get(podcast_id, {}).get("title", "Untitled Podcast")
        })
        
        # Stream intro message
        await websocket.send_json({
            "type": "status",
            "message": "Starting podcast streaming..."
        })
        
        # Stream each turn
        for index, sentence in enumerate(turns):
            host = 1 if index % 2 == 0 else 2
            voice = 'nova' if host == 1 else 'onyx'
            
            # Send status update
            await websocket.send_json({
                "type": "status",
                "message": f"Generating audio for turn {index+1}/{len(turns)}",
                "progress": (index / len(turns)) * 100
            })
            
            try:
                # Generate audio
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=sentence,
                    response_format='mp3'
                )
                
                # Send host information
                await websocket.send_json({
                    "type": "host",
                    "host": host
                })
                
                # Stream chunks to client
                for chunk in response.iter_bytes(chunk_size=4096):
                    await websocket.send_bytes(chunk)
                    await asyncio.sleep(0.05)  # Control flow rate
                
                # Send end of segment marker
                await websocket.send_json({
                    "type": "segment_end",
                    "turn": index
                })
                
            except Exception as e:
                print(f"Error generating audio for turn {index}: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error generating audio: {str(e)}"
                })
        
        # Send completion message
        await websocket.send_json({
            "type": "complete",
            "message": "Podcast streaming completed"
        })
        
    except WebSocketDisconnect:
        manager.disconnect(websocket, podcast_id)
    except Exception as e:
        print(f"Error streaming podcast: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error streaming podcast: {str(e)}"
            })
        except:
            pass
        manager.disconnect(websocket, podcast_id)

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
