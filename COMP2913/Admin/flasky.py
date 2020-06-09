import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission,Membership_type,Membership,Facility,Credit_card_info,Activity,Account,Booking,Time_management

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission,Membership_type=Membership_type,Membership=Membership,
                Facility=Facility,Booking=Booking,Time_management=Time_management,Activity=Activity,Credit_card_info=Credit_card_info,
                Account=Account)


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
