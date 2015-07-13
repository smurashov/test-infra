#!/bin/bash
set -x
for i in $(virsh list | awk '/paused/{print $2}'); do
  sudo lvcreate -sn $i-snapshot -l 100%ORIGIN vms/$i
  snap_arg=""
  case $i in
  fuel )
    snap_arg="--diskspec hdb,snapshot=no"
    ;;
  compute-* )
    snap_arg="--diskspec hdb,snapshot=no"
    sudo lvcreate -sn $i-ceph-snapshot -l 100%ORIGIN vms/$i-ceph
    ;;
  esac
  virsh snapshot-create-as $i $i-snapshot --atomic --memspec /var/lib/libvirt/qemu/save/$i-snapshot --diskspec hda,snapshot=no $snap_arg
  sleep 20
done
