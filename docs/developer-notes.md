
# Development Environment Setup

## Create a conda environment

    We recommend 'conda' (specifically miniconda) but that's optional of course. All that's really required is Python.

    conda create -n quanta_agent python=3.11.5
    conda activate quanta_agent

Don't forget to activate your "quanta_agent" environment in your IDE. IDE's like VSCode, require you to choose the Python interpreter, so simply running 'conda activate quanta_agent' won't be enough.


# Config File

The current `config.py` will automatically find the API keys from `..\secrets\secrets.yaml` (outside this project), and it's not recommended to put them directly into config.yaml itself, because of risk of accidental commits to the repository.

## update_strategy Option

NOTE: The default config setting for the `update_strategy` config option is `whole_file` (not `injection_points`). When you run the tool you have to set this option to tell it whether it should try to update files based on `Injection Points` or `Whole Files`. The `whole_file` option lets you ask the AI to essentially edit one or more files for you and it will overwrite your existing file(s) with new content as it sees fit based on what you asked it to do in your prompt, where as `injection_points` tells the tool to only insert code where you've defined an injection point in the code.


# AI Dry-Run Testing

If you want to run the app to do development/testing without making actual calls to OpenAI, you can set `dry_run=True` in `app_openai.py` and then put into your `[data_folder]/dry-run-answer.txt` whatever you want to simulate as an answer gotten back from the AI, and the tool will automatically use that answer file content instead of calling the OpenAI API


# pytest Testing

This project doesn't yet contain full pytest testing, but just has a couple of pytest examples to prove pytest is working.

You can install pytest with:

    pip install pytest

Then run in the root of the project with:

    pytest -vs

## Troubleshooting

If you run `pytest` with another argument other than -v, -s, or comfig parameters and it throws an error you should just look in `app_config.py` to see how to add support for aguments. It will fail on any unrecognized arguments.


# PIP Tips: Managing Module Versions

Current installed modules can be gathered into `requirements.txt` using this:

    pip freeze > requirements.txt

To install the current requirements that are published with this project run this:

    pip install -r requirements.txt

To show all outdated modules:

    pip list --outdated

To upgrade one module:

    pip install --upgrade <package_name>

To upgrade all modules at once:

    Warning this can be dangerous, and break things;

    pip list --outdated | grep -v '^\-e' | awk '{print $1}' | xargs -n1 pip install -U


## Troubleshooting:

If you get ERROR: 

pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
langchain-core 0.1.50 requires packaging<24.0,>=23.2, but you have packaging 24.0 which is incompatible.

Then fix it with this:

    pip install 'packaging>=23.2,<24.0'


# Python & Langchain Resources

https://python.langchain.com/docs/get_started/introduction/

https://python.langchain.com/docs/integrations/chat/openai/


