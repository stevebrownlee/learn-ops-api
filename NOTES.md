# Github Auth URL

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
