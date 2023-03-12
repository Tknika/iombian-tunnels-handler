#!/usr/bin/env python3

import logging
import signal
import sys

from communication_module import CommunicationModule
from firestore_tunnels_handler import FirestoreTunnelsHandler
from tunnel_name_generator import TunnelNameGenerator
from tunnels_handler import TunnelsHandler

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s - %(name)-16s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TUNNEL_SERVICE_HOST = "iomtunnels.online"


def stop():
    logger.info("Stopping IoMBian Tunnels Service")
    if tunnels_handler: tunnels_handler.stop()
    if firestore_tunnels_handler: firestore_tunnels_handler.stop()
    if comm_module: comm_module.stop()


def signal_handler(sig, frame):
    stop()


def on_tunnels_state_update(tunnels):
    tunnels_handler.on_tunnels_update(tunnels)


def on_tunnel_available(tunnel_info):
    logger.info(f"New tunnel available: {tunnel_info}")
    port = tunnel_info.get("port")
    url = tunnel_info.get("url")
    if not port or not url:
        logger.error(f"New available tunnel is not correct: {tunnel_info}")
        return
    firestore_tunnels_handler.update_tunnel_url(port, url)


if __name__ == "__main__":
    logger.info("Starting IoMBian Tunnels Service")

    comm_module, tunnels_handler, firestore_tunnels_handler = None, None, None

    comm_module = CommunicationModule(host="127.0.0.1", port=5555)
    comm_module.start()

    api_key = comm_module.execute_command("get_api_key")
    project_id = comm_module.execute_command("get_project_id")
    refresh_token = comm_module.execute_command(
        "get_refresh_token")
    device_id = comm_module.execute_command("get_device_id")

    firestore_tunnels_handler = FirestoreTunnelsHandler(
        api_key, project_id, refresh_token, device_id, on_tunnels_state_update)

    tunnel_token = firestore_tunnels_handler.get_tunnel_token()
    user_email = firestore_tunnels_handler.get_user_email()
    user_id = firestore_tunnels_handler.get_user_id()
    if not tunnel_token:
        logger.error("This user does not have a valid tunnel token")
        stop()
        sys.exit(1)

    tunnel_name_generator = TunnelNameGenerator(user_id, device_id)

    tunnels_handler = TunnelsHandler(
        TUNNEL_SERVICE_HOST, tunnel_token, user_email, device_id, tunnel_name_generator)
    tunnels_handler.add_tunnel_available_callback(on_tunnel_available)
    tunnels_handler.start()

    firestore_tunnels_handler.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()
