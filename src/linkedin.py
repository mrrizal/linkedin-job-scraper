import re
import os
import sys
import inspect
import aiohttp
import asyncio
import hashlib
from pprint import pprint
from bs4 import BeautifulSoup
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from models.mongo import Mongo


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

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def parse_index(self, content):
        soup = BeautifulSoup(content, 'lxml')
        temp_jobs = soup.findAll('li', {'class': re.compile('^result-card')})

        result = []
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

            temp[
                'url'] = 'https://id.linkedin.com/jobs-guest/jobs/api/jobPosting/{}?refId={}'.format(
                    temp_job['data-id'], temp_job['data-search-id'])

            temp['_id'] = hashlib.md5(temp['url'].encode()).hexdigest()

            result.append(temp)
        return result

    def parse_detail(self, job, content):
        soup = BeautifulSoup(content, 'lxml')
        job['description'] = soup.find(
            'div', {
                'class': 'description__text description__text--rich'
            }).text

        job_criteria_list = soup.find('ul', {
            'class': 'job-criteria__list'
        }).findAll('li')

        criteria_fields = ['seniority_level', 'job_function', 'industries']

        for job_criteria in job_criteria_list:
            if job_criteria.find('h3').text.lower() in [
                    'seniority level', 'tingkat senioritas'
            ]:
                job['seniority_level'] = [
                    i.text for i in job_criteria.findAll('span')
                ]
            elif job_criteria.find('h3').text.lower() in [
                    'job function', 'fungsi pekerjaan'
            ]:
                job['job_function'] = [
                    i.text for i in job_criteria.findAll('span')
                ]
            elif job_criteria.find('h3').text.lower() in [
                    'industries', 'industri'
            ]:
                job['industries'] = [
                    i.text for i in job_criteria.findAll('span')
                ]

        for criteria_field in criteria_fields:
            if criteria_field not in job:
                job[criteria_field] = None

        return job

    async def get_detail(self, jobs):
        chunk_size = 5
        for chunked_jobs in self.chunks(jobs, chunk_size):
            detail_job_tasks = await asyncio.gather(
                *[self.fetch_page(job['url']) for job in chunked_jobs])
            for counter, detail_job in enumerate(detail_job_tasks):
                if detail_job is not None:
                    pprint(
                        self.parse_detail(chunked_jobs[counter], detail_job))

    async def index(self):
        start = 0
        size = 25
        stop = False
        while not stop:
            base_url = 'https://id.linkedin.com/jobs-guest/jobs/api/jobPostings/jobs?location=Indonesia&redirect=false&position=1&pageNum=0&f_TP=1&start={}'.format(
                start)
            content = await self.fetch_page(base_url, json_=False)
            if content is not None:
                jobs = self.parse_index(content)

                if len(jobs) == 0:
                    stop = True
                else:
                    await self.get_detail(jobs)

                start += size


if __name__ == '__main__':
    mongo = Mongo()
    linkedin = Linkedin()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(linkedin.index())
