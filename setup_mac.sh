#!/bin/bash

source ./setup_mac_python.sh
source ./setup_mac_data.sh

code --install-extension irongeek.vscode-env --force
code --install-extension ms-python.python --force
code --install-extension ms-python.vscode-pylance --force
code --install-extension njpwerner.autodocstring --force
code --install-extension streetsidesoftware.code-spell-checker --force
code --install-extension ms-vscode-remote.remote-wsl --force
code --install-extension ms-python.pylint --force
code --install-extension ms-python.black-formatter --force