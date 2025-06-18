#!/bin/bash

PYTHON_VERSION=3.11.11

function installPyenv() {
    # If changes need to be made to user's config file, detect the correct one
    [[ "$SHELL" == *"bash"* ]] && config_file=".bashrc" || config_file=".zshrc"

    if [ $(brew list | grep -c pyenv) != 1 ]; then
        echo "Installing Pyenv"
        brew install pyenv
    else
        echo "Skipping Pyenv install. Ensuring latest version of pip."
        python3 -m pip install --upgrade pip
    fi

    if [[ PYENV_ROOT ]]; then
        echo "Skipping Pyenv Configuration"
    else
        echo "
# Configure pyenv
export PYENV_ROOT=\"$HOME/.pyenv\"
export PIPENV_DIR=\"$HOME/.local\"
export PATH=$HOME/.local/bin:$HOME/.pyenv/bin:$PATH

if command -v pyenv 1>/dev/null 2>&1; then
    export PATH=$(pyenv root)/shims:$PATH
    eval "$(pyenv init -)"\n
fi" >>$HOME/$config_file
        source $HOME/$config_file
    fi
}

function installPython() {
    installPyenv

    versionInstalled=$(pyenv versions | grep -c "$PYTHON_VERSION")
    if [ $versionInstalled != 1 ]; then
        echo "Installing Python version $PYTHON_VERSION"
        pyenv install ${PYTHON_VERSION}:latest
    else
        echo "Skipping $PYTHON_VERSION install"
    fi

    INSTALLED_PYTHON_VERSION=$(pyenv versions | grep -o ${PYTHON_VERSION}'.*[0-9]' | tail -1)
    pyenv global $INSTALLED_PYTHON_VERSION

    if [ $(python3 -m pip list | grep -c pipenv) != 1 ]; then
        echo "Install pipenv and autopep8"
        python3 -m pip install pipenv autopep8
    else
        echo "Skipping pipenv and autopep8 install"
    fi

    if [[ $(which pipenv) == "pipenv not found" ]]; then
        echo "Could not find pipenv. Exiting installation process..."
        return 0
    fi
}

function installBrew() {
    if ! type brew &>/dev/null; then
        echo -e "\n\n\n\nInstalling Homebrew..."

        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        echo 'eval $(/opt/homebrew/bin/brew shellenv)' >>$HOME/.zprofile
        eval $(/opt/homebrew/bin/brew shellenv)
    fi
}

installBrew
installPython
