import click

from faker import Faker
from flask.cli import with_appcontext

from .extensions import db
from .models import User

fake = Faker()

@click.command(name = 'create_tables')
@with_appcontext
def create_tables():
    """Create the database tables."""
    db.create_all()
    click.echo('Database tables created successfully.')
