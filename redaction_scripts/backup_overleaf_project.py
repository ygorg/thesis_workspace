"""
Ygor Gallina 2021
Heavily copied from https://github.com/tbmihailov/overleaf-backup-tool
"""

import json
import requests as reqs

from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/60.0.3112.113 Safari/537.36'}


def get_login_cookies(username, password):
    global headers
    _url_signin = 'https://www.overleaf.com/login'
    # Retrieve authenticity token from login page
    # This is required to make the login request
    r_signing_get = reqs.get(_url_signin, headers=headers)
    if r_signing_get.status_code != 200:
        err_msg = f'Status code {r_signing_get.status_code} '\
                  f'when loading {_url_signin}. Can not continue...'
        raise Exception(err_msg)

    html_doc = r_signing_get.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    authenticity_token = ''
    for tag in soup.find_all('input'):
        if tag.get("name", None) == '_csrf':
            authenticity_token = tag.get('value', None)
            break

    if len(authenticity_token) == 0:
        err_msg = 'authenticity_token is empty! Cannot continue...'
        raise Exception(err_msg)

    # Get login cookie
    # form login data object
    login_json = {
        '_csrf': authenticity_token,
        'email': username,
        'password': password,
    }

    r_signing_post = reqs.post(_url_signin, data=login_json, timeout=5,
                               headers=headers, cookies=r_signing_get.cookies)

    if not r_signing_post.status_code == 200:
        err_msg = 'Status code {} when signing in {} with user [{}].'
        err_msg = err_msg.format(r_signing_post.status_code,
                                 _url_signin, username)
        raise Exception(err_msg)

    try:
        response = json.loads(r_signing_post.text)
        if response['message']['type'] == 'error':
            msg = 'Login failed: {}'.format(response['message']['text'])
            raise ValueError(msg)
    except json.JSONDecodeError:
        # This happens when the login is successful because a HTML document
        # is returned instead of some JSON.
        pass
    return r_signing_post.cookies


def get_project_archive(project_id, login_cookies):
    # Retrieve given project archive
    global headers
    zip_url = f'https://www.overleaf.com/project/{project_id}/download/zip'

    zip_archive = reqs.get(zip_url, headers=headers, cookies=login_cookies)
    if zip_archive.status_code != 200:
        raise Exception(f'Something went wrong! : {zip_archive.status_code}')

    return zip_archive.content


if __name__ == '__main__':
    import os
    import sys
    import argparse
    from datetime import datetime

    def arguments():
        parser = argparse.ArgumentParser()
        parser.add_argument('project_id', help='Id of the project to backup (last part of project url).')
        parser.add_argument('username', help='Overleaf username, or file with 2 lines ("username\\npassword").')
        parser.add_argument('-p', '--password', help='Overleaf password.')
        return parser.parse_args()

    args = arguments()

    if os.path.isfile(args.username) and not args.password:
        with open(args.username) as f:
            args.username, args.password = f.read().strip().split('\n')
        args.username = args.username.strip()
        args.password = args.password.strip()

    cookies = get_login_cookies(args.username, args.password)
    del args.username, args.password

    archive = get_project_archive(args.project_id, cookies)

    date_str = datetime.now().strftime('%d%m%y')

    with open('backup_{}_{}.zip'.format(args.project_id, date_str), 'wb') as f:
        f.write(archive)
