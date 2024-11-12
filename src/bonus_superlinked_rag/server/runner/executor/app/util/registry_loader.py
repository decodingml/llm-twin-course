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
from importlib import import_module

from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry

logger = logging.getLogger(__name__)


class RegistryLoader:
    @staticmethod
    def get_registry(app_module_path: str) -> SuperlinkedRegistry | None:
        try:
            return import_module(app_module_path).SuperlinkedRegistry
        except ImportError:
            logger.exception("Module not found at: %s", app_module_path)
        except AttributeError:
            logger.exception("SuperlinkedRegistry not found in module: %s", app_module_path)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("An unexpected error occurred while loading the module at: %s", app_module_path)
        return None
