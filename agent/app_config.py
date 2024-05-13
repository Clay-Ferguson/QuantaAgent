"""Loads configuration from config.yaml and secrets.yaml files."""

import os
import re
import configargparse


class AppConfig:
    """Loads configuration from config.yaml and secrets.yaml files."""

    ext_list = []
    ext_set = set()

    STRATEGY_WHOLE_FILE = "whole_file"
    STRATEGY_INJECTION_POINTS = "injection_points"

    @classmethod
    def get_config(cls, config_file=None):
        """Loads configuration from config.yaml and secrets.yaml files."""

        # Both of these config files are optional, because the ArgParser can load
        # from command line arguments or environment variables as well.
        if config_file is None:
            config_file = "config/config.yaml"
        secrets_file = "../secrets/secrets.yaml"

        if not os.path.exists(config_file):
            print(f"WARNING: File not found: {config_file}")

        if not os.path.exists(secrets_file):
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
        p.add_argument("--system_prompt", required=True, help="AI query system prompt")
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
            "--update_strategy",
            required=True,
            help="Update strategy for the files (whole_file or injection_points)",
        )
        p.add_argument(
            "--max_prompt_length", required=True, help="Max characters in prompt"
        )

        options = p.parse_args()

        AppConfig.ext_list = re.split(r"\s*,\s*", options.scan_extensions)
        AppConfig.ext_set = set(AppConfig.ext_list)
        # print(f"Config loaded: {config_file}")
        return options
