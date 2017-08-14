import click

from app.extensions import db


def initialize_cli(app):

    @app.cli.command()
    def init_db():
        click.echo('Initializing the db')
        db.create_all()

    @app.cli.command()
    def clear_db():
        """
        Removes all the tables of the database and their content
        """
        click.echo('Clearing the db')
        db.drop_all()
        click.echo('Initializing the db')
        db.create_all()


