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

# Temporary ignore due to vdb connector access. Fix in: FAI-1961
# ruff: noqa: SLF001

import logging
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager

import inject
from fastapi import FastAPI
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.space.recency_space import RecencySpace
from superlinked.framework.storage.in_memory.in_memory_vdb import InMemoryVDB

from executor.app.configuration.app_config import AppConfig
from executor.app.service.data_loader import DataLoader
from executor.app.service.persistence_service import PersistenceService
from executor.app.util.fast_api_handler import FastApiHandler
from executor.app.util.registry_loader import RegistryLoader

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handle the lifecycle of the application.
    All the setup should be done before the yield, then the teardown happens after the yield.
    Only graceful shutdown will let the teardown happen.
    """
    setup_application(app)
    yield
    teardown_application(app)


def setup_application(app: FastAPI) -> None:
    persistence_service = inject.instance(PersistenceService)
    data_loader = inject.instance(DataLoader)
    app_config = inject.instance(AppConfig)

    if registry := RegistryLoader.get_registry(app_config.APP_MODULE_PATH):
        for executor in registry.get_executors():
            if isinstance(executor, RestExecutor):
                logger.info("Found an executor, registering the endpoints")
                if has_recency_space(executor._indices) and app_config.DISABLE_RECENCY_SPACE:
                    msg = (
                        "RecencySpace found in Index but is disabled. "
                        "Either enable RecencySpace or remove it from the Index."
                    )
                    raise ValueError(msg)
                try:
                    rest_app = executor.run()
                except Exception:  # pylint: disable=broad-exception-caught
                    msg = "An error occurred during app execution."
                    logger.exception(msg)
                    return
                if rest_app.data_loader_sources:
                    data_loader.register_data_loader_sources(rest_app.data_loader_sources)
                if isinstance(rest_app.online_app.storage_manager._vdb_connector, InMemoryVDB):
                    persistence_service.register(rest_app)
                fast_api_handler = FastApiHandler(rest_app.handler)

                for path in rest_app.handler.ingest_paths:
                    app.add_api_route(path=path, endpoint=fast_api_handler.ingest, methods=["POST"])

                for path in rest_app.handler.query_paths:
                    app.add_api_route(path=path, endpoint=fast_api_handler.query, methods=["POST"])
    persistence_service.restore()


def teardown_application(_: FastAPI) -> None:
    persistence_service = inject.instance(PersistenceService)
    logger.info("Shutdown event detected. Persisting the database")
    persistence_service.persist()


# Temporary recency space deactivation. Refer to: FAI-1965 for details
def has_recency_space(indices: Sequence[Index]) -> bool:
    return any(
        isinstance(space, RecencySpace) for index in indices if hasattr(index, "__spaces") for space in index.__spaces
    )
