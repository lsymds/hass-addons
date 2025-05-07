#!/bin/bash

# Control mechanism for local development of hass-addons. Creates and initializes a KVM VM for HAOS and provides tools
# to manage it.

HAOS_VERSION="15.2"

function usage
{
  echo "
Usage: $0 [bootstrap|create|destroy|start|stop|uninstall]

Creates and manages a local KVM VM for local development of Home Assistant Addons.

Commands:
  bootstrap   Installs any required packages to allow the running of the HAOS VM
  create      Creates and bootstraps the HAOS VM
  destroy     Destroys the HAOS VM and any associated resources
  start       Starts the HAOS VM if it is in a non-running state
  stop        Stops the HAOS VM
  uninstall   Removes all KVM packages from the system
"
}

function bootstrap
{
  echo "Bootstrapping required utilities for HAOS VM..."

  # sudo setfacl -m u:libvirt-qemu:x /home/foo

  # Verify that this machine supports virtualisation.
  echo "Verifying virtualisation support..."
  VIRT_COUNT=$(egrep -c '(vmx|svm)' /proc/cpuinfo)
  if [ $VIRT_COUNT -le 0 ]; then
    echo "Processor does not support virtualisation. Try enabling it."
    exit 1
  fi

  # Update package catalogues
  echo "Updating package repositories..."
  sudo apt update -y

  # Install relevant KVM packages
  echo "Installing required KVM packages..."
  sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst wget -y
}

function uninstall
{
  echo "Removing KVM packages..."
  sudo apt remove qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst -y
}

function create
{
  if _vm_exists; then
    echo "HAOS VM already exists. Please run './control.sh destroy' followed by './control.sh create' to recreate it."
    exit 1
  fi

  # Download HAOS VM image
  echo "Downloading HAOS VM image..."
  wget -O haos_vm.qcow2.xz "https://github.com/home-assistant/operating-system/releases/download/$HAOS_VERSION/haos_ova-$HAOS_VERSION.qcow2.xz"
  xz --decompress haos_vm.qcow2.xz

  # Create the HAOS VM using the HAOS VM image as the base.
  echo "Creating HAOS VM..."
  virt-install \
    --name haos \
    --description "Home Assistant OS" \
    --os-variant=generic \
    --ram=4096 \
    --vcpus=2 \
    --disk haos_vm.qcow2,bus=scsi \
    --controller type=scsi,model=virtio-scsi \
    --filesystem type=mount,source=$(pwd),target=addons,accessmode=mapped \
    --import \
    --graphics none \
    --boot uefi \
    --noautoconsole

  # Print details about the VM
  echo "Waiting for VM to be assigned an IP address..."

  MAX_ATTEMPTS=10 # Fewer attempts might be needed for NAT as libvirt usually assigns quickly
  ATTEMPT=0

  while [[ -z "$(virsh domifaddr "haos" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n 1)" ]]; do
    ATTEMPT=$((attempt + 1))
    if [[ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]]; then
      echo "Error: Max attempts reached. Could not retrieve IP address for VM."
      exit 1
    fi
    sleep 3
  done

  VM_IP=$(virsh domifaddr haos | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n 1)

  echo "HomeAssistant OS VM created"
  echo "HomeAssistant URL: http://$VM_IP:8123"
  echo "!IMPORTANT!: You need to log in to the VM ('virsh console haos' and run 'mount -t 9p addons /mnt/data/supervisor/addons/local') to map the current folder to the local addons directory."
}

function start
{
  if ! _vm_exists; then
    echo "Cannot start a non-existent VM."
    exit 1
  fi

  echo "Starting HomeAssistant OS VM..."
  virsh start haos
  echo "!IMPORTANT!: You need to log in to the VM ('virsh console haos' and run 'mount -t 9p addons /mnt/data/supervisor/addons/local') to map the current folder to the local addons directory."
}

function stop
{
  if ! _vm_exists; then
    exit 0
  fi

  echo "Stopping HomeAssistant OS VM..."
  virsh shutdown haos
}

function destroy
{
  if ! _vm_exists; then
    exit 0
  fi

  echo "Destroying VM and removing all storage"
  virsh destroy haos
  virsh undefine haos --nvram --remove-all-storage
}

function _vm_exists
{
  if [ "$(virsh list --all | grep " haos " | awk '{ print $3}')" != "" ]; then
    return 0
  else
    return 1
  fi
}

case $1 in
  bootstrap)
    bootstrap
    ;;
  create)
    create
    ;;
  destroy)
    destroy
    ;;
  start)
    start
    ;;
  stop)
    stop
    ;;
  uninstall)
    uninstall
    ;;
  *)
    usage
    ;;
esac
