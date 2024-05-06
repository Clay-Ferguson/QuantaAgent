# Notest about Testing

You can install pytest with:

    pip install pytest

Then run in the root of the project with:

    pytest -vs

## Troubleshooting

If you run pytest with another argument other than -v, -s, or comfig parameters and it throws an error you should just look in `app_config.py` to see how we need to add support for aguments. It will fail on any unrecognized arguments.
