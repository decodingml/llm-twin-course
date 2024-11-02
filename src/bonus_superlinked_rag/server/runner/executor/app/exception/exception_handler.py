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

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def handle_bad_request(_: Request, exception: Exception) -> JSONResponse:
    logger.exception("Bad request")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "exception": str(exception.__class__.__name__),
            "detail": str(exception),
        },
    )


async def handle_generic_exception(_: Request, exception: Exception) -> JSONResponse:
    logger.exception("Unexpected exception happened")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "exception": str(exception.__class__.__name__),
            "detail": str(exception),
        },
    )
