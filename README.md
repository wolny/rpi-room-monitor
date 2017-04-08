# rpi-room-monitor

Simple home surveillance app to be installed on Raspberry Pi with the camera board. 

The app scans the local network and checks if any of the configured trusted devices is present in the network.
If at least one trusted device (MAC address) is discovered on the local network then any movement in the room is ignored.
Otherwise if no trusted devices are present and the motion is detected within the camera range, the app captures the photo
of the the room and uploads it to Flickr and/or the FTP server.

Phones, eReaders or other personal WiFi-capable devices should be picked as a "trusted devices", so that the surveillance
is activated as soon as one leaves it's home WiFi range.

Motion detection module inspired by [this great post](http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/).

## Installation
On your Raspberry Pi:
- `sudo apt-get install arp-scan`; `arp-scan` needs to be needs to be run as root in order to open a link-layer socket so one might add `myuser ALL = (root) NOPASSWD: /usr/bin/arp-scan` to the sudoers file
- `sudo pip3 install flickrapi`
- `sudo pip3 install influxdb`
- [install OpenCV](http://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/)
- get the [Flickr API key](https://www.flickr.com/services/apps/create/)
- `python3 flickr_auth.py -c config.json` in order to [authenticate with flickr](https://stuvel.eu/flickrapi-doc/3-auth.html#authenticating-without-local-web-server); needs to be run from the terminal within the X-server, since the Pi's default web browser will be opened
- run the app: `python3 monitor.py -c config.json`
- `sudo cp delete_old_frames.sh /etc/cron.daily/delete-old-frames`; all the frames on which the motion was detected will be kept in `/tmp` dir, this script cleans it up (by default removes images older than 4 days); make sure that the script in `/etc/cron.daily` doesn't have the `.sh` extension


## Configuration
Sample `config.json`:
```
{
  "arp_scanner_interval": 10,
  "state_check_interval": 4,
  "network_prefix": "192.168.0",
  "trusted_macs": [
    "test"
  ],
  "resolution": [
    800,
    600
  ],
  "framerate": 16,
  "flickr_enabled": true,
  "flickr_api_key": "FLICKR_API_KEY",
  "flickr_api_secret": "FLICKR_API_SECRET",
  "ftp_enabled": true,
  "ftp_host": "FTP_HOST",
  "ftp_user": "FTP_USER",
  "ftp_passwd": "FTP_PASSWD",
  "ftp_dir": "FTP_DIR",
  "influxdb_host": "INFLUXDB_HOST",
  "influxdb_port": "INFLUXDB_PORT",
  "influxdb_db": "INFLUXDB_DB"
}
```
- `arp_scanner_interval` - number of sec. between each ARP protocol scans used to determine MAC addresses present in the LAN
- `state_check_interval` - number of sec. between photos (if any) are sent to Flickr/FTP server
- `network_prefix` - consider only hosts with network addresses with this prefix (optional)
- `trusted_macs` - list of trusted MAC addresses, which if present on the network disables the surveillance
- the rest config values are self-explanatory

## Recommended hardware
- [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
- [Raspberry Pi 2](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/)
- [Raspberry Pi 1 B+](https://www.raspberrypi.org/products/model-b-plus/) would work as well