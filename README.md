# NSS Instructor Applications Project

## Assets

### ERD

[dbdiagram.io ERD](https://dbdiagram.io/d/6005cc1080d742080a36d6d8)


### Postman testing requests

1. Open Postman
1. Click Import from the navbar
1. Choose the Link option
1. Paste in this URL: https://www.getpostman.com/collections/46729eac036157ae9e1e
1. You should be prompted to import LearnOps Collection.
1. Click the Import button to complete the process.

## Setup

### Database

1. Go to [Postgresapp](https://postgresapp.com/) to download and run the Postgres app for your platform.
1. Once installed, open pgAdmin and create a new database named `learnops` on the server that was automatically created during installation.

### Getting the Code

1. Fork the learn-ops-api repo to your own account.
1. Clone repository to your machine

### Set Up Environment

```sh
cd learn-ops-api
pipenv shell
pipenv install
```

## Seed the Database

1. Request the secret key from your administrator.

1. Add the secret key to the `./LearningAPI/fixtures/socialaccount.json` file in the `"secret"` key for the `"socialaccount.socialapp"` object.

1. In the main directory there is a bash script that you can run to create the tables and seed some data. You can run it with the command below.

    ```sh
    ./seed.sh
    ```

1. Create a Django superuser account with `python manage.py createsuperuser`. This will give you an account with which you can get into the admin site.

## Testing the Installation

1. Start the API in debug mode in Visual Studio Code.
1. Open the client application.
1. Authorize the client with Github.
1. Visit http://localhost:8000/admin
1. Authenticate with the superuser credentials you created previously.
1. Verify that the following tables have data in them:
    1. Tokens
    1. Users
    1. Nss users
    1. Social accounts
    1. Social application tokens
    1. Learning records
    1. Learning record weights
1. If all the data is there, open Postman.
1. Look in the Tokens data and find a token for a student.
1. Open the "Get Single Student" request in Postman.
1. Copy pasta the student token

## Github Auth URL

> The folowing content is just to document the process of Github authentication. It isn't step to follow, but it is good to understand the flow of tokens and redirections.

1. Put a button in the client to send the user to the following URL to login with Github. This is a URL mapping on the API _(look in urls.py)_.

    http://localhost:8000/auth/github/url

1. The API code redirects the user to the following URL.

    https://github.com/login/oauth/authorize?client_id=9494949494949494&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fgithub%2Fcallback&scope=&response_type=code&state=1010101010

1. The student is presented with the interface to authorize the application with their Github credentials. Once the student authorizes, Github redirects to the following URL _(this is an API URL, not the client)_.

    http://localhost:8000/auth/github/callback

1. The API immediately redirects the user to the client callback URL with some query parameters.

    http://localhost:3000/auth/github?code=8ad10df9d7c89dd28c89&state=tBozt4gdvy7a

1. The client then uses the `code` query param to ping the API.

    http://localhost:8000/auth/github?code=8ad10df9d7c89dd28c89

1. The API will then respond with an authorization key.

    ```json
    {
        "key": "seriesofrandomnumbersandletters"
    }
    ```

1. Finally, the client can use authorization key to get the user information. All requests during the user's session must include the authorizaation token.

    ```js
    fetch("http://localhost:8000/profile", {
        method: "GET",
        headers: {
            "Authorization": "Token seriesofrandomnumbersandletters",
            "Accepts": "application/json"
        }
    }
    ```

1. That request responds with an object containing the student's profile information.

    ```json
    {
        "pk":82,
        "username":"colonelmustard",
        "email":"killer@boddymansion.com",
        "first_name":"Colonel",
        "last_name":"Mustard"
    }
    ```
