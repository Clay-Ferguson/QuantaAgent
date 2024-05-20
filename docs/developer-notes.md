
# Development Environment Setup

## Architectural and Design Notes

### No Langchain `Tool Use`? Why not?

This app doesn't use any **Langchain Tools or Function Calling**, but instead uses more conventional prompt engineering. Tool use in Langchain is still only reliable when the message has only one single directive per prompt.

For example with Langchain Tools enabled for updating code blocks, a prompt like "Save a block with name 'myblock' and content 'My Block Conent'" works well and generates a call to the correct tool with the correct arguments. However if you do that same prompt but with one more sentence added like perhaps "And tell me what is 1+1?" then the Langchain Tool calling mechanism will fail to generate the block saving function call.

The Quanta Agent therefore cannot use Langchain Tools because our goal is go allow a free flow conversation between a developer and the Agent. So our instructions to the agent (System Prompt) simply tell the agent how to embed updates into it's normal conversational flow, and those embedded formats are detected by us and whatever calls we need to do (updating and/or creating source files) we handle ourselves.

There's actually a lot of moving parts in Tool Calling AI systems as well, and not all LLMs support it. Since we can give more clear instructions in a single System Prompt that will work on any LLM we therefore also benefit by not only keeping things simpler with our non-tool approach, but we also achieve better compatibility with all LLMs.

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


