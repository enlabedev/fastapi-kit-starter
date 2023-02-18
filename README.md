<!-- omit in toc -->
# FASTAPI KIT STARTER
FASTAPI KIT STARTER is a project optimized to work with Visual Studio Code

<!-- omit in toc -->
## Table of contents

- [Initial steps](#initial-steps)
- [Setup git](#setup-git)
- [Set up environment](#set-up-environment)
- [Style guides](#style-guides)
- [Reset migrations](#reset-migrations)


## Initial steps

If you're going to contribute to this repo, follow the steps below.

- Set up your git config locally.
- Read style guide docs.
- Set up all tools needed.
- Edit the `.vscode/settings.json` file according to your OS.
- Interact with the database.

## Setup git

Set a name on your `local` git config

```bash
# e.g.:
$ git config --local user.name "{{ first name }} {{ last name }}"
```

Set an email on your `local` git config

```bash
# suggestion, use your private GitHub email
# e.g.:
$ git config --local user.email "xxxxxxxxxx@users.noreply.github.com"
```

Set a pull strategy on your `local` git config, avoid a warning on every `git pull` since version `2.27`

```bash
$ git config --local pull.rebase false
```

References:

- [How to deal with this git warning? “Pulling without specifying how to reconcile divergent branches is discouraged”](https://stackoverflow.com/q/62653114/)


## Set up environment
Install and set the right python version
```bash
curl https://pyenv.run | bash
pyenv install 3.11.1
pyenv local 3.11.1
```
Install and set poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry env use 3.11.1
poetry shell
poetry install
```

Use the poetry to locally run the web app
```bash
cp .env.example .env
nano .env # Modify connection
alembic upgrade head
poetry run start
```

## Style guides

In the Python ecosystem, it is strongly suggested to use [PEP 8](https://www.python.org/dev/peps/pep-0008/), which is a list of suggestions to follow on any Python code. The tool that we use as a `linter` to enforce this suggestion is [flake8](https://github.com/PyCQA/flake8).

After that, considering that we are going to use [FastAPI](https://fastapi.tiangolo.com/) as a web framework. One of the suggestions is to use [isort](https://github.com/PyCQA/isort) to enforce a specific sort of technique on `import` statements

Part of the standardization that we have as a team, we're going to use [black](https://github.com/psf/black) as the code formatting, to complement PEP8 with its [code style](https://black.readthedocs.io/en/stable/the_black_code_style.html)

References:

- [zedr/clean-code-python](https://github.com/zedr/clean-code-python) - Code Cleand used in Python
- [mjhea0/awesome-fastapi](https://github.com/mjhea0/awesome-fastapi) - Multiple resources for FastAPI
- [Things about Python](https://gist.github.com/eevmanu/b2c8c49b79f02cdc1f764c1d9bdfa320)
- [JSON Naming Convention (snake_case, camelCase or PascalCase) [closed]](https://stackoverflow.com/q/5543490/)

## Reset migrations

- Delete all migrations files
- Run `alembic revision --autogenerate` command
- Clean database, recreate if needed
- Apply changes with `alembic upgrade head` command
