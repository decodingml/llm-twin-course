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
import shutil
from datetime import datetime, timezone

from poller.app.resource_handler.resource_handler import ResourceHandler


class LocalResourceHandler(ResourceHandler):
    def get_bucket(self) -> str:
        return "local"

    def download_file(self, _: str | None, object_name: str, download_path: str) -> None:
        """
        'Download' a file from local storage to the specified path.
        In this case, it's just copying the file.
        """
        self.logger.info("Copy file from %s to %s", object_name, download_path)
        shutil.copy2(object_name, download_path)

    def poll(self) -> None:
        """
        Poll files from a local directory and notify about new or modified files.
        """
        self.logger.info("Polling files from: %s", self.app_location.path)
        if not self._path_exists():
            self.logger.error("Path does not exist: %s", self.app_location.path)
            return
        self._process_path()

    def _path_exists(self) -> bool:
        return os.path.exists(self.app_location.path)

    def _process_path(self) -> None:
        if os.path.isfile(self.app_location.path):
            self._process_file(self.app_location.path)
        else:
            self._process_directory()

    def _process_directory(self) -> None:
        for root, _, files in os.walk(self.app_location.path):
            for file in files:
                file_path = os.path.join(root, file)
                self._process_file(file_path)

    def _process_file(self, file_path: str) -> None:
        self.logger.info("Found file: %s", file_path)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
        try:
            self.check_and_download(file_time, self.app_location.path)
        except (FileNotFoundError, PermissionError):
            self.logger.exception("Failed to download and notify new version")
