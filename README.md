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

