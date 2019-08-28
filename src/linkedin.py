import re
import aiohttp
import asyncio
import argparse
from pprint import pprint
from bs4 import BeautifulSoup


class Linkedin(object):
    def __init__(self):
        pass

    async def fetch_page(self, url, json_=False):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                messsage = '{} status code:{}'.format(url, resp.status)
                print(messsage)
                result = None
                if resp.status == 200:
                    if json_:
                        result = await resp.json()
                    else:
                        result = await resp.text()

                return result

    def parse_index(self, content):
        soup = BeautifulSoup(content, 'lxml')
        temp_jobs = soup.find('ul', {
            'class': 'jobs-search__results-list'
        }).findAll('li')

        for temp_job in temp_jobs:
            temp = {}

            temp['logo'] = temp_job.find('img', {
                'class': re.compile('^entity-image')
            })['data-delayed-url']

            temp['company_name'] = temp_job.find(
                'h4', {
                    'class': 'result-card__subtitle job-result-card__subtitle'
                }).text.strip()

            temp['location'] = temp_job.find(
                'span', {
                    'class': 'job-result-card__location'
                }).text.strip()

            temp['job_title'] = temp_job.find(
                'h3', {
                    'class': 'result-card__title job-result-card__title'
                }).text.strip()

            temp['date'] = temp_job.find('time')['datetime']

            temp['job_description']

            pprint(temp)

    async def index(self, url):
        stop = False
        while not stop:
            content = await self.fetch_page(url, json_=False)
            self.parse_index(content)
            exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    args = parser.parse_args()

    linkedin = Linkedin()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(linkedin.index(args.url))
