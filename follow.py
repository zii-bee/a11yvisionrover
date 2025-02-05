import asyncio
from viam.components.base import Base
from viam.components.camera import Camera
from viam.services.vision import VisionClient
from capture import capture_images_with_rotation
from vision_utils import describe_room, leftOrRight
from speech import text_to_speech

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

    global images
    images = []  # Global variable to store captured images

    while True:
        while not input_queue.empty():
            cmd = await input_queue.get()
            if cmd == '1':
                print("Stopping follow to capture images...")
                await base.stop()
                captured_images = await capture_images_with_rotation(base, camera)
                images = captured_images
                print("Capture completed. Describing room...")
                room_description = describe_room(images)
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
        from viam.media.utils.pil import viam_to_pil_image  # Local import if needed
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
