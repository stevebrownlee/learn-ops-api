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

## Setup

### Getting Started

1. Fork this repo to your own Github account, and then clone it.
1. Install dependencies
   ```sh
   cd learn-ops-api
   pipenv shell
   pipenv install
   ```


### Social Account Fixture

In the `fixtures` directory of the API app, create a file named **socialaccount.json** and paste in the follow data.

 ```json
[
   {
      "model": "sites.site",
      "pk": 1,
      "fields": {
         "domain": "learningplatform.com",
         "name": "Learning Platform"
      }
   },
   {
      "model": "socialaccount.socialapp",
      "pk": 1,
      "fields": {
         "provider": "github",
         "name": "Github",
         "client_id": "",
         "secret": "",
         "key": "",
         "sites": [
            1
         ]
      }
   }
]
 ```

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
14. Copy the secret key that is generated into the `secret` field into the JSON file.

### Environment Variables

Set up the following environment variables initialization file _(i.e. `.bashrc` or `.zshrc`)_. You get to pick any username and password you want. The location in the file is irrelevent.

Just don't use spaces in the username or password.

```sh
export LEARN_OPS_DB=learnops
export LEARN_OPS_USER={Postgres username}
export LEARN_OPS_PASSWORD={Postgres user password}
export LEARN_OPS_HOST=localhost
export LEARN_OPS_PORT=5432
```

Then reload your bash session with `source zsh` if you are using zshell or `source bash` if you have the default bash environment.


### Create the Database

In the main directory there is a bash script that you can run to create the database and database user needed for the project. You can run the script with the command below.

It will prompt you for your password.

```sh
./createdb.sh
```

### Seed the Database

In the main directory there is a bash script that you can run to create the tables and seed some data. You can run it with the command below.

```sh
./seed.sh
```

> For Mac, if you get feedback that `psql command not found`, add the following to your PATH in your shell initialization file _(.bashrc or .zshrc)_. Make sure the version is correct. You may not have version 10 of Postgres.
>
>    ```
>    /Applications/Postgres.app/Contents/Versions/10/bin
>    ```

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
