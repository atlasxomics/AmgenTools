#!/bin/bash

# Check if systemd is running
if [ "$(pidof systemd)" ]; then
    echo "Systemd is running. Installing custom service..."
else
    echo "Systemd is not running. Exiting..."
    exit 1
fi

# Define the custom service unit content
custom_service_unit="[Unit]
Description=Custom Service
After=network.target

[Service]
Type=simple
ExecStart=/root/PortableAtlasTools/portable_tools.sh

[Install]
WantedBy=multi-user.target"

# Path to store the custom service unit file
custom_service_unit_file="/etc/systemd/system/portable_tools.service"

# Write the custom service unit file
echo "$custom_service_unit" | sudo tee "$custom_service_unit_file" > /dev/null

# Reload systemd to read the new unit file
sudo systemctl daemon-reload

# Enable and start the custom service
sudo systemctl enable portable_tools.service
sudo systemctl start portable_tools.service

echo "Custom service installed and started."
