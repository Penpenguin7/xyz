# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Description: An RNN model for generating drum tracks.

licenses(["notice"])  # Apache 2.0

py_binary(
	name = "piano_to_drum_create_dataset",
	srcs = ["piano_to_drum_create_dataset.py"],
	visibility = [
        "//magenta/tools/pip:__subpackages__",
    ],
    deps = [
	"//magenta",
    "//magenta/models/drums_rnn:drums_rnn_config_flags",
    "//magenta/music",
    "//magenta/pipelines",
    ":melody_rnn_config_flags",
	],
)

py_library(
    name = "melody_rnn_config_flags",
    srcs = ["melody_rnn_config_flags.py"],
    srcs_version = "PY2AND3",
    visibility = [
        # internal model:drums_rnn
    ],
    deps = [
        "//magenta/models/melody_rnn:melody_rnn_model",
        "//magenta",
        # tensorflow dep
    ],
)

