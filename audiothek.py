import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

API_URL = 'https://api.ardaudiothek.de/graphql'
GRAPHQL_DIR = os.path.join(Path(__file__).parent, 'graphql')


def download_episodes(ard_id: int, directory: str):
    # change query if url is a collection
    if 'sammlung' in args.url.lower():
        graphql_file = 'editorialCollection'
    else:
        graphql_file = 'ProgramSetEpisodesQuery'

    with open(os.path.join(GRAPHQL_DIR, f'{graphql_file}.graphql')) as f:
        query = f.read()

    response = requests.get(API_URL, params={
        'query': query,
        'variables': json.dumps({'id': ard_id})
    })
    response_json = response.json()

    nodes = response_json.get('data').get('result').get('items').get('nodes')

    for i, node in enumerate(nodes):
        number = node['id']

        node_id = node.get('id')
        title = node.get('title')

        # get title from infos
        array_filename = re.findall(r'(\w+)', title)
        if len(array_filename) > 0:
            filename = '_'.join(array_filename)
        else:
            filename = node_id

        filename = f'{filename}_{number}'

        # get image information
        image_url = node.get('image').get('url')
        image_url = image_url.replace('{width}', '500')
        mp3_url = node.get('audios')[0].get('downloadUrl') or node.get('audios')[0].get('url')
        programset_id = node.get('programSet').get('id')

        program_path: str = os.path.join(directory, programset_id)

        # get information of program
        if programset_id:
            try:
                os.makedirs(program_path)
            except FileExistsError:
                pass
            except Exception as e:
                print('[Error] Couldn\'t create output directory!', file=sys.stderr)
                print(e, file=sys.stderr)
                return

            # write image
            image_file_path = os.path.join(program_path, f'{filename}.jpg')

            if not os.path.exists(image_file_path):
                response_image = requests.get(image_url)
                with open(image_file_path, 'wb') as f:
                    f.write(response_image.content)

            # write mp3
            mp3_file_path = os.path.join(program_path, f'{filename}.mp3')

            print(f'Download: {i + 1} of {len(nodes)} -> {mp3_file_path}')

            if not os.path.exists(mp3_file_path):
                response_mp3 = requests.get(mp3_url)

                with open(mp3_file_path, 'wb') as f:
                    f.write(response_mp3.content)
        else:
            print('No programset_id found!', file=sys.stderr)


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

    args = parser.parse_args()

    url_parser = re.search(r'/(\d+)/?$', args.url)
    if url_parser:
        download_episodes(int(url_parser.group(1)), os.path.realpath(args.directory))
    else:
        exit('No ID found in URL')
