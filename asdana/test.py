"""
Unit tests for the Asdana project.
"""

import asyncio
from asdana.database.database import create_tables

asyncio.run(create_tables())
