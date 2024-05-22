"""Loads configuration from config.yaml and secrets.yaml files."""

import os
import re
from typing import List, Set, Optional
import argparse
import configargparse


class AppConfig:
    """Loads configuration from config.yaml and secrets.yaml files."""

    tool_use = True

    # WARNING: If you set agentic to FALSE here and you want tools recognized (but not called) be sure to
    # uncomment the `@tool` annotation in this code where you see it, and also beware that will break the code
    # because we don't have the ability to actually EXECUTE the tool calls that the LLM will inject into it's
    # responses. So this app can run only with agentic and tool_use BOTH set to True, or both set to false. Setting
    # both to false should allow the app to run using basic prompt engineering and parsing of outputs, but no Langchain
    # tool calls will be recognized or executed.
    agentic = True

    ext_list: List[str] = []
    ext_set: Set[str] = set()

    MODE_FILES: str = "files"
    MODE_BLOCKS: str = "blocks"

    @classmethod
    def get_config(cls, config_file: Optional[str] = None) -> argparse.Namespace:
        """Loads configuration from config.yaml and secrets.yaml files."""

        # Both of these config files are optional, because the ArgParser can load
        # from command line arguments or environment variables as well.
        if config_file is None:
            config_file = "config/config.yaml"
        secrets_file: str = "../secrets/secrets.yaml"

        if not os.path.isfile(config_file):
            print(f"WARNING: File not found: {config_file}")

        if not os.path.isfile(secrets_file):
            print(f"WARNING: File not found: {secrets_file}")

        p = configargparse.ArgParser(default_config_files=[config_file, secrets_file])
        p.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose output"
        )
        p.add_argument(
            "-s",
            "--capture-output",
            action="store_true",
            help="Disable capturing of stdout/stderr",
        )
        p.add_argument(
            "-c",
            "--config",
            required=False,
            is_config_file=True,
            help="config file path",
        )
        p.add_argument("--openai_api_key", required=True, help="API key for OpenAI")
        p.add_argument("--openai_model", required=True, help="OpenAI model name")
        p.add_argument(
            "--scan_extensions",
            required=True,
            help="Comma separated list of file extensions to scan",
        )
        p.add_argument(
            "--data_folder",
            required=True,
            help="Holds the question.txt file and also all generated response files",
        )
        p.add_argument(
            "--source_folder", required=True, help="Folder with source files to scan"
        )
        p.add_argument(
            "--mode",
            required=True,
            help="Update mode for the files (files or blocks)",
        )
        p.add_argument(
            "--max_prompt_length", required=True, help="Max characters in prompt"
        )

        options = p.parse_args()

        AppConfig.ext_list = re.split(r"\s*,\s*", options.scan_extensions)
        AppConfig.ext_set = set(AppConfig.ext_list)
        return options
