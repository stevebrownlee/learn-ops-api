# Mac Development Environment Setup

## Step 1: Prerequisite Installations

### Homebrew

If you don't have Homebrew installed, [visit the Homebrew site](https://brew.sh/) and follow the simple instructions.

### Bash Update

It is highly recommended that you install an updated version of `bash` as the default version on a Mac is notoriously outdated.

```sh
brew install bash
```

Once complete, log out and back into your Mac.

## Step 2: Github OAuth App

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


## Step 3: Environment Variables

Several environment variables need to be set up by you to make the setup process faster and more secure. Set up the following environment variables anywhere in your shell initialization file _(i.e. `.bashrc` or `.zshrc`)_.

### Postgres

These variables define the name of the database, the Postgres user _(with accompanying password)_, the host, and the port. It is recommended that you keep all default values except for the value of **LEARN_OPS_PASSWORD**.

```sh
export LEARN_OPS_DB=learnopsdev
export LEARN_OPS_USER=learnopsdev
export LEARN_OPS_PASSWORD=DatabasePasswordOfYourChoice
export LEARN_OPS_HOST=127.0.0.1
export LEARN_OPS_PORT=5432
```

### Github OAuth

These two variables are the client ID and secret key for the Github OAuth application you created.

```sh
export LEARN_OPS_CLIENT_ID=GithubOAuthAppClientId
export LEARN_OPS_SECRET_KEY=GithubOAuthAppSecret
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
export LEARN_OPS_ALLOWED_HOSTS="127.0.0.1,localhost"
export LEARN_OPS_SUPERUSER_NAME=AdminUsernameOfYourChoice
export LEARN_OPS_SUPERUSER_PASSWORD=AdminPasswordOfYourChoice
```

### Activate Environment Variables

Then reload your bash session with `source ~/.zshrc` if you are using zshell or `source ~/.bashrc` if you have the default bash environment.

## Step 4: Install Python

Run the following scripts to ensure the you have `pyenv` installed, which will, in turn, install the correct version of `python` for this project. It will also install `pipenv` which is used to manage the virutal environment for this project.

```sh
./setup_mac_python.sh
```

## Step 5: Activate Virtual Environment

Run the following command from the project's top-level directory to activate the environment.

```sh
pipenv shell
```

## Step 6: Install Database and Initialize App

If the virtual environment initialized properly, run the following command from the project's top-level directory to install the database, run migrations, seed it with data, and install all project dependencies.

```sh
./setup_mac.sh
```

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
