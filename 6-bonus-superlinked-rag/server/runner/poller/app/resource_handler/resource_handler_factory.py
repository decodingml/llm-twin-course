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

from poller.app.app_location_parser.app_location_parser import AppLocation, StorageType
from poller.app.resource_handler.gcs.gcs_resource_handler import GCSResourceHandler
from poller.app.resource_handler.local.local_resource_handler import (
    LocalResourceHandler,
)
from poller.app.resource_handler.resource_handler import ResourceHandler
from poller.app.resource_handler.s3.s3_resource_handler import S3ResourceHandler


class ResourceHandlerFactory:
    @staticmethod
    def get_resource_handler(app_location: AppLocation) -> ResourceHandler:
        match app_location.type_:
            case StorageType.S3:
                return S3ResourceHandler(app_location)
            case StorageType.GCS:
                return GCSResourceHandler(app_location)
            case StorageType.LOCAL:
                return LocalResourceHandler(app_location)
            case _:
                msg = f"Invalid resource type in config: {app_location.type_}"
                raise ValueError(msg)
