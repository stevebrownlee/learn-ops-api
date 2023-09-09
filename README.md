# Learning Platform Project

## About

This project is the API for the Learning Platform. It is a Django project using the Django REST Framework application. It integrates with the Github OAuth platform to create accounts and perform authorization for the companion [Learning Platform React client](https://github.com/stevebrownlee/learn-ops-client).

## Prerequisites for Windows Users

If you are a Windows user, you will need to install WSL and Ubuntu.

Do only steps 1-4 of these instructions if you have never installed WSL before.

Do not do step 5... only steps 1-4.

[Ubuntu on WSL install instructions](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support#1-overview)

Once you are done, you will be working in an Ubuntu terminal during all setup and developing on the API.

## Project Setup

1. Fork this repo to your own Github account.
2. Clone it.
3. `cd` into the project directory.

### Github OAuth App

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

## Installations

Once your environment variables are established, you will run a bash script to install all the software needed for the API to run, create the database tables needed, and seed the database with some data.

### Mac Users

In your terminal, be in the project directory, and run the following command.

```sh
./setup_mac.sh
```

### Windows Users

In your Ubuntu terminal, be in the project directory, and run the following command.

```sh
./setup_ubuntu_local.sh
```

## API Account Setup

Go back to VSCode and start a Django debugger _(recommend [creating a launcher profile](https://code.visualstudio.com/docs/python/tutorial-django#_create-a-debugger-launch-profile) for yourself)_. If the setup was successful, you will see the following output in the VSCode integrated terminal.

```sh
Performing system checks...

System check identified no issues (0 silenced).
September 09, 2023 - 19:46:38
Django version 4.2.2, using settings 'LearningPlatform.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Testing Superuser Credentials

1. Visit [http://localhost:8000/admin](http://localhost:8000/admin)
1. Authenticate with the superuser credentials you specified in your environment variables and ensure that you gain access to the admin interface.

### Make Yourself an Instructor

If you successfully authenticated, follow these steps to access the instructor interface of the Learning Platform. You must have already cloned and set up the client application before you perform these steps.

1. Start the React client application.
1. Authorize the client with Github.
2. Visit the [admin interface](http://localhost:8000/admin) and authenticate with your superuser credentials.
3. Click on **Users** in the left navigation.
4. Find the account that was just created for your Github authorization by searching for your Github username.
5. Click on your user account.
6. Toggle **Staff status** to be on.
7. In the **Group** sections, double click **Instructor** so that it moves to the _Chosen groups_ list.
8. Close the browser tab that is running the Learning Platform.
9. Open a new tab and visit http://localhost:3000 again and authenticate.
10. You should now see the instructor interface.


## ERD

[dbdiagram.io ERD](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)
