# Learning Platform - Multipass Edition

## Getting Started

### Install Multipass

Visit the [Multipass installation](https://multipass.run/install) page and install it.

### Generate Django Secret Key

Run the following command in your terminal to generate a randomized secret key for Django. Save the generated key for use later.

```sh
python3 -c 'import secrets; print(secrets.token_hex(30))'
```

## Github OAuth App

The Learning Platform uses Github for authorization, so you need to set up an OAuth app in Github for the app to work.

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
14. **DO NOT CLOSE THIS TAB OR NAVIGATE AWAY**

## Starting Ubuntu Virtual Machine

Clone your repository and navigate to the project directory that is created. Run the following commands to start and enter the virtual machine.

```sh
multipass launch lts -m 2G -d 4G -n learnops --mount $(pwd):/mnt/learnops
multipass shell learnops
```

Once logged into Ubuntu navigate to the mounted directory.

```sh
cd /mnt/learnops
```

## Configure

### Virtual Machine IP Address

Run `multipass list` to get the IP address of your Ubuntu VM.

### Installs and Configuration for Ubuntu

Run the following bash script, making sure you replace the dummy values for the actual values that you've generated previously. Ask a teammate for the Slack Token.

You might want to copy pasta the command below into VS Code and modify it before running it in the terminal.

```sh
./setup_ubuntu.sh \
    -c=InsertOAuthClientIDHere \
    -s=InsertOAuthSecretHere \
    -p=PasswordOfYourChoice \
    -d='DjangoSecretKeyHere' \
    -h="127.0.0.1,localhost,IP.Address.Of.VM" \
    -k=AskTeamForTheSlackToken \
    -u=$USER
```

Once the process is complete, run the following command to enable all of the environment variables.

```sh
source ~/.bashrc
```

### Create a Superuser

Create a Django superuser account with `python3 manage.py createsuperuser`. This will give you an account with which you can get into the admin site.

## Testing the Installation

1. In the Ubuntu VM, start the API with `python3 manage.py runserver 0.0.0.0:8000`.
1. In Chrome, visit http://vm.ip.address:8000/admin
1. Authenticate with the superuser credentials you created previously and then you can view all kinds of data that is in your database.

## Make Yourself an Instructor

1. Start the React client application.
1. Authorize the client with Github.
1. Visit http://vm.ip.address:8000/admin and authenticate with your superuser credentials.
2. Click on **Users** in the left navigation.
3. Find the account that was just created for your Github authorization by searching for your Github username.
4. Click on your user account.
5. Toggle **Staff status** to be on.
6. In the **Group** sections, double click **Instructor** so that it moves to the _Chosen groups_ list.
7. Close the browser tab that is running the Learning Platform.
8. Open a new tab and visit http://localhost:3000 again and authenticate.
9. You should now see the instructor interface.
