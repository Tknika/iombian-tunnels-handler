#!/usr/bin/env python3

from firestore_client_handler import FirestoreClientHandler
import logging
import threading

logger = logging.getLogger(__name__)


class FirestoreTunnelsHandler(FirestoreClientHandler):

    KEYWORD = "tunnels"
    RESTART_DELAY_TIME_S = 0.5

    def __init__(self, api_key, project_id, refresh_token, device_id, tunnels_update_callback=lambda _: None):
        super().__init__(api_key, project_id, refresh_token)
        self.device_id = device_id
        self.users_path = None
        self.devices_path = None
        self.tunnels_update_callback = tunnels_update_callback
        self.device_subscription = None
        self.tunnels_cache = None

    def start(self):
        logger.debug("Starting Firestore Tunnels Handler")
        self.initialize_client()

    def stop(self):
        logger.debug("Stopping Firestore Tunnels Handler")
        if self.device_subscription:
            self.device_subscription.unsubscribe()
            self.device_subscription = None
        self.stop_client()

    def restart(self):
        logger.debug("Restarting Firestore Tunnels Handler")
        self.stop()
        self.start()

    def on_client_initialized(self):
        logger.info("Firestore client initialized")
        self.devices_path = f"users/{self.user_id}/devices"
        if self.device_subscription:
            return
        self.device_subscription = self.client.collection(self.devices_path).document(
            self.device_id).on_snapshot(self._on_device_update)

    def on_server_not_responding(self):
        logger.error("Firestore server not responding")
        threading.Timer(self.RESTART_DELAY_TIME_S, self.restart).start()

    def on_token_expired(self):
        logger.debug("Refreshing Firebase client token id")
        threading.Timer(self.RESTART_DELAY_TIME_S, self.restart).start()

    def get_tunnel_token(self):
        return self._get_user_field("tunnel_token")

    def get_user_email(self):
        return self._get_user_field("email")

    def get_user_id(self):
        return self.user_id

    def update_tunnel_url(self, port, url):
        self.initialize_client(notify=False)
        if not self.client:
            logger.debug("Firebase client not ready, cannot update tunnel url")
            return
        updated_field = {f"{self.KEYWORD}.{port}.url": url}
        self.client.collection(self.devices_path).document(
            self.device_id).update(updated_field)

    def _get_user_field(self, field):
        self.users_path = f"users"
        self.initialize_client(notify=False)
        if not self.client:
            logger.error("Firebase client not ready, cannot get user field")
            return
        user_info = self.client.collection(self.users_path).document(
            self.user_id).get().to_dict()
        return user_info.get(field)

    def _on_device_update(self, document_snapshot, changes, read_time):
        if len(document_snapshot) != 1:
            return
        device_info = document_snapshot[0].to_dict()

        if not self.KEYWORD in device_info:
            logger.warn(
                f"'{self.KEYWORD}' information not available, creating the new field")
            updated_field = {f"{self.KEYWORD}": {}}
            self.client.collection(self.devices_path).document(self.device_id).update(updated_field)
            return

        tunnels = device_info.get(self.KEYWORD)

        if tunnels != self.tunnels_cache:
            self.tunnels_cache = tunnels
            self.tunnels_update_callback(tunnels)