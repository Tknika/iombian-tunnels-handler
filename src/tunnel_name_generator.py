#!/usr/bin/env python3

import hashlib
import logging

logger = logging.getLogger(__name__)


class TunnelNameGenerator():

    def __init__(self, user_id, device_id):
        self.user_id = user_id
        self.device_id = device_id

    def create_service_name(self, service_name):
        full_name = f"{service_name}-{self.device_id}-{self.user_id}"
        full_name_hashed = hashlib.md5(full_name.encode()).hexdigest()
        return full_name_hashed
