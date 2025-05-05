#!/bin/bash
# Script to install Node.js and Puppeteer for the EVE Online web scraper

echo "Installing Node.js and Puppeteer for EVE Online web scraping..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Installing Node.js..."
    
    # Install Node.js using package manager
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs
    elif command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew install node
    else
        echo "Could not determine package manager. Please install Node.js manually."
        exit 1
    fi
else
    echo "Node.js is already installed."
fi

# Check Node.js version
NODE_VERSION=$(node -v)
echo "Node.js version: $NODE_VERSION"

# Install Puppeteer
echo "Installing Puppeteer..."
npm install puppeteer

echo "Installation complete!"
echo "You can now use the Puppeteer-based web scraper to fetch EVE Online faction warfare data."

