import asyncio
import io
from viam.media.utils.pil import viam_to_pil_image

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
        print(f"Error during capture: {e}")
        return images_local
