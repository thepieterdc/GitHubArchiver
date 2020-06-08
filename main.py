#!/usr/bin/env python3
import logging
import multiprocessing as mp
import os
from typing import Tuple

import requests

import sys

# Set-up the logger.
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    level=logging.INFO)

PROCESSES = 4


def ask_user(question: str) -> str:
    resp = None
    while not resp:
        resp = input(question)
    return resp


if __name__ == '__main__':
    # Validate arguments.
    if len(sys.argv) != 3:
        logging.error("Syntax: python3 main.py github_api output_directory")
        exit(1)

    # Parse arguments.
    github_server, out_dir = sys.argv[1:3]

    # Clean arguments.
    github_server = str(github_server).rstrip("/")
    if not github_server.startswith('http'):
        github_server = f"https://{github_server}"

    # Get username from user.
    api_token = ask_user("API token?")

    # Construct request header.
    header = {'Accept': 'application/vnd.github.mercy-preview+json',
              'Authorization': f'token {api_token}',
              'Content-Type': 'application/json'}

    # Fetch the repositories, uses pagination.
    logging.info("Discovering repositories.")
    repositories = set()

    page = 1
    while True:
        url = f"{github_server}/user/repos?page={page}"
        logging.info(f"Fetching {url}")

        response = requests.get(url, headers=header)
        contents = response.json()

        if response.status_code != 200:
            logging.error(contents['message'])
            exit(2)

        # Parse repositories.
        for entry in contents:
            repo_author = entry['owner']['login']
            repo_name = entry['name']
            repositories.add((repo_author, repo_name))

        if not contents:
            break

        page += 1

    logging.info(f"Found {len(repositories)} repositories.")

    # Iterate over every repository owner to create the subdirectories.
    repositories = tuple(repositories)
    for owner in set(map(lambda r: r[0], repositories)):
        try:
            os.mkdir(os.path.join(out_dir, owner))
        except FileExistsError:
            pass


    # Define a download function.
    def download(_repositories: Tuple[str, str, str,]):
        for repository in _repositories:
            # Build the url to download the zip.
            owner, repo = repository
            zip_url = f"{github_server}/repos/{owner}/{repo}/zipball"
            logging.info(f"Downloading {zip_url}")
            response = requests.get(zip_url, headers=header)
            with open(os.path.join(out_dir, owner, f"{repo}.zip"), "wb") as f:
                f.write(response.content)


    # Split the work up in 4 parts and execute each of them in parallel.
    pool = mp.Pool(processes=PROCESSES)
    for p in range(PROCESSES):
        logging.info(f"Starting download process {p + 1}/{PROCESSES}.")
        pool.apply_async(download, (repositories[p::PROCESSES],))

    pool.close()
    pool.join()

    logging.info("Done!")