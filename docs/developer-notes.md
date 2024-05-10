# AI Dry-Run Testing

If you want to run the app to do development/testing without making actual calls to OpenAI, you can set `dry_run=True` in `app_openai.py` and then put into your `[data_folder]/dry-run-answer.md` whatever you want to simulate as an answer gotten back from the AI, and the tool will automatically use that answer file content instead of calling the OpenAI API


# Testing

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



