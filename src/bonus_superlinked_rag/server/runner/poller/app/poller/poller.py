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

import time
from threading import Thread

import yaml

from poller.app.app_location_parser.app_location_parser import (
    AppLocation,
    AppLocationParser,
)
from poller.app.config.poller_config import PollerConfig
from poller.app.resource_handler.resource_handler_factory import ResourceHandlerFactory


class Poller(Thread):
    """
    The Poller class is a thread that polls files from different types of storage: local, S3,
    and Google Cloud Storage at a regular interval.
    """

    def __init__(self, config_path: str) -> None:
        Thread.__init__(self)
        self.poller_config = PollerConfig()
        self.app_location_config_path = config_path
        self.app_location_config = self.parse_app_location_config()

    def parse_app_location_config(self) -> AppLocation:
        """
        Parse the configuration from the YAML file.
        """
        with open(self.app_location_config_path, encoding="utf-8") as file:
            config_yaml = yaml.safe_load(file)
        app_location = config_yaml["app_location"]
        return AppLocationParser().parse(app_location)

    def run(self) -> None:
        """
        Start the polling process.
        """
        resource_handler = ResourceHandlerFactory.get_resource_handler(self.app_location_config)
        while True:
            if resource_handler.check_api_health():
                resource_handler.poll()
            time.sleep(self.poller_config.poll_interval_seconds)
