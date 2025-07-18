#!/bin/bash
# Script: update.sh
# Description: Downloads and extracts configuration templates from GitHub repository
# Author: Thomas Schmelzer
# Usage: ./update.sh

# Download the configuration templates zip file from GitHub
# -L follows redirects, -o specifies the output filename
curl -L -o templates.zip https://github.com/tschm/.config-templates/archive/refs/heads/main.zip

# Extract the contents of the downloaded zip file
unzip templates.zip

# Copy the extracted configuration files to the current directory
cp -r .config-templates-main/. .

# Clean up by removing the zip file and the extracted directory
# This prevents cluttering the workspace with temporary files
rm -rf templates.zip .config-templates-main

# Git operations: create or checkout the config-sync branch, commit changes
# Check if the config-sync branch exists
if git show-ref --verify --quiet refs/heads/config-sync; then
    # Branch exists, check it out
    git checkout config-sync
else
    # Branch doesn't exist, create and check it out
    git checkout -b config-sync
fi

# Add all changes to git
git add .

# Commit the changes
git commit -m "Update configuration templates from tschm/.config-templates"

git push origin config-sync