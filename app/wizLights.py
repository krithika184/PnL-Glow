import os
from dotenv import load_dotenv
import asyncio
from pywizlight import wizlight, PilotBuilder

load_dotenv()

async def test(color):
    light = wizlight(os.getenv('LIGHT_IP'))

    match color:
        case 'GREEN':
            print("Turning GREEN...")
            await light.turn_on(PilotBuilder(brightness=255, rgb=(0, 255, 0)))

        case 'RED':
            print("Turning RED...")
            await light.turn_on(PilotBuilder(brightness=255, rgb=(255, 0, 0)))

        case 'RELAX':
            await light.turn_on(PilotBuilder(brightness=255, rgb=(0,0,0)))

        case _:
            print("Turning OFF...")
            await light.turn_off()

    print("Done!")

def changeLights(color):
    print(color)
    asyncio.run(test(color))
