#!/usr/bin/env python

import sys
import optparse
import logging
import socket

import bjsonrpc
import bjsonrpc.connection
import augeas

# =============================================================================
# Command line handling
def main():

    socket_path="/tmp/exmachina.sock"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)

    c = bjsonrpc.connection.Connection(sock)
    print "time: %s" % c.call.test_whattime()
    print "files: %s" % c.call.test_listfiles()
    print c.call.initd_status("bluetooth")
    print "/*: %s" % c.call.augeas_match("/*")
    print "/files/*: %s" % c.call.augeas_match("/files/*")
    print "/files/etc/*: %s" % c.call.augeas_match("/files/etc/*")
    print "/augeas/*: %s" % c.call.augeas_match("/augeas/*")
    print "hostname: %s" % c.call.augeas_get("/files/etc/hostname/*")
    print "localhost: %s" % c.call.augeas_get("/files/etc/hosts/1/canonical")

if __name__ == '__main__':
    main()
