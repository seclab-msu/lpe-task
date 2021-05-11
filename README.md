* Import OVA to virtualbox as some user
* Modify the host-only network settings of the machine, note the DHCP IP address range
* `docker-compose up -d --build` - build an run the submitter webserv
* python execution_queue.py $IP $user_password - execute the executor, use first IP of the host-only net addr range and the password of user `user` from OVA.

