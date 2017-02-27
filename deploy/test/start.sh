#!/bin/bash

# reset VMs
echo "Destroying previous vagrant VM if any and creating new one..."
vagrant destroy -f && vagrant up
echo "vagrant VM is up"

echo "start ansible"
ansible-playbook web.yml
