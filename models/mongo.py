import os
import sys
import inspect
import asyncio
import argparse
from pymongo import ASCENDING, DESCENDING
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config import MONGO_HOST, MONGO_PORT
from motor.motor_asyncio import AsyncIOMotorClient


class Mongo(object):
    def __init__(self):
        self.db_name = 'linkedin'
        self.coll_name = 'jobs'
        self.connect()

    def connect(self):
        self.client = AsyncIOMotorClient(host=MONGO_HOST, port=int(MONGO_PORT))

    async def create_jobs_index(self):
        db = self.client[self.db_name]
        coll = db[self.coll_name]

        fields = [
            'date', 'industries', 'job_function', 'seniority_level', 'url',
            'timestamp'
        ]

        for field in fields:
            if field in ['date', 'timestamp']:
                await coll.create_index([(field, ASCENDING)])
                await coll.create_index([(field, DESCENDING)])
            else:
                await coll.create_index(field)

    async def drop_jobs_index(self):
        db = self.client[self.db_name]
        coll = db[self.coll_name]

        await coll.drop_indexes()

    async def insert_data(self, data):
        db = self.client[self.db_name]
        coll = db[self.coll_name]

        _id = data['_id']
        resp = await coll.update_one(
            filter={'_id': _id}, update={'$set': data}, upsert=True)
        result = {'match': resp.matched_count, 'modified': resp.modified_count}
        print(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-index', action='store_true')
    parser.add_argument('--drop-index', action='store_true')
    args = parser.parse_args()

    mongo = Mongo()
    loop = asyncio.get_event_loop()

    if args.create_index:
        loop.run_until_complete(mongo.create_jobs_index())

    if args.drop_index and not args.create_index:
        loop.run_until_complete(mongo.drop_jobs_index())
