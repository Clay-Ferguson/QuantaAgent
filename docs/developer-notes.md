
# Development Environment Setup

## Latest Project News!

Quanta Agent is now using a Langchain Agent with Tools, to perform all file editing that it does to your code (i.e. editing of your files)!! This is a huge advancement!!

We initially developed this project using only formatting of the prompts and responses (i.e. old-school `Prompt Engineering`) to accomplish refactoring of code, and we still support the "non-Tool and non-Agentic" way of doing things, so that we can be sure to keep supporting LLMs for which there is no Langchain Agent and/or Tool support. So we will keep that legacy (i.e. a whole week old!) code in place until we're sure we can go 100% with Langchain Agents and Tools going forward, which will happen very likely during the next year.

We still have non-agentic code for detecting `block(), file() and folder()` references in your prompts and injecting those blocks, files, and folders directly into the prompt, and we will possibly never make that part agentic, because replacing those parts of a prompt with contents of your files doesn't require any intelligence or need to be in the Agent's set of tools. In other words if you reference `file(/my/file/name.py)` in your promt we detect that manually and replace it with the content of the file right into the prompt itself, although theoretically we could be using an agent to do that.

So the part of this codebase that has been converted to "Agentic" is just the part where the LLM decides what code to create or write. All of that reply logic to write to your files, is, as stated, fully Langchain Agentic and Tools based.


## Create a conda environment

    We recommend 'conda' (specifically miniconda) but that's optional of course. All that's really required is Python.

    conda create -n quanta_agent python=3.11.5
    conda activate quanta_agent

Don't forget to activate your "quanta_agent" environment in your IDE. IDE's like VSCode, require you to choose the Python interpreter, so simply running 'conda activate quanta_agent' won't be enough.


# Config File

The current `config.py` will automatically find the API keys from `..\secrets\secrets.yaml` (outside this project), and it's not recommended to put them directly into config.yaml itself, because of risk of accidental commits to the repository.

## mode Option

NOTE: The default config setting for the `mode` option is `files`. When you run the tool you have to set this option to tell it whether it should try to update files based on updating entire files (`mode="file"`), or only by updating only `Named Blocks` in files (`mode="blocks"`).


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


