import asyncio
import websockets

async def test_audio_stream():
    user_id = "33"  # Replace with your user ID
    episode = "pickle_script"   # Replace with your episode number
    uri = f"ws://127.0.0.1:8000/ws/podcast/{user_id}/{episode}"

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")

        while True:
            try:
                message = await websocket.recv()
                if isinstance(message, bytes):
                    print("Received audio chunk")
                    # Save the audio chunk to a file for verification
                    with open("test_audio.mp3", "ab") as f:
                        f.write(message)
                else:
                    print("Received message:", message)
            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break

# Run the test
asyncio.run(test_audio_stream())
