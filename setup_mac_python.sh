#!/bin/bash

function installPyenv() {
    if [ $(brew list | grep -c pyenv) != 1 ]; then
        echo "Installing Pyenv"
        brew install pyenv
    else
        echo "Skipping Pyenv install"
    fi

    if [ -v "$PYENV_ROOT" ]; then
        echo "Skipping Pyenv Configuration"
    else
        echo -e '\n\n# Configure pyenv\n
export PYENV_ROOT="$HOME/.pyenv"\n
export PIPENV_DIR="$HOME/.local"\n
export PATH="$PIPENV_DIR/bin:$PYENV_ROOT/bin:$PATH"\n

if command -v pyenv 1>/dev/null 2>&1; then\n
\texport PATH=$(pyenv root)/shims:$PATH\n
\teval "$(pyenv init -)"\n
fi\n' >>~/.zshrc
        source ~/.zshrc
    fi
}

function installPython() {
    installPyenv

    if [ $(pyenv versions | grep -c $PYTHON_VERSION) != 1 ]; then
        echo "Installing Python version $PYTHON_VERSION"
        pyenv install ${PYTHON_VERSION}:latest
    else
        echo "Skipping $PYTHON_VERSION install"
    fi
}

