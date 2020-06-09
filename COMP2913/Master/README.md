# COMP2913 Group 21

Sports centre management system written in Python 3 with Flask and `sqllite` as the web server/database backend.

## Installation

To install the app and its dependencies, do
```shell
$ git clone git@gitlab.com:jakeboughey/21.git comp2913
$ cd comp2913
$ virtualenv venv && source venv/bin/activate
$ pip install -r requirements.txt
```

## Getting started

If running the app for the first time, you first need to set up the database:
```shell
$ export FLASK_APP=flasky.py
$ flask db upgrade
```

Add the role IDs to the database:
```shell
$ flask shell
Python 3.7.5
...
>>> models.Role.insert_roles()
```

Choose an admin email:
```shell
$ export FLASKY_ADMIN=<some email address>
```

Then finally run the app:
```shell
$ flask run
```

Finally, navigate to <http://127.0.0.1:5000/register> and create an account with the admin email address, then log in.

## Contributing

This repository uses feature branches. When implementing a new item from the backlog please create a new branch (`git checkout -b <branch-name>`). Branches will be merged into `master` once features are complete.

## Further info

Please see the project wiki for meeting summaries, design documents etc.
