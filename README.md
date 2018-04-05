# NSS Instructor Applications Project

## Setup

### Clone repository

```sh
git clone git@github.com:nashville-software-school/LearningPlatform.git
cd LearningPlatform
```

### Enable virtual environment

```sh
# OSX/Linux
mkdir learngingenv
cd learningenv
python3.6 -m venv .

## Windows
python -m venv .
```

### Activate virtual environment

```sh
## Mac
source learningenv/bin/activate

## Windows
/Scripts/activate.bat
```

### Install required packages

```sh
pip install -r requirements.txt
```

## Initializing Database

In the `LearningPlatform` directory, run the following command to apply the initial migration.

```sh
python manage.py migrate
```

## Testing the Installation

```sh
python manage.py runserver
```

