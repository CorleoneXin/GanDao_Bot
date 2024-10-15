# GanDao_Bot

## Run the Bot
- Make sure [poetry](https://python-poetry.org) is installed on your system.

<!-- 
poetry env list  # shows the name of the current environment
poetry env remove <current environment>
poetry install  # will create a new environment using your updated configuration
 -->

poetry config virtualenvs.in-project true
poetry install

## Dev mode

- Run: `poetry run python -m src.main --dev` or execute the `main` function directly in your debugger which will default to `dev` mode. (make sure the environment is activated by running `poetry shell` first)

## Production mode

Production mode runs alembic migrations against your database before starting the bot, make sure the following environment variables are set:

- `BOT_TOKEN` you can get one from **_[Botfather](https://t.me/botfather)_**
- `DB_PATH` the path to your database, relative from where the bot is executing. (I recommend choosing `/data/yourdb.sqlite3`, as a `/data` directory is automatically created in the Docker container and can be mounted to a persistent volume)
- `FIRST_ADMIN` your `telegram_id`, this can be set to give you automatically the `ADMIN` role when you register in your own bot

The following are optional:
- `LOGGING_CHANNEL` a *telegram* `chat_id` that the `ErrorForwarder` can use to send *JSON* logs to. Very useful, usually set to a shared channel or your own id.

Finally:

- Execute `./entrypoint.sh`
