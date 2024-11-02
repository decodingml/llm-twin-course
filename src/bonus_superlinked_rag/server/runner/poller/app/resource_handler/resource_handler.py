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

import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests
from botocore.exceptions import ClientError
from google.cloud.exceptions import GoogleCloudError

from poller.app.app_location_parser.app_location_parser import AppLocation
from poller.app.config.poller_config import PollerConfig


class ResourceHandler(ABC):
    def __init__(self, app_location: AppLocation) -> None:
        self.app_location = app_location
        self.start_time = datetime.now(tz=timezone.utc)
        self.first_run = True
        self.poller_config = PollerConfig()
        self.logger = self.poller_config.setup_logger(__name__)

    @abstractmethod
    def poll(self) -> None:
        pass

    @abstractmethod
    def download_file(self, bucket_name: str | None, object_name: str, download_path: str) -> None:
        pass

    def get_bucket(self) -> str:
        if self.app_location.bucket is None:
            msg = "Bucket name is None"
            raise ValueError(msg)
        return self.app_location.bucket

    def convert_to_utc(self, dt: datetime) -> datetime:
        """
        Convert a datetime object to UTC timezone.
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def check_and_download(self, object_time: datetime, object_name: str) -> None:
        """
        Check if the object's time is more recent than the poller's start time and download it if so.
        If it's the first run, download the object regardless of its time.
        After downloading, call the executor API's /reload endpoint with a PUT request.
        """
        self.start_time = self.convert_to_utc(self.start_time)
        object_time = self.convert_to_utc(object_time)

        if self.first_run or object_time > self.start_time:
            filename = os.path.basename(object_name.lstrip("/"))
            download_path = os.path.join(self.poller_config.download_location, filename)
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            try:
                self.download_file(self.get_bucket(), object_name, download_path)
                self.logger.info("Downloaded %s to %s", object_name, download_path)
                self.notify_executor(object_name)
                self.start_time = datetime.now(tz=timezone.utc)
            except (OSError, ClientError, GoogleCloudError):
                self.logger.exception("Failed to download %s", object_name)

        if self.first_run:
            self.first_run = False
            self.start_time = datetime.now(tz=timezone.utc)

    def notify_executor(self, object_name: str) -> None:
        """
        Notify the executor API about the new version by making a PUT request to /reload.
        """
        api_url = f"{self.poller_config.executor_url}:{self.poller_config.executor_port}/reload"
        data = {"object_name": object_name}
        response = None
        try:
            response = requests.post(api_url, json=data, timeout=10)
            response.raise_for_status()
            self.logger.info(
                "Successfully notified executor about new version of %s",
                object_name,
            )
        except requests.HTTPError:
            self.logger.exception(
                "Failed to notify executor about new version of %s. Status code: %s",
                object_name,
                response.status_code if response else "No response received",
            )
        except requests.RequestException:
            self.logger.exception(
                "Failed to notify executor about new version of %s",
                object_name,
            )

    def check_api_health(self) -> bool:
        """
        Check the health of the API and return True if it's healthy, False otherwise.
        """
        api_endpoint = f"{self.poller_config.executor_url}:{self.poller_config.executor_port}/health"
        try:
            response = requests.get(api_endpoint, timeout=10)
            response.raise_for_status()
        except (requests.HTTPError, requests.RequestException) as e:
            self.logger.warning("API is not healthy! Error: %s", e)
            return False
        return True
