========
myDebate
========

The myDebate Django project requires the following Python packages:

 - Django 1.1.1
 - django-profiles
 - django-haystack
 - whoosh

These are listed in requirements.txt file, which is used later on.

=== Virtualenv ===

It is recommeneded that you use virtualenv to get a working environment for the project,
as it makes installing the required packages *much* easier. Virtualenvwrapper is a collection
of scripts that makes using virtualenv simpler.

Virtualenv can be installed with the following command on ubuntu:

    sudo apt-get install python-virtualenv

Virtualenv wrapper, however, is not distributed as a .deb, so you need to use easy_install:

    sudo easy_install virtualenvwrapper

If easy_install is not installed, you need the python-setuptools package.

To create the virtual environment with virtualenvwrapper, use the following command:

    mkvirtualenv --no-site-packages mydebate

This will then place you in "working" mode, whereby you will have {{{(mydebate)}}} before your command prompt.

=== Installing Dependencies ===

The {{{requirements.txt}}} file contains all the requirements for myDebate. To install these dependencies, use the following command from within the `democonf' folder (the project was renamed half way through)

    pip -E $VIRTUAL_ENV install -r requirements.txt

Note that if you don't have pip, you can use easy_install instead, but you will have to install each required dependency (and it's exact version) manually.

=== Setting up the Database ===

Before you start the server, you will need to sync the database. Before you do this, however, you will need to copy the template local settings file into your project:

    cp local_settings.py.tmpl local_settings.py

The template local settings file states that an SQLite database should be used, called `dev.db'. This is usually fine, so you probably shouldn't need to edit the file at all.

Then, run the syncdb command:

    python manage.py syncdb

=== Starting the Server ===

Now you should be ready to go ahead and start the development server:

    python manage.py runserver

The server can be accessed by pointing your browser at http://localhost:8000.
