# Learning Platform Project

## About

This project is the API for the Learning Platform. It is a Django project using the Django REST Framework application. It integrates with the Github OAuth platform to create accounts and perform authorization for the companion [Learning Platform React client](https://github.com/stevebrownlee/learn-ops-client).

The Learning Platform allows instructors to track student progress, through books and projects, create new courses _(a collection of books and projects)_, keep notes about students, transfer students between cohorts, build student teams for group projects, create Github repositories for group projects, create Slack channels for student teams, and use Valkey to communicate with the [Monarch](https://github.com/stevebrownlee/service-monarch) service to migrate issue tickets to Github repositories for group projects.

## Tech Stack

* Django
* Django REST Framework
* django-cors-headers
* dj-rest-auth
* django-allauth
* valkey

## Github OAuth App

This application uses Github for authorization instead of user accounts in Django. You will need to set up your own OAuth application for use during local development.

1. Go to your Github account settings
2. Open **Developer Settings**
3. Open **OAuth Apps**
4. Click **Register New Application** button
5. Application name should be **Learning Platform**
6. Homepage URL should be `http://localhost:3000`
7. Enter a description if you like
8. Authorization callback should be `http://localhost:8000/auth/github/callback`
9. Leave **Enable Device Flow** unchecked
10. Click the **Register Application** button
11. Click the **Generate a new client secret** button
12. **DO NOT CLOSE TAB. CLIENT AND SECRET NEEDED BELOW.**


## Getting Started

1. Fork this repo to your own Github account. Set your fork as remote origin. Set this repository as remote upstream.
2. Clone your fork to your directory of choice.
3. `cd` into the project directory that gets created.

### Environment Variables

Several environment variables need to be set up by you to make the setup process faster and more secure.

1. Open the project directory in your code editor.
2. Make a copy of the `.env.template` file in the project directory and name it `.env`.
3. Replace all "replace_me" values in the file and be sure to read the notes below.

#### Environment Variables Notes

* The `LEARN_OPS_CLIENT_ID` and `LEARN_OPS_SECRET_KEY` values will be listed in the open tab you created previously for the Github OAuth app.
* For the Django secret key, a quick way to get a good secret key is to visit [Djecrety](https://djecrety.ir/).
* The superuser variables will be your credentials for logging into the Django admin panel where you can view and update data in a web interface.
* The `LEARN_OPS_PASSWORD` variable is the password for a database user that will be created your local database. Make it something simple.

### Installations

Once your environment variables are established, you will run a bash script to install all the software needed for the API to run, create the database tables needed, and seed the database with some data.

In your terminal, be in the project directory, and run the following command.

```sh
./setup.sh
```

Once this script is complete, you will have the Postgres database, and some starter data seeded in it.


## Start Virtual Environment

The setup script installs Python 3.11.11, so your last step is to start the virtual environment for the project with the correct version.

```sh
pipenv --python 3.11.11 shell
```

## Using the API

Go back to VSCode and start a Django debugger _(recommend [creating a launcher profile](https://code.visualstudio.com/docs/python/tutorial-django#_create-a-debugger-launch-profile) for yourself)_. If the setup was successful, you will see the following output in the VSCode integrated terminal.

```sh
Performing system checks...

System check identified no issues (0 silenced).
September 09, 2023 - 19:46:38
Django version 4.2.2, using settings 'LearningPlatform.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## ERD

[dbdiagram.io ERD](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)
