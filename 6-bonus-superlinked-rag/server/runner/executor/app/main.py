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
from json import JSONDecodeError

import uvicorn
from fastapi import FastAPI
from fastapi_restful.timing import add_timing_middleware
from superlinked.framework.common.parser.exception import MissingIdException
from superlinked.framework.online.dag.exception import ValueNotProvidedException

from executor.app.configuration.app_config import AppConfig
from executor.app.dependency_register import register_dependencies
from executor.app.exception.exception_handler import (
    handle_bad_request,
    handle_generic_exception,
)
from executor.app.middleware.lifespan_event import lifespan
from executor.app.router.management_router import router as management_router

app_config = AppConfig()

logging.basicConfig(level=app_config.LOG_LEVEL)
logger = logging.getLogger(__name__)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(ValueNotProvidedException, handle_bad_request)
app.add_exception_handler(MissingIdException, handle_bad_request)
app.add_exception_handler(JSONDecodeError, handle_bad_request)
app.add_exception_handler(Exception, handle_generic_exception)

app.include_router(management_router)

add_timing_middleware(app, record=logger.info)

register_dependencies()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104 hardcoded-bind-all-interfaces
