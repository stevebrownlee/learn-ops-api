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

## Install Python

Run the following scripts to ensure the you have `pyenv` installed, which will, in turn, install the correct version of `python` for this project. It will also install `pipenv` which is used to manage the virutal environment for this project.

```sh
./setup_mac_python.sh
```

## Activate Virtual Environment

Run the following command from the project's top-level directory to activate the environment.

```sh
pipenv shell
```

## Install Database and Initialize App

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
