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

### Clone repository

```sh
git clone git@github.com:nashville-software-school/LearningPlatform.git
cd LearningPlatform
```

### Set Up Environment

```sh
pipenv shell
pipenv install
```

## Create and Seed the Database

1. Go to [Postgresapp](https://postgresapp.com/) to download and run the Postgres app for your platform.
1. Once installed, open pgAdmin and create a new database named `learnops` on the server that was automatically created during installation.
1. In the `LearningPlatform` directory there is a bash script that you can run to create the tables and seed some data. You can run it with the command below.

```sh
./seed.sh
```

## Testing the Installation

```sh
python manage.py runserver
```

## Github Auth URL

Put a button in the client to send the user to the following URL to login with Github.

http://localhost:8000/auth/github/url

That will redirect the user to the following URL

https://github.com/login/oauth/authorize?client_id=9494949494949494&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fgithub%2Fcallback&scope=&response_type=code&state=1010101010

Once the user authorizes, Github redirects to the following URL.

http://localhost:8000/auth/github/callback

Which in turn redirects the user to the client callback URL with some query parameters

http://localhost:3000/auth/github?code=8ad10df9d7c89dd28c89&state=tBozt4gdvy7a

The client then uses the `code` query param to ping the API

http://localhost:8000/auth/github?code=8ad10df9d7c89dd28c89

The API will then respond with an authorization key.

```json
{
    "key": "627d52a940b6c6dfd3214ecff442deeadb024547"
}
```

Finally, the client can use that key to get the user information. All requests during the user's session must include the auth token.

```js
fetch("http://localhost:8000/auth/user/", {
    method: "GET",
    headers: {
        "Authorization": "Token 627d52a940b6c6dfd3214ecff442deeadb024547",
        "Accept": "application/json"
    }
}
```

Which will respond with an object.

```json
{
    "pk":82,
    "username":"colonelmustard",
    "email":"killer@boddymansion.com",
    "first_name":"Colonel",
    "last_name":"Mustard"
}
```
