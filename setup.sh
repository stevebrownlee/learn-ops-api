#!/bin/bash

# Detect the operating system
os_name="$(uname -s)"

# Define the paths to the OS-specific scripts
script_mac="./setup_mac.sh"
script_linux="./setup_ubuntu_local.sh"

# Execute the appropriate script based on the operating system
case "$os_name" in
    Darwin)
        echo "Detected macOS. Executing Mac setup script..."
        chmod u+x "$script_mac"    # Ensure the script is executable
        ./"$script_mac"
        ;;
    Linux)
        echo "Detected Linux. Executing Linux setup script..."
        chmod u+x "$script_linux"  # Ensure the script is executable
        ./"$script_linux"
        ;;
    *)
        echo "Unsupported operating system: $os_name"
        exit 1
        ;;
esac
