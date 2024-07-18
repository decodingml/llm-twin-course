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

"""Module for polling storage services and downloading updated files."""

import argparse

from poller.app.poller.poller import Poller

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the poller with a given config file.")
    parser.add_argument(
        "--config_path",
        help="Path to the configuration file.",
        default="../config/config.yaml",
    )
    args = parser.parse_args()

    poller = Poller(args.config_path)
    poller.run()
