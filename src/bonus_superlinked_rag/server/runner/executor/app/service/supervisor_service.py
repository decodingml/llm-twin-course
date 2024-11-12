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


class SupervisorService:
    def __init__(self, server_proxy: ServerProxy) -> None:
        self.server = server_proxy

    def restart(self) -> str:
        """Restart the API via supervisor XML-RPC and return the result."""
        return str(self.server.supervisor.restart())
