from base64 import b64encode
from openai import OpenAI
from config import OPENAI_API_KEY

# Initialize OpenAI client using the API key from config
client = OpenAI(api_key=OPENAI_API_KEY)

def describe_room(images):
    base64_images = [b64encode(img).decode('utf-8') for img in images]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides brief, concise room descriptions."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this room in a single, clear paragraph (maximum 3-4 sentences). Focus on the main features and layout."
                },
                *[{
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}"
                    }
                } for image in base64_images]
            ]
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=200
    )

    return response.choices[0].message.content

def leftOrRight(detections, frame_midpoint):
    largest_area = 0
    largest = {"x_max": 0, "x_min": 0, "y_max": 0, "y_min": 0}

    if not detections:
        return -1, 0

    for d in detections:
        area = (d.x_max - d.x_min) * (d.y_max - d.y_min)
        if area > largest_area:
            largest_area = area
            largest = d

    object_centerX = (largest["x_min"] + largest["x_max"]) / 2
    offset = (object_centerX - frame_midpoint) / frame_midpoint
    return offset, largest_area
