#!/bin/sh
# remove files older than 4 days
find /tmp/motion* -type f -ctime 4 -delete