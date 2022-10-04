# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import subprocess
import os
import logging
import sys
import re
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Sh:
    def __init__(self, env=None, cwd=None):
        self.env = os.environ.copy()
        if env is not None:
            self.env.update(env)
        self.cwd = cwd

    def run(self, cmd: str, **kwargs):
        logging.getLogger("py-github").info(f"+ {cmd}")
        defaults = {
            "check": True,
            "shell": True,
            "env": self.env,
            "encoding": "utf-8",
            "cwd": self.cwd,
        }
        defaults.update(kwargs)

        return subprocess.run(cmd, **defaults)


def tags_from_title(title: str) -> List[str]:
    tags = re.findall(r"\[(.*?)\]", title)
    tags = [t.strip() for t in tags]
    final_tags = []
    for tag in tags:
        comment_tags = [t.strip() for t in tag.split(",")]
        final_tags.extend([t for t in comment_tags if t != ""])
    return final_tags
