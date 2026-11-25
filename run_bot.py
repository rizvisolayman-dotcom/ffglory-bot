#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ["BOT_TOKEN"] = "9220955071:AAEPejjOTPfqusnWEJjH_1KQvhDwAj8Mxz0"

from bot import main

if __name__ == "__main__":
    asyncio.run(main())