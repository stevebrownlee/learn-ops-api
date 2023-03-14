# NSS Instructor Applications Project

## Installs Needed

### Postgres

Go to [Postgresapp](https://postgresapp.com/) to download and run the Postgres app for your platform.

### Learning Platform Request Collection

1. Install [Postman](https://www.postman.com/downloads/)
1. Open Postman app
1. Click Import from the navbar
1. Choose the Link option
1. Paste in this URL: https://www.getpostman.com/collections/46729eac036157ae9e1e
1. You should be prompted to import LearnOps Collection.
1. Click the Import button to complete the process.

### pgAdmin (Optional)

pgAdmin is not a required install, but if you ever have the desire to have a browser-based interface for working directly with the database, go to [pgAdmin](https://www.pgadmin.org/download/) to download the administration tool for Postgres.

### Multipass (optional)

If you want to run the Learning Platform in an Ubuntu instance instead of installting everything on your machine, you can install Multipass.

Visit the [Multipass installation](https://multipass.run/install) page and install it.

## Setup

### Getting Started

Fork this repo to your own Github account, and then clone it. Then `cd` into the project directory.

#### Mac OS

You can move on to the next step.

#### Multipass

If you are using Multipass, run the following command. Run `pwd` to get your current directory to use in the command.

```sh
multipass launch -m 1G -d 2G -n learnops --mount /absolute/path/to/learn-ops-api:/mnt/learnops
multipass shell learnops
```

You should now be logged into your Ubuntu image.


### Github OAuth App

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
11. Open the `fixtures/socialaccount.json` file
12. Go to Github and copy the **Client ID** and paste it into the `client_id` key in the JSON file.
13. Go to Github and click the **Generate a new client secret** button
14. **DO NOT CLOSE THIS TAB OR NAVIGATE AWAY**

### Environment Variables

Several environment variables need to be set up by you to make the setup process faster and more secure. Set up the following environment variables anywhere in your shell initialization file _(i.e. `.bashrc` or `.zshrc`)_.

#### OAuth

Copy the client ID and secret key that was generated in the previous step as the value of the corresponding variables.

```sh
export LEARN_OPS_CLIENT_ID={Github app client ID}
export LEARN_OPS_SECRET_KEY={Github app secret}
```

#### Database

> **Tip:** You get to pick any Postgres password you want, but don't use spaces in it.

```sh
export LEARN_OPS_DB=learnops
export LEARN_OPS_USER=learnops
export LEARN_OPS_PASSWORD={Postgres user password}
export LEARN_OPS_HOST=localhost
export LEARN_OPS_PORT=5432
```

#### Django Secret Key

To generate a Django secret key, run the following command in your terminal.

```sh
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then add a new variable to your init file.

```sh
export LEARN_OPS_DJANGO_SECRET_KEY={insert generated key}
```

#### Django Allowed Hosts

Add the following environment variable to your init file. If you are running the API in a container using a tool like Multipass or Docker, you must add the IP address of the container to this comma-separated list.

```sh
export LEARN_OPS_ALLOWED_HOSTS="learning.nss.team,learningapi.nss.team,127.0.0.1,localhost"
```

### Activate Environment Variables

Then reload your bash session with `source zsh` if you are using zshell or `source bash` if you have the default bash environment.

### Project Installs and Config

If you are running on a Mac, run the following commands

```sh
pipenv shell
pipenv install
```



### Create the Database

In the main directory there is a bash script that you can run to create the database and database user needed for the project. You can run the script with the command below.

It will prompt you for your password.

```sh
./createdb.sh
```

> For Mac, if you get feedback that `psql command not found`, add the following to your PATH in your shell initialization file _(.bashrc or .zshrc)_. Make sure the version is correct. You may not have version 10 of Postgres. If you don't, determine your version and replace the 10.
>
>    ```
>    /Applications/Postgres.app/Contents/Versions/10/bin
>    ```


### Seed the Database

In the main directory there is a bash script that you can run to create the tables and seed some data. You can run it with the command below.

```sh
./seed.sh
```


### Create a Superuser

Create a Django superuser account with `python manage.py createsuperuser`. This will give you an account with which you can get into the admin site.

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
