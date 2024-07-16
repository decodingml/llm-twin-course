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

import asyncio
import logging
import traceback
from collections.abc import Sequence
from typing import Any

import pandas as pd
from pandas.io.json._json import JsonReader
from pandas.io.parsers import TextFileReader
from pydantic.alias_generators import to_snake
from superlinked.framework.dsl.source.data_loader_source import DataFormat, DataLoaderConfig, DataLoaderSource

from executor.app.configuration.app_config import AppConfig
from executor.app.exception.exception import (
    DataLoaderAlreadyRunningException,
    DataLoaderNotFoundException,
    DataLoaderTaskNotFoundException,
)

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, app_config: AppConfig) -> None:
        self._app_config = app_config
        self._data_loader_sources: dict[str, DataLoaderSource] = {}
        self._data_loader_tasks: dict[str, asyncio.Task] = {}

    def register_data_loader_sources(self, data_loader_sources: Sequence[DataLoaderSource]) -> None:
        for source in data_loader_sources:
            if source.name in self._data_loader_sources:
                logger.warning(
                    "Data loader source with the name '%s' is already registered. Skipping registration.", source.name
                )
                continue
            self._data_loader_sources[to_snake(source.name)] = source

    def get_data_loaders(self) -> dict[str, DataLoaderConfig]:
        return {name: source.config for name, source in self._data_loader_sources.items()}

    def load(self, name: str) -> None:
        data_loader_source = self._data_loader_sources.get(name)
        if not data_loader_source:
            msg = f"Data loader with name: {name} not found"
            raise DataLoaderNotFoundException(msg)
        task = self._data_loader_tasks.get(name)
        if task and not task.done():
            msg = f"Data loader already running with name: {name}"
            raise DataLoaderAlreadyRunningException(msg)
        logger.info("Starting data load for source with the following configuration: %s", data_loader_source.config)
        task = asyncio.create_task(asyncio.to_thread(self.__read_and_put_data, data_loader_source))
        self._data_loader_tasks.update({name: task})

    def get_task_status_by_name(self, name: str) -> str | None:
        task = self._data_loader_tasks.get(name)
        if task is None:
            msg = "Data loader task not found with name: %s"
            raise DataLoaderTaskNotFoundException(msg, name)

        if not task.done():
            return "Task is still running"

        if task.exception() is not None:
            if exc := task.exception():
                logger.error(traceback.format_exception(type(exc), exc, exc.__traceback__))
            return f"Task failed with exception: {task.exception()}. For traceback, check the logs."

        return "Task completed successfully"

    def __read_and_put_data(self, source: DataLoaderSource) -> None:
        data = self.__read_data(source.config.path, source.config.format, source.config.pandas_read_kwargs)
        if isinstance(data, pd.DataFrame):
            if logger.isEnabledFor(logging.DEBUG):
                data.info(memory_usage=True)
            logger.debug(
                "Data frame of size: %s has been loaded into memory. Beginning persistence process.", len(data)
            )
            source._source.put(data)  # noqa: SLF001 private-member-access
        elif isinstance(data, TextFileReader | JsonReader):
            for chunk in data:
                if logger.isEnabledFor(logging.DEBUG):
                    chunk.info(memory_usage=True)
                logger.debug(
                    "Chunk of size: %s has been loaded into memory. Beginning persistence process.", len(chunk)
                )
                source._source.put(chunk)  # noqa: SLF001 private-member-access
        else:
            error_message = (
                "The returned object from the Pandas read method was not of the "
                f"expected type. Actual type: {type(data)}"
            )
            raise TypeError(error_message)
        logger.info("Finished the data load for source with the following configuration: %s", source.config)

    def __read_data(
        self, path: str, data_format: DataFormat, pandas_read_kwargs: dict[str, Any] | None
    ) -> pd.DataFrame | TextFileReader | JsonReader:
        kwargs = pandas_read_kwargs or {}
        match data_format:
            case DataFormat.CSV:
                return pd.read_csv(path, **kwargs)
            case DataFormat.FWF:
                return pd.read_fwf(path, **kwargs)
            case DataFormat.XML:
                return pd.read_xml(path, **kwargs)
            case DataFormat.JSON:
                return pd.read_json(path, **kwargs)
            case DataFormat.PARQUET:
                return pd.read_parquet(path, **kwargs)
            case DataFormat.ORC:
                return pd.read_orc(path, **kwargs)
            case _:
                msg = "Unsupported data format: %s"
                raise ValueError(msg, data_format)
