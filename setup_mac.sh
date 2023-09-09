#!/bin/bash

source ./setup_mac_python.sh
source ./setup_mac_data.sh

code --install-extension ms-python.python --force
code --install-extension ms-python.vscode-pylance --force
code --install-extension njpwerner.autodocstring --force
code --install-extension alexcvzz.vscode-sqlite --force
code --install-extension streetsidesoftware.code-spell-checker --force
code --install-extension irongeek.vscode-env --force