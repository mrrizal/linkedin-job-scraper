import os
import sys
import inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config import MONGO_HOST, MONGO_PORT
from motor.motor_asyncio import AsyncIOMotorClient


class Mongo(object):
    def __init__(self):
        self.connect()

    def connect(self):
        self.client = AsyncIOMotorClient(host=MONGO_HOST, port=int(MONGO_PORT))

    async def create_index(self):
        db = self.client['linkedin']
        coll = db['jobs']
        await coll.create_index('date')
