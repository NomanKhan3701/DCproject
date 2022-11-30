# Distributed-Movie-Ticket-Booking-System
A Movie Ticket Booking System built on a Distributed Client-Server model in Python (using Sockets and RPC).

Initial Setup:
1. Download [**Nginx**](http://nginx.org/en/docs/windows.html)
2. Copy the `nginx.conf` configuration file to the `conf` directory in extracted Nginx folder. This holds the configuration for the ***Loadbalancer*** for three different locations, each having three server ports.
3. Edit `start_nginx.bat` by adding the path for extracted location of Nginx on *Line 1* and the Project Directory on *Line 5*.
4. Run `start_nginx.bat`.
5. Run `run.bat` from Windows Powershell or Command Prompt ***(as Admin)***. This will create a total of 9 server ports (changeable) by running `CinemaServer.py`.
6. Run the `client1.py` python file.
