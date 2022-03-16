#!/usr/bin/env python3

import logging
import signal

from communication_module import CommunicationModule
from tunnel_firestore_handler import TunnelFirestoreHandler
from tunnel_name_generator import TunnelNameGenerator
from tunnels_handler import TunnelsHandler

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s - %(name)-16s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TUNNEL_SERVICE_HOST = "iomtunnels.online"


def stop():
    logger.info("Stopping IoMBian Tunnels Service")
    tunnels_handler.stop()
    tunnel_firestore_handler.stop()
    comm_module.stop()


def signal_handler(sig, frame):
    stop()


def on_tunnels_state_update(tunnels):
    tunnels_handler.on_tunnels_update(tunnels)


def on_tunnel_available(tunnel_info):
    logger.debug(f"New tunnel available: {tunnel_info}")
    port = tunnel_info.get("port")
    url = tunnel_info.get("url")
    if not port or not url:
        logger.error(f"New available tunnel is not correct: {tunnel_info}")
        return
    tunnel_firestore_handler.update_tunnel_url(port, url)


if __name__ == "__main__":
    logger.info("Starting IoMBian Tunnels Service")

    comm_module = CommunicationModule(host="127.0.0.1", port=5555)
    comm_module.start()

    api_key = comm_module.execute_command("get_api_key")
    project_id = comm_module.execute_command("get_project_id")
    refresh_token = comm_module.execute_command(
        "get_refresh_token")
    device_id = comm_module.execute_command("get_device_id")

    tunnel_firestore_handler = TunnelFirestoreHandler(
        api_key, project_id, refresh_token, device_id)
    tunnel_token = tunnel_firestore_handler.get_tunnel_token()
    user_email = tunnel_firestore_handler.get_user_email()
    user_id = tunnel_firestore_handler.get_user_id()
    if not tunnel_token:
        logger.error("This user does not have a valid tunnel token")
        comm_module.stop()
        exit(1)

    tunnel_name_generator = TunnelNameGenerator(user_id, device_id)

    tunnels_handler = TunnelsHandler(
        TUNNEL_SERVICE_HOST, tunnel_token, user_email, device_id, tunnel_name_generator)
    tunnels_handler.add_tunnel_available_callback(on_tunnel_available)
    tunnels_handler.start()

    tunnel_firestore_handler.add_tunnels_update_callback(
        on_tunnels_state_update)
    tunnel_firestore_handler.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()
