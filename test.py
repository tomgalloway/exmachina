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
    print c.call.whattime()
    print c.call.listfiles()

if __name__ == '__main__':
    main()
