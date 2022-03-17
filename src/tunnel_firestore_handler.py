#!/usr/bin/env python3

from firestore_handler import FirestoreHandler
import logging

logger = logging.getLogger(__name__)


class TunnelFirestoreHandler(FirestoreHandler):

    KEYWORD = "tunnels"

    def __init__(self, api_key, project_id, refresh_token, device_id):
        super().__init__(api_key, project_id, refresh_token, self.__on_expired_token)
        self.device_id = device_id
        self.users_path = None
        self.devices_path = None
        self.tunnels_update_callback = None
        self.device_subscription = None
        self.tunnels_cache = None

    def start(self):
        logger.debug("Starting Firestore Tunnels Handler")
        self.initialize_db()

    def stop(self):
        logger.debug("Stopping Firestore Tunnels Handler")
        if self.device_subscription:
            self.device_subscription.unsubscribe()
            self.device_subscription = None
        if self.db:
            self.stop_db()

    def initialize_db(self):
        super().initialize_db()
        if not self.db:
            logger.error("DB connection not ready")
            return
        self.devices_path = f"users/{self.user_id}/devices"
        if not self.device_subscription:
            self.device_subscription = self.db.collection(self.devices_path).document(
                self.device_id).on_snapshot(self.__on_device_update)

    def get_tunnel_token(self):
        return self.__get_user_field("tunnel_token")

    def get_user_email(self):
        return self.__get_user_field("email")

    def get_user_id(self):
        return self.user_id

    def update_tunnel_url(self, port, url):
        if not self.db:
            self.initialize_db()
        updated_field = {f"{self.KEYWORD}.{port}.url": url}
        self.db.collection(self.devices_path).document(
            self.device_id).update(updated_field)

    def add_tunnels_update_callback(self, callback):
        self.tunnels_update_callback = callback

    def __get_user_field(self, field):
        self.users_path = f"users"
        super().initialize_db()
        if not self.db:
            logger.error("DB connection not ready")
            return
        user_info = self.db.collection(self.users_path).document(
            self.user_id).get().to_dict()
        return user_info.get(field)

    def __on_device_update(self, document_snapshot, changes, read_time):
        if len(document_snapshot) != 1:
            return
        device_info = document_snapshot[0].to_dict()

        if not self.KEYWORD in device_info:
            logger.warn(
                f"'{self.KEYWORD}' information not available, creating the new field")
            updated_field = {f"{self.KEYWORD}": {}}
            self.db.collection(self.devices_path).document(self.device_id).update(updated_field)
            return

        tunnels = device_info.get(self.KEYWORD)

        if tunnels != self.tunnels_cache:
            self.tunnels_cache = tunnels
            self.tunnels_update_callback(tunnels)

    def __on_expired_token(self):
        logger.debug("Refreshing Token Id")
        if self.device_subscription:
            self.device_subscription.unsubscribe()
            self.device_subscription = None
        self.db = None
        self.initialize_db()
