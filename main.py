import asyncio
from viam.robot.client import RobotClient
from config import VIAM_API_KEY, VIAM_API_KEY_ID, ROBOT_ADDR
from follow import user_input_task, follow_task

async def connect():
    opts = RobotClient.Options.with_api_key(api_key=VIAM_API_KEY, api_key_id=VIAM_API_KEY_ID)
    return await RobotClient.at_address(ROBOT_ADDR, opts)

async def main():
    machine = None
    try:
        machine = await connect()
        input_queue = asyncio.Queue()

        # Start background tasks
        input_task = asyncio.create_task(user_input_task(input_queue))
        follow = asyncio.create_task(follow_task(machine, input_queue))

        # Wait for follow_task to finish (likely when user presses 'q')
        await follow

        # Cancel input task if still running
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
