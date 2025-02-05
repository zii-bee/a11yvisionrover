# single script solution

import asyncio
import io
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from viam.components.camera import Camera
from viam.components.base import Base
from viam.media.utils.pil import viam_to_pil_image
from openai import OpenAI
import os
from base64 import b64encode
import pyaudio

client = OpenAI(api_key='')


API_KEY = ''
API_KEY_ID = ''
ROBOT_ADDR = ''

images = []

async def connect():
    opts = RobotClient.Options.with_api_key(api_key=API_KEY, api_key_id=API_KEY_ID)
    return await RobotClient.at_address(ROBOT_ADDR, opts)

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

    object_centerX = (largest.x_min + largest.x_max) / 2
    offset = (object_centerX - frame_midpoint) / frame_midpoint
    return offset, largest_area

async def capture_images_with_rotation(base, camera, num_images=6, rotation_angle=60):
    images_local = []
    try:
        for i in range(num_images):
            frame = await camera.get_image(mime_type="image/jpeg")
            pil_frame = viam_to_pil_image(frame)

            image_buffer = io.BytesIO()
            pil_frame.save(image_buffer, format='JPEG')
            images_local.append(image_buffer.getvalue())

            print(f"Captured image {i + 1}/{num_images}")

            if i < num_images - 1:
                print(f"Rotating rover {rotation_angle} degrees")
                await base.spin(rotation_angle, velocity=30)
                await asyncio.sleep(1)

        return images_local
    except Exception as e:
        print(f"error during capture: {e}")
        return images_local

def describe_room():
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

def text_to_speech(text):
    # initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=8,
                    channels=1,
                    rate=24000,
                    output=True)

    # create and stream the audio
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="pcm"
    ) as response:
        for chunk in response.iter_bytes(1024):
            stream.write(chunk)

    # clean up
    stream.stop_stream()
    stream.close()
    p.terminate()

async def user_input_task(input_queue):
    # continuously read user input in the background
    while True:
        user_inp = await asyncio.to_thread(input, "")
        await input_queue.put(user_inp.strip())

async def follow_task(machine, input_queue):
    spin_base_speed = 15
    move_distance = 240
    vel = 320
    fill_threshold = 0.3
    resume_threshold = 0.2
    moving = False

    base = Base.from_robot(machine, "viam_base")
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    my_detector = VisionClient.from_robot(machine, "my_color_detector")

    print("Rover follow logic started.")
    print("Press '1' + Enter to capture images and describe the room. Press 'q' + Enter to quit.")

    while True:
        while not input_queue.empty():
            cmd = await input_queue.get()
            if cmd == '1':
                # stop following temporarily to capture images
                print("Stopping follow to capture images...")
                await base.stop()
                captured_images = await capture_images_with_rotation(base, camera)
                # store captured images globally
                global images
                images = captured_images
                print("Capture completed. Describing room...")
                room_description = describe_room()
                print("\nRoom Description:\n")
                print(room_description)
                print("\nConverting description to speech...")
                text_to_speech(room_description)
                print("Done!")
                print("Resuming follow...")
            elif cmd.lower() == 'q':
                print("Quitting program.")
                await base.stop()
                return
        
        frame = await camera.get_image(mime_type="image/jpeg")
        pil_frame = viam_to_pil_image(frame)
        frame_midpoint = pil_frame.size[0] / 2
        frame_area = pil_frame.size[0] * pil_frame.size[1]

        detections = await my_detector.get_detections_from_camera(camera_name)
        offset, largest_area = leftOrRight(detections, frame_midpoint)
        fill_ratio = largest_area / frame_area
        print(f"Object fill ratio: {fill_ratio:.2f}")

        if fill_ratio >= fill_threshold:
            if moving:
                print("Object fills enough of the frame. Stopping.")
                await base.stop()
                moving = False
        elif fill_ratio < resume_threshold or offset != -1:
            if not moving:
                print("Object moved further away or is in frame. Resuming movement.")
                moving = True

        if moving:
            if offset == -1:
                print("Object not detected. Searching...")
                await base.spin(spin_base_speed, vel)
            else:
                spin_adjustment = spin_base_speed * offset
                print(f"Offset: {offset:.2f}, Adjusting spin by: {spin_adjustment:.2f}")
                await base.spin(spin_adjustment, vel)
                await base.move_straight(move_distance, vel)

        await asyncio.sleep(0.1)  # avoid busy loop

async def main():
    machine = None
    try:
        machine = await connect()
        input_queue = asyncio.Queue()

        # start tasks
        input_task = asyncio.create_task(user_input_task(input_queue))
        follow = asyncio.create_task(follow_task(machine, input_queue))

        # wait for follow_task to finish (likely when user presses 'q')
        await follow

        # cancel input task if still running
        input_task.cancel()
        try:
            await input_task
        except asyncio.CancelledError:
            pass

    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        if machine:
            await machine.close()

if __name__ == '__main__':
    asyncio.run(main())