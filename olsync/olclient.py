"""Overleaf Two-Way Sync Tool"""
##################################################
# MIT License
##################################################
# File: olclient.py
# Description: Overleaf API Wrapper
# Author: Moritz Glöckl
# License: MIT
# Version: 1.0.3
##################################################
import hashlib
import random

import requests as reqs
from bs4 import BeautifulSoup
import json
import uuid
import websocket._core

# Where to get the CSRF Token and where to send the login request to
LOGIN_URL = "https://www.overleaf.com/login"
PROJECT_URL = "https://www.overleaf.com/project"  # The dashboard URL
# The URL to download all the files in zip format
DOWNLOAD_URL = "https://www.overleaf.com/project/{}/download/zip"
UPLOAD_URL = "https://www.overleaf.com/project/{}/upload"  # The URL to upload files
SOCKET_TOKEN_URL = "https://www.overleaf.com/socket.io/1/"
SOCKET_UPDATE_URL = "https://www.overleaf.com/socket.io/1/websocket/"


class OverleafClient(object):
    """
    Overleaf API Wrapper
    Supports login, querying all projects, querying a specific project, downloading a project and
    uploading a file to a project.
    """

    def __init__(self, session: reqs.Session = None, csrf=None):
        self._csrf = csrf  # Store the CSRF token since it is needed for some requests
        self._session = session if session else reqs.session()
        self.ws = None
        self.project_cache = {}

    def login(self, username, password):
        """
        Login to the Overleaf Service with a username and a password
        Params: username, password
        Returns: Dict of cookie and CSRF
        """

        get_login = self._session.get(LOGIN_URL)
        self._csrf = BeautifulSoup(get_login.content, 'html.parser').find(
            'input', {'name': '_csrf'}).get('value')
        login_json = {
            "_csrf": self._csrf,
            "email": username,
            "password": password
        }
        post_login = self._session.post(LOGIN_URL, json=login_json)

        # On a successful authentication the Overleaf API returns a new authenticated cookie.
        # If the cookie is different than the cookie of the GET request the authentication was successful
        if post_login.status_code == 200 and get_login.cookies["overleaf_session2"] != post_login.cookies[
            "overleaf_session2"]:
            return {"session": self._session, "csrf": self._csrf}

    def all_projects(self):
        """
        Get all of a user's active projects (= not archived)
        Returns: List of project objects
        """
        projects_page = self._session.get(PROJECT_URL)
        json_content = json.loads(
            BeautifulSoup(projects_page.content, 'html.parser').find('script', {'id': 'data'}).contents[0])
        return list(filter(lambda x: not x.get("archived"), json_content.get("projects")))

    def get_project(self, project_name):
        """
        Get a specific project by project_name
        Params: project_name, the name of the project
        Returns: project object
        """
        projects_page = self._session.get(PROJECT_URL)
        json_content = json.loads(
            BeautifulSoup(projects_page.content, 'html.parser').find('script', {'id': 'data'}).contents[0])
        return next(
            filter(lambda x: not x.get("archived") and x.get("name")
                             == project_name, json_content.get("projects")),
            None)

    def download_project(self, project_id):
        """
        Download project in zip format
        Params: project_id, the id of the project
        Returns: bytes string (zip file)
        """
        r = self._session.get(DOWNLOAD_URL.format(project_id), stream=True)
        return r.content

    def upload_file(self, project_id, file_name, file_size, file):
        """
        Upload a file to the project

        Params:
        project_id: the id of the project
        file_name: how the file will be named
        file_size: the size of the file in bytes
        file: the file itself

        Returns: True on success, False on fail
        """
        project_dirs=self.get_project_dir(format(int(project_id, 16) - 1, 'x'))
        # To get the folder_id, we convert the hex project_id to int, subtract 1 and convert it back to hex
        params = {
            # FIXME
            "folder_id": format(int(project_id, 16) - 1, 'x'),
            "_csrf": self._csrf,
            "qquuid": str(uuid.uuid4()),
            "qqfilename": file_name,
            "qqtotalfilesize": file_size,
        }
        files = {
            "qqfile": file
        }
        r = self._session.post(UPLOAD_URL.format(project_id), params=params, files=files)
        return r.status_code == str(200) and json.loads(r.content)["success"]

    def get_project_dir(self, project_id: str):
        if project_id in self.project_cache:
            return self.project_cache[project_id]

        self.get_socket().send('5:4+::{"name":"joinProject","args":[{"project_id":"' + project_id + '"}]}')
        recv = self.get_socket().recv()
        self.project_cache[project_id] = json.loads(recv[12:])
        return self.project_cache[project_id]

    def get_socket(self) -> websocket._core.WebSocket:
        if self.ws:
            return self.ws
        resp = self._session.get(SOCKET_TOKEN_URL)
        if resp.status_code == 200:
            token = resp.text.split(":")[0]

        headers = {"Connection": "Upgrade", "Pragma": "no-cache", "Cache-Control": "no-cache",
                   "Upgrade": "websocket", "Origin": "https://www.overleaf.com", "Sec-WebSocket-Version": "13",
                   "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
                   "Sec-WebSocket-Key": hashlib.md5(random.getrandbits(2).to_bytes(2, "big")).hexdigest()}
        ws = websocket._core.create_connection("wss://www.overleaf.com/socket.io/1/websocket/" + token)
        resp=self._session.get(SOCKET_UPDATE_URL + token, headers=headers)
        self.ws = ws
        return ws
