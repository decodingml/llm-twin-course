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

import configparser
import logging
import logging.config


class PollerConfig:
    def __init__(self) -> None:
        poller_dir = "poller"
        poller_config_path = f"{poller_dir}/poller_config.ini"
        logging_config_path = f"{poller_dir}/logging_config.ini"

        config = configparser.ConfigParser()
        config.read(poller_config_path)

        self.poll_interval_seconds = config.getint("POLLER", "POLL_INTERVAL_SECONDS")
        self.executor_port = config.getint("POLLER", "EXECUTOR_PORT")
        self.executor_url = config.get("POLLER", "EXECUTOR_URL")
        self.aws_credentials = config.get("POLLER", "AWS_CREDENTIALS")
        self.gcp_credentials = config.get("POLLER", "GCP_CREDENTIALS")
        self.download_location = config.get("POLLER", "DOWNLOAD_LOCATION")
        self.logging_config = logging_config_path

    def setup_logger(self, name: str) -> logging.Logger:
        logging.config.fileConfig(self.logging_config)
        return logging.getLogger(name)
