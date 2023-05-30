# Multipass Environment Setup

## Install Multipass

Visit the [Multipass installation](https://multipass.run/install) page and install it.

## Create Ubuntu Virtual Machine

Navigate to the project's top-level directory. Run the following command to create an Ubuntu 22.04 virtual machine.

```sh
# On Mac, you may have to `multipass set local.driver=qemu` for this to work
multipass launch jammy -m 2G -d 3500M -c 2 -n learnops --mount $(pwd):/mnt/learnops
```

## Configure Ubuntu Virtual Machine

Run the following script to install all software, create the database, get the code, install dependencies, seed the database, and configure nginx. When the script is done,

```sh
multipass exec learnops -- /bin/bash -c "/mnt/learnops/config/setup_ubuntu_local.sh --client="$LEARN_OPS_CLIENT_ID" --secret="$LEARN_OPS_SECRET_KEY" --password="$LEARN_OPS_PASSWORD" --django="$LEARN_OPS_DJANGO_SECRET_KEY" --hosts="$LEARN_OPS_ALLOWED_HOSTS" --suser="$LEARN_OPS_SUPERUSER_NAME" --supass="$LEARN_OPS_SUPERUSER_PASSWORD" --slack="$SLACK_TOKEN
```

## Give Your Virtual Machine a Domain Name

Run the following command to find the IPv4 address of your instance.

```sh
multipass info learnops
```

Copy the IPv4 address and then edit your `/etc/hosts` file and add the following line to it.

```sh
the.ip4.address.copied      api.learning.local
```

## Verify Local Domain

Run the following command to verify that the virtual machine is configured correctly and you get data back.

```sh
curl -H "Authorization: Token 86aa7dee6e554818fe9a3cf8a2c67f57bc4991eb" http://api.learning.local/cohorts/1
```

## Testing Superuser Credentials

1. Visit http://api.learning.local/admin
1. Authenticate with the superuser credentials you specified in your environment variables and ensure that you gain access to the admin interface.


## Make Yourself an Instructor

1. Start the React client application.
1. Authorize the client with Github.
2. Visit http:///api.learning.local/admin and authenticate with your superuser credentials.
3. Click on **Users** in the left navigation.
4. Find the account that was just created for your Github authorization by searching for your Github username.
5. Click on your user account.
6. Toggle **Staff status** to be on.
7. In the **Group** sections, double click **Instructor** so that it moves to the _Chosen groups_ list.
8. Close the browser tab that is running the Learning Platform.
9. Open a new tab and visit http://localhost:3000 again and authenticate.
10. You should now see the instructor interface.
