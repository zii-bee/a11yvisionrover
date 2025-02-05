import pyaudio
from config import OPENAI_API_KEY
from openai import OpenAI

# Initialize OpenAI client (if not already initialized in vision_utils, you can use a separate instance)
client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech(text):
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=8,
                    channels=1,
                    rate=24000,
                    output=True)

    # Create and stream the audio using OpenAI TTS
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="pcm"
    ) as response:
        for chunk in response.iter_bytes(1024):
            stream.write(chunk)

    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
