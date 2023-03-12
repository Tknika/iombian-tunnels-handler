#!/usr/bin/env python3

from boringproxy_api import BoringproxyUserAPI
from boringproxy_local_client import BoringproxyLocalClient
import logging

logger = logging.getLogger(__name__)


class TunnelsHandler():

    DEFAULT_TUNNEL_OPTIONS = {"tunnel_port": "Random", "client_addr": "127.0.0.1", "tls_termination": "client",
                              "allow_external_tcp": False, "password_protect": False, "username": None, "password": None}
    TUNNEL_OPTIONS_BY_TYPE = {
        "node-red": {"tunnel_port": "Random", "client_addr": "127.0.0.1", "tls_termination": "client-tls", "allow_external_tcp": False, "password_protect": False, "username": None, "password": None},
        "wetty": {"tunnel_port": "Random", "client_addr": "127.0.0.1", "tls_termination": "client", "allow_external_tcp": False, "password_protect": False, "username": None, "password": None},
    }

    def __init__(self, service_host, service_token, username, device_name, tunnel_name_generator):
        self.service_host = service_host
        self.service_token = service_token
        self.username = username
        self.device_name = device_name
        self.tunnel_name_generator = tunnel_name_generator
        self.active_tunnels = {}
        self.bp_api_user = BoringproxyUserAPI(
            service_host, username, service_token)
        self.bp_api_client = None
        self.bp_local_client = BoringproxyLocalClient(
            service_host, service_token, device_name)
        self.tunnel_available_callback = None

    def start(self):
        if not self.bp_api_client:
            self.bp_api_client = self.bp_api_user.create_client(
                self.device_name)
        self.bp_local_client.start()

    def stop(self):
        self.bp_local_client.stop()

    def add_tunnel_available_callback(self, callback):
        self.tunnel_available_callback = callback

    def on_tunnels_update(self, tunnels):
        self.active_tunnels = self.bp_api_client.get_tunnels()
        for tunnel_port, tunnel_info in tunnels.items():
            if tunnel_port in self.active_tunnels:
                tunnel_url = tunnel_info.get("url")
                active_tunnel_url = self.active_tunnels.get(tunnel_port)
                if tunnel_url == active_tunnel_url:
                    logger.debug(
                        f"Tunnel for port '{tunnel_port}' already active and published")
                else:
                    logger.debug(
                        f"Tunnel for port '{tunnel_port}' is unpublished")
                    self._announce_tunnel_availability(
                        tunnel_port, active_tunnel_url)
                continue
            logger.debug(f"We must create a tunnel for port {tunnel_port}")
            tunnel_type = tunnel_info.get("type")
            subdomain = self.tunnel_name_generator.create_service_name(
                tunnel_type)
            domain = f"{subdomain}.{self.service_host}"
            tunnel_options = self.TUNNEL_OPTIONS_BY_TYPE.get(
                tunnel_type, self.DEFAULT_TUNNEL_OPTIONS)
            url = self.bp_api_client.create_tunnel(domain,
                                                   tunnel_port, **tunnel_options)
            self._announce_tunnel_availability(
                tunnel_port, url)
        for active_tunnel_port in self.active_tunnels.keys():
            if active_tunnel_port not in tunnels:
                logger.debug(
                    f"Active tunnel for port '{active_tunnel_port}' not needed")
                self.bp_api_client.delete_tunnel(active_tunnel_port)

    def _announce_tunnel_availability(self, port, url):
        if self.tunnel_available_callback:
            self.tunnel_available_callback({"url": url, "port": port})
