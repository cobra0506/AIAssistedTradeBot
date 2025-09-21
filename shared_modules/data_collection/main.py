# shared_modules/data_collection/main.py
import asyncio
from .console_main import console_main

def run_data_collection():
    """Entry point for data collection functionality"""
    asyncio.run(console_main())