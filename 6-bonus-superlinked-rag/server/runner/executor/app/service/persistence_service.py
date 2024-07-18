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

import logging

from superlinked.framework.dsl.executor.rest.rest_executor import RestApp

from executor.app.service.file_object_serializer import FileObjectSerializer

logger = logging.getLogger(__name__)


class PersistenceService:
    def __init__(self, serializer: FileObjectSerializer) -> None:
        self._applications: list[RestApp] = []
        self._serializer = serializer

    def register(self, rest_app: RestApp) -> None:
        if rest_app in self._applications:
            logger.warning("Application already exists: %s", rest_app)
            return
        logger.info("Rest app registered: %s", rest_app)
        self._applications.append(rest_app)

    def persist(self) -> None:
        for app in self._applications:
            app.online_app.persist(self._serializer)

    def restore(self) -> None:
        for app in self._applications:
            app.online_app.restore(self._serializer)
