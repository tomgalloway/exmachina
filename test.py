#!/usr/bin/env python

import sys
import optparse
import logging
import socket

import bjsonrpc
import bjsonrpc.connection
import augeas

from exmachina import ExMachinaClient

# =============================================================================
# Command line handling
def main():

    socket_path="/tmp/exmachina.sock"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)

    print "========= Testing low level connection"
    c = bjsonrpc.connection.Connection(sock)
    print "time: %s" % c.call.test_whattime()
    print "/*: %s" % c.call.augeas_match("/*")
    print "/augeas/*: %s" % c.call.augeas_match("/augeas/*")
    print "/etc/* files:"
    for name in c.call.augeas_match("/files/etc/*"):
        print "\t%s" % name
    print c.call.initd_status("bluetooth")
    print "hostname: %s" % c.call.augeas_get("/files/etc/hostname/*")
    print "localhost: %s" % c.call.augeas_get("/files/etc/hosts/1/canonical")

    print "========= Testing user client library"
    client = ExMachinaClient()
    print client.augeas.match("/files/etc/*")
    print client.initd.restart("bluetooth")

if __name__ == '__main__':
    main()
