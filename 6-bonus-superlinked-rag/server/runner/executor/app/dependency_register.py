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

from xmlrpc.client import ServerProxy

import inject

from executor.app.configuration.app_config import AppConfig
from executor.app.service.data_loader import DataLoader
from executor.app.service.file_handler_service import FileHandlerService
from executor.app.service.file_object_serializer import FileObjectSerializer
from executor.app.service.persistence_service import PersistenceService
from executor.app.service.supervisor_service import SupervisorService


def register_dependencies() -> None:
    inject.configure(_configure)


def _configure(binder: inject.Binder) -> None:
    app_config = AppConfig()
    file_handler_service = FileHandlerService(app_config)
    serializer = FileObjectSerializer(file_handler_service)
    server_proxy = ServerProxy(app_config.SERVER_URL)
    binder.bind(DataLoader, DataLoader(app_config))
    binder.bind(PersistenceService, PersistenceService(serializer))
    binder.bind(SupervisorService, SupervisorService(server_proxy))
