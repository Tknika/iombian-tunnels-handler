#!/usr/bin/env python3

from google.cloud.firestore import Client
from google.oauth2.credentials import Credentials
import json
import logging
import requests
import threading

logger = logging.getLogger(__name__)


class FirestoreHandler(object):

    TOKEN_REFRESH_TIME_MIN = 58
    TOKEN_RETRY_TIME_MIN = 2

    def __init__(self, api_key, project_id, refresh_token, on_expired_token):
        self.api_key = api_key
        self.project_id = project_id
        self.refresh_token = refresh_token
        self.on_expired_token = on_expired_token
        self.refresh_expired_token_timer = None
        self.user_id = None
        self.db = None

    def initialize_db(self):
        if self.db:
            return
        logger.debug("Initializing Firestore database connection")
        creds = self.__get_credentials()
        if creds:
            self.db = Client(self.project_id, creds)
        self.refresh_expired_token_timer = threading.Timer(
            self.TOKEN_REFRESH_TIME_MIN*60.0 if creds else self.TOKEN_RETRY_TIME_MIN*60.0, self.on_expired_token)
        self.refresh_expired_token_timer.start()

    def stop_db(self):
        logger.debug("Stopping Firestore database connection")
        self.db = None
        if self.refresh_expired_token_timer:
            self.refresh_expired_token_timer.cancel()
            self.refresh_expired_token_timer.join()

    def __get_credentials(self):
        user_id, token_id = self.__get_ids()
        if not user_id or not token_id:
            logger.warn(f"Invalid user and token ids ({user_id}, {token_id})")
            return None
        self.user_id = user_id
        creds = Credentials(token_id, self.refresh_token)
        return creds

    def __get_ids(self):
        token_response = self.__get_token_response()
        user_id = token_response.get("user_id")
        token_id = token_response.get("id_token")
        return (user_id, token_id)

    def __get_token_response(self):
        request_ref = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"grantType": "refresh_token",
                          "refreshToken": self.refresh_token})
        try:
            response_object = requests.post(
                request_ref, headers=headers, data=data)
            return response_object.json()
        except:
            return {}
