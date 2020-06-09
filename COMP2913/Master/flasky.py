import os
import click
from flask_migrate import Migrate

from app import create_app, db
import app.models as models

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, models=models)


@app.context_processor
def inject_facilities():
    return dict(facilities=models.Facility.query.all())


@app.template_filter()
def currency(value):
    return "£{:,.2f}".format(value)


@app.template_filter()
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)


@app.template_filter()
def timeformat(value, format='%H:%M'):
    return datetimeformat(value, format=format)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
