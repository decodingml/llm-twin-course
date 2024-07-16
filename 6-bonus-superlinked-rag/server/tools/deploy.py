#!/usr/bin/env python3
# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides a script for deploying with docker-compose.

Usage:
    python deploy.py up       # Starts the services in detached mode
    python deploy.py down     # Stops the services
    python deploy.py restart  # Restarts all services
"""
import argparse
import logging
import os
import select
import subprocess
import sys

import yaml
from cerberus import Validator

config_schema = {
    "app_location": {
        "anyof": [
            {"type": "string", "allowed": ["local"]},
            {"type": "string", "regex": r"s3[a|n]?://([^/]+)/(.+)"},
            {"type": "string", "regex": r"gs://([^/]+)/(.+)"},
            {
                "type": "string",
                "regex": r"https?://(?:s3)[^/]*\.amazonaws\.com/([^/]+)/(.+)",
            },
            {
                "type": "string",
                "regex": r"https?://(?:storage\.cloud\.google\.com|storage\.googleapis\.com)/([^/]+)/(.+)",
            },
        ],
        "required": True,
    }
}


class NoOutputStreamsError(Exception):
    pass


def validate_config(config_path: str) -> bool:
    if not os.path.isfile(config_path):
        logging.error("Config file not found at path %s", config_path)
        return False
    validator = Validator(config_schema)
    with open(config_path, encoding="utf-8") as fd:
        config = yaml.safe_load(fd)
    if validator.validate(config):
        return True
    logging.error("There was an error with the provided app.py location configuration.")
    logging.error("Please make sure to use the full file URI in the configuration file (config/config.yaml)!")
    logging.error("The following error(s) were found while validating the passed config file:")
    logging.error(validator.errors)
    return False


def execute_command(command: list, cwd: str = None) -> None:
    if cwd is None:
        cwd = os.getcwd()

    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
        cwd=cwd,
    ) as process:
        if not process.stdout or not process.stderr:
            raise NoOutputStreamsError("Subprocess seems to have spawned without stdout and stderr")
        fds = [process.stdout.fileno(), process.stderr.fileno()]
        stream_map = {
            process.stdout.fileno(): sys.stdout,
            process.stderr.fileno(): sys.stderr,
        }
        while True:
            if process.poll() is not None:
                for line in process.stdout:
                    sys.stdout.write(line)
                for line in process.stderr:
                    sys.stderr.write(line)
                break

            readable, _, _ = select.select(fds, [], [], 0.1)
            for fd in readable:
                line = os.read(fd, 1024).decode("utf-8")
                stream_map[fd].write(line)

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)


def run_docker_compose(command: str) -> None:
    """
    Run a docker-compose command.

    Args:
        command (str): The docker-compose command to run. Supported commands are 'up', 'down', and 'restart'.

    Raises:
        Exception: If the subprocess call returns a non-zero exit code.
    """
    match command:
        case "up":
            execute_command(["docker", "compose", command, "--build", "-d"])
        case _:
            execute_command(["docker", "compose", command])


def print_usage() -> None:
    """
    Print the usage instructions for the deploy script.
    """
    print("Usage: python deploy.py [up|down|restart]")


def main() -> None:
    """
    Parse arguments and execute the docker-compose command.
    """
    parser = argparse.ArgumentParser(description="Deploy services using docker-compose.")
    parser.add_argument(
        "command",
        choices=["up", "down", "restart"],
        help="The docker-compose command to run",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to the configuration file",
    )

    args = parser.parse_args()

    match args.command:
        case "up" | "restart":
            if validate_config(args.config):
                run_docker_compose(args.command)
            else:
                logging.error("The passed config file was invalid. Refusing to run.")
        case "down":
            run_docker_compose(args.command)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
