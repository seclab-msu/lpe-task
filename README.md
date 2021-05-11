* Import OVA to virtualbox as some user
* Modify the host-only network settings of the machine, note the DHCP IP address range:
```
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet2 --ip 192.168.56.1
VBoxManage dhcpserver add --ifname vboxnet2 --ip 192.168.56.1 --netmask 255.255.255.0 --lowerip 192.168.56.100 --upperip 192.168.56.200
VBoxManage dhcpserver modify --ifname vboxnet2 --enable
VBoxManage startvm "LPE-TASK"  --type headless
VBoxManage dhcpserver --interface=vboxnet2 findlease --mac-address=080027AE2623
```

* `docker-compose up -d --build` - build an run the submitter webserv
* python execution_queue.py $IP $user_password - execute the executor, use first IP of the host-only net addr range and the password of user `user` from OVA.

