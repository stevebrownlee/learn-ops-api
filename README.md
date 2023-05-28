# Learning Platform Project

## Prerequisites

### Github OAuth App

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


## Getting Started

1. Fork this repo to your own Github account.
2. Clone it.
3. `cd` into the project directory.
4. Click on the appropriate link below to follow the installations for your dev environment

* [Mac environment installations](./MAC_SETUP.md)
* [Linux environment installations](./LINUX_SETUP.md)

## Environment Variables

Several environment variables need to be set up by you to make the setup process faster and more secure. Set up the following environment variables anywhere in your shell initialization file _(i.e. `.bashrc` or `.zshrc`)_.
### Postgres Config

These variables define the name of the database, the Postgres user _(with accompanying password)_, the host, and the port.

```sh
export LEARN_OPS_DB=learnopsdev
export LEARN_OPS_USER=learnopsdev
export LEARN_OPS_PASSWORD=DatabasePasswordOfYourChoice
export LEARN_OPS_HOST=127.0.0.1
export LEARN_OPS_PORT=5432
```

### Github OAuth Config

These two variables are the client ID and secret key for the Github OAuth application you created.

```sh
export LEARN_OPS_CLIENT_ID=GithubOAuthAppClientId
export LEARN_OPS_SECRET_KEY=GithubOAuthAppSecret
```

### Django Secret Key Config

You will need a Django secret key environment variable. Run the following command in your terminal to generate one. Make sure your virtual environment is activated before you run it.

```sh
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then take the output and set it as the value of this environment variable.

```sh
export LEARN_OPS_DJANGO_SECRET_KEY="GeneratedDjangoSecretKey"
```

### Django Settings Config

A super user account will be automatically created for you that will allow you to log into the admin console. Specify what you want your username and password to be with these variables.

You can leave the allowed hosts value to what it already is for local development.

```sh
export LEARN_OPS_ALLOWED_HOSTS="127.0.0.1,localhost"
export LEARN_OPS_SUPERUSER_NAME=AdminUsernameOfYourChoice
export LEARN_OPS_SUPERUSER_PASSWORD=AdminPasswordOfYourChoice
```

### Activate Environment Variables

Then reload your bash session with `source ~/.zshrc` if you are using zshell or `source ~/.bashrc` if you have the default bash environment.

## Testing the Installation

1. Start the API in debug mode in Visual Studio Code.
1. Visit http://localhost:8000/admin
1. Authenticate with the superuser credentials you created previously and then you can view all kinds of data that is in your database.

## Make Yourself an Instructor

1. Start the React client application.
1. Authorize the client with Github.
1. Visit http://localhost:8000/admin and authenticate with your superuser credentials.
2. Click on **Users** in the left navigation.
3. Find the account that was just created for your Github authorization by searching for your Github username.
4. Click on your user account.
5. Toggle **Staff status** to be on.
6. In the **Group** sections, double click **Instructor** so that it moves to the _Chosen groups_ list.
7. Close the browser tab that is running the Learning Platform.
8. Open a new tab and visit http://localhost:3000 again and authenticate.
9. You should now see the instructor interface.



## Assets

### ERD

[dbdiagram.io ERD](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)
