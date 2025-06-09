import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from pathvalidate import sanitize_filename

API_URL = 'https://api.ardaudiothek.de/graphql'
GRAPHQL_DIR = os.path.join(Path(__file__).parent, 'graphql')


def download_episodes(show_id: int, directory: str):
    # change query if url is a collection
    if 'sammlung' in args.url.lower():
        graphql_file = 'editorialCollection'
    else:
        graphql_file = 'ProgramSetEpisodesQuery'

    with open(os.path.join(GRAPHQL_DIR, f'{graphql_file}.graphql')) as f:
        query = f.read()

    response = requests.get(API_URL, params={
        'query': query,
        'variables': json.dumps({'id': show_id})
    })
    response_json: dict = response.json()

    nodes: list = response_json.get('data').get('result').get('items').get('nodes')

    for i, node in enumerate(nodes):
        title: str = node.get('title')
        filename: str = sanitize_filename(title.replace('/', '-'))

        if args.square_images:
            image_attr = 'url1X1'
        else:
            image_attr = 'url'
        image_url: str = node.get('image').get(image_attr).replace('{width}', '500')
        mp3_url: str = node.get('audios')[0].get('downloadUrl') or node.get('audios')[0].get('url')

        program_set_id: str = node.get('programSet').get('id')
        program_set_title: str = node.get('programSet').get('title')
        program_path: str = os.path.join(directory, f'{program_set_title} ({program_set_id})')

        episode_title_regex = re.match(r'^(.+?)\s?\(\d+/\d+\)$', title)
        if episode_title_regex and args.group_episodes:
            episode_title: str = episode_title_regex.group(1)
            episode_title_safe: str = sanitize_filename(episode_title.replace('/', '-')).strip()

            program_path: str = os.path.join(program_path, episode_title_safe)

        # get information of program
        if program_set_id:
            if not os.path.exists(program_path):
                try:
                    os.makedirs(program_path)
                except Exception as e:
                    print(f'[Error] Couldn\'t create output directory: {e}', file=sys.stderr)
                    continue

            image_file_path = os.path.join(program_path, f'{filename}.jpg')

            if not os.path.exists(image_file_path):
                response_image = requests.get(image_url)
                with open(image_file_path, 'wb') as f:
                    f.write(response_image.content)

            mp3_file_path: str = os.path.join(program_path, f'{filename}.mp3')

            print(f'Download: {i + 1} of {len(nodes)} -> {mp3_file_path}')

            if os.path.exists(mp3_file_path):
                print('skipping (file exists)')
            else:
                response_mp3 = requests.get(mp3_url)

                with open(mp3_file_path, 'wb') as f:
                    f.write(response_mp3.content)
        else:
            print('No program_set_id found!', file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='ARD Audiothek downloader.'
    )
    parser.add_argument(
        '--url', '-u', type=str, default='', required=True,
        help='Insert audiothek url (e.g. https://www.ardaudiothek.de/sendung/2035-die-zukunft-beginnt-jetzt-scifi-mit-niklas-kolorz/12121989/)'
    )
    parser.add_argument(
        '--directory', '-f', type=str, default='output', help='directory to save all mp3s'
    )
    parser.add_argument('--square-images', '-s', action='store_true', default=False,
                        help='Download images in aspect ratio 1x1 instead of widescreen')
    parser.add_argument('--group-episodes', '-g', action='store_true', default=False,
                        help='Group episodes in own sub-directories')
    args = parser.parse_args()

    url_parser = re.search(r'/(\d+)/?$', args.url)
    if url_parser:
        download_episodes(int(url_parser.group(1)), os.path.realpath(args.directory))
    else:
        exit('No ID found in URL')
