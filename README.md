# Learning Platform Project

## About

This project is the API for the Learning Platform. It is a Django project using the Django REST Framework application. It integrates with the Github OAuth platform to create accounts and perform authorization for the companion [Learning Platform React client](https://github.com/stevebrownlee/learn-ops-client).

## Github OAuth App

This application uses Github for authorization instead of user accounts in Django. You will need to set up your own OAuth application for use during local development.

1. Go to your Github account settings
2. Open **Developer Settings**
3. Open **OAuth Apps**
4. Click **New OAuth App** button
5. Application name should be **Learning Platform**
6. Homepage URL should be `http://localhost:3000`
7. Enter a description if you like
8. Authorization callback should be `http://localhost:8000/auth/github/callback`
9. Leave **Enable Device Flow** unchecked
10. Create the app and **do not close** the screen that appears
11. Go to Github and click the **Generate a new client secret** button
12. **DO NOT CLOSE TAB. CLIENT AND SECRET NEEDED BELOW.**

## Environment Variables

Several environment variables need to be set up by you to make the setup process faster and more secure. Set up the following environment variables anywhere in your shell initialization file _(i.e. `.bashrc` or `.zshrc`)_.

### Github OAuth

These two variables are the client ID and secret key for the Github OAuth application you created.

```sh
export LEARN_OPS_CLIENT_ID=GithubOAuthAppClientId
export LEARN_OPS_SECRET_KEY=GithubOAuthAppSecret
```

### Postgres

These variables define the name of the database, the Postgres user _(with accompanying password)_, the host, and the port. It is recommended that you keep all default values except for the value of **LEARN_OPS_PASSWORD**.

```sh
export LEARN_OPS_DB=learnopsdev
export LEARN_OPS_USER=learnopsdev
export LEARN_OPS_PASSWORD=DatabasePasswordOfYourChoice
export LEARN_OPS_HOST=127.0.0.1
export LEARN_OPS_PORT=5432
```

### Django Secret Key

You will need a Django secret key environment variable. A quick way to get a good secret key is to visit [Djecrety](https://djecrety.ir/). Then paste what it generates as the value of your environment variable. Make sure that the double quotes wrap your secret key.

```sh
export LEARN_OPS_DJANGO_SECRET_KEY="GeneratedDjangoSecretKey"
```

### Django Settings

A super user account will be automatically created for you that will allow you to log into the admin console. Specify what you want your username and password to be with these variables.

You can leave the allowed hosts value to what it already is for local development.

```sh
export LEARN_OPS_ALLOWED_HOSTS="api.learning.local,127.0.0.1,localhost"
export LEARN_OPS_SUPERUSER_NAME=AdminUsernameOfYourChoice
export LEARN_OPS_SUPERUSER_PASSWORD=AdminPasswordOfYourChoice
```

### Activate Environment Variables

Then reload your bash session with `source ~/.zshrc` if you are using zshell or `source ~/.bashrc` if you have the default bash environment.

## Project Setup

1. Fork this repo to your own Github account.
2. Clone it.
3. `cd` into the project directory.


The recommended way to set up your local development environment is using Multipass. This will create a virtual machine that you can stop and start any time you want when you want to work on the Learning Platform.

Follow the instructions in the [Multipass Environment Setup](./MULTIPASS.md)

> If you don't want to rely on a separate virtual machine for a development environment, and just use your Mac system as the environment, you can follow the instruction in the [Mac Development Environment Setup](./MAC_SETUP.md)


## ERD

[dbdiagram.io ERD](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)
