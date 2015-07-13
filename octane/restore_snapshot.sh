#!/bin/bash
set -x
for i in $(virsh list --all | awk '/shut/{print $2}'); do
  sudo lvconvert --merge vms/$i-snapshot -i 5
  sudo lvcreate -sn $i-snapshot -l 100%ORIGIN vms/$i
  case $i in
  compute-* )
    sudo lvconvert --merge vms/$i-ceph-snapshot -i 5
    sudo lvcreate -sn $i-ceph-snapshot -l 100%ORIGIN vms/$i-ceph
    ;;
  esac
  virsh restore /var/lib/libvirt/qemu/save/$i-snapshot --paused
  sleep 20
done
