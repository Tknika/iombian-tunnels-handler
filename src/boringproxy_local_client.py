#!/usr/bin/env python3

import logging
import os
import subprocess
import threading


logger = logging.getLogger(__name__)


class BoringproxyLocalClient:

    BINARY_NAME = "boringproxy"

    def __init__(self, server_host, token, client_name, binary_path=None):
        self.server_host = server_host
        self.token = token
        self.client_name = client_name
        self.binary_finder = BinaryFileFinder(self.BINARY_NAME)
        self.binary_path = binary_path if binary_path else self.binary_finder.get_binary_path()
        self.process = None
        self.output_checker_thread = None

    def start(self):
        logger.debug(f"Starting '{self.client_name}' boringproxy local client")
        if not self.binary_path:
            logger.error(
                "Binary file for boringproxy local client could not be found")
            return
        command = [self.binary_path, "client",  "-server", self.server_host,
                   "-token", self.token, "-client-name", self.client_name]
        self.process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.output_checker_thread = threading.Thread(
            target=self.__output_checker)
        self.output_checker_thread.start()

    def stop(self):
        logger.debug(f"Stopping '{self.client_name}' boringproxy local client")
        if self.process:
            self.process.terminate()

    def restart(self):
        logger.debug(
            f"Restarting '{self.client_name}' boringproxy local client")
        self.stop()
        self.start()

    def __output_checker(self):
        line = ''
        while self.process.returncode is None:
            character = self.process.stdout.read(1).decode("utf-8")
            line += character
            if character == '\n':
                logger.debug(line)
                line = ''
            if "Email address: " in line:
                logger.info(
                    "Email input detected, sending new line character to access the license")
                self.process.stdin.write(b'\n')
                self.process.stdin.flush()
                break
            self.process.poll()
        logger.debug("Output checker has finished")


class BinaryFileFinder:

    BINARY_FOLDERS = [
        "/usr/bin",
        "/usr/sbin",
        "/usr/local/bin",
        "/usr/local/sbin"
    ]

    def __init__(self, binary_name):
        self.binary_name = binary_name

    def get_binary_path(self):
        for folder in self.BINARY_FOLDERS:
            possible_path = f"{folder}/{self.binary_name}"
            if os.path.isfile(possible_path):
                return possible_path
