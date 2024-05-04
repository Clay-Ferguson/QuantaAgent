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


# TROUBLESHOOTING:

If you get ERROR: 

pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
langchain-core 0.1.50 requires packaging<24.0,>=23.2, but you have packaging 24.0 which is incompatible.

Then fix it with this:

    pip install 'packaging>=23.2,<24.0'
