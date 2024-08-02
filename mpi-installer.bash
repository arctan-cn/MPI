#!/bin/bash  
echo "MPI Installer v0.1"
if [ $# -eq 1 ]; then
    version=$1
    echo "Custom version: $version"
else
    echo "Checking latest version..."
    version=$(wget -qO- "https://projects.async.ltd/mpi/latest/VERSION")
    echo "Latest version: $version"
fi
packname="mpi-$version.tar.gz"
echo "Installing MPI v$version..."
wget -O "$packname" "https://projects.async.ltd/mpi/versions/$packname"
echo "Unzipping $packname..."
tar -zxvf "$packname"
echo "Deleting $packname..."
rm "$packname"
echo "MPI $version Installed."