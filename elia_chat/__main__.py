"""
Elia CLI
"""

import pathlib
from typing import Tuple

import click

from elia_chat.app import Elia
from elia_chat.config import LaunchConfig
from elia_chat.database.create_database import create_database
from elia_chat.database.import_chatgpt import import_chatgpt_data
from elia_chat.database.models import sqlite_file_name
from elia_chat.launch_args import QuickLaunchArgs
from elia_chat.models import DEFAULT_MODEL, MODEL_MAPPING


@click.group(invoke_without_command=True)
@click.pass_context
def cli(context: click.Context) -> None:
    """
    Elia: A terminal ChatGPT client built with Textual
    """
    # TODO - we should pull defaults from a file
    app = Elia(LaunchConfig())
    # Run the app if no subcommand is provided

    if context.invoked_subcommand is None:
        # Create the database if it doesn't exist
        # TODO - we should run a migration file so we can update
        #  the end users database when required.
        if sqlite_file_name.exists() is False:
            create_database()
        app.run()


@cli.command()
def reset() -> None:
    """
    Reset the database

    This command will delete the database file and recreate it.
    Previously saved conversations and data will be lost.
    """
    sqlite_file_name.unlink(missing_ok=True)
    create_database()
    click.echo(f"♻️  Database reset @ {sqlite_file_name}")


@cli.command("import")
@click.argument(
    "file",
    type=click.Path(
        exists=True, dir_okay=False, path_type=pathlib.Path, resolve_path=True
    ),
)
def import_file_to_db(file: pathlib.Path) -> None:
    """
    Import ChatGPT Conversations

    This command will import the ChatGPT conversations from a local
    JSON file into the database.
    """
    import_chatgpt_data(file=file)
    click.echo(f"✅  ChatGPT data imported into database {file}")


@cli.command()
@click.argument("message", nargs=-1, type=str, required=True)
@click.option(
    "-m",
    "--model",
    type=click.Choice(choices=list(MODEL_MAPPING.keys())),
    default=DEFAULT_MODEL.name,
    help="The model to use for the chat",
)
def chat(message: Tuple[str, ...], model: str) -> None:
    """
    Start Elia with a chat message
    """
    quick_launch_args = QuickLaunchArgs(
        launch_prompt=" ".join(message),
        launch_prompt_model_name=model,
    )
    launch_config = LaunchConfig(
        default_model=quick_launch_args.launch_prompt_model_name,
    )
    app = Elia(launch_config, quick_launch_args.launch_prompt)
    app.run()


if __name__ == "__main__":
    cli()
