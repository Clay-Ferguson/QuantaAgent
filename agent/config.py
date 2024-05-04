"""Loads configuration from config.yaml and secrets.yaml files."""

import os
import configargparse


def get_config():
    """Loads configuration from config.yaml and secrets.yaml files."""

    # Both of these config files are optional, because the ArgParser can load
    # from command line arguments or environment variables as well.
    config_file = "config/config.yaml"
    secrets_file = "../secrets/secrets.yaml"

    if not os.path.exists(config_file):
        print(f"WARNING: File not found: {config_file}")

    if not os.path.exists(secrets_file):
        print(f"WARNING: File not found: {secrets_file}")

    p = configargparse.ArgParser(default_config_files=[config_file, secrets_file])
    p.add(
        "-c", "--config", required=False, is_config_file=True, help="config file path"
    )
    p.add("--openai_api_key", required=True, help="API key for OpenAI")
    p.add("--openai_model", required=True, help="OpenAI model name")
    p.add("--system_prompt", required=True, help="AI query system prompt")
    p.add(
        "--scan_extensions",
        required=True,
        help="Comma separated list of file extensions to scan",
    )
    p.add(
        "--data_folder",
        required=True,
        help="Holds the question.md file and also all generated response files",
    )
    p.add("--source_folder", required=True, help="Folder with source files to scan")

    options = p.parse_args()
    return options
