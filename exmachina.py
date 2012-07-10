#!/usr/bin/env python

# Author: bnewbold <bnewbold@robocracy.org>
# Date: July 2012
# License: GPLv3 (see http://www.gnu.org/licenses/gpl-3.0.html)

import os
import sys
import optparse
import logging
import socket

import bjsonrpc
import bjsonrpc.handlers
import bjsonrpc.server
import augeas

import time # TODO

log = logging.getLogger(__name__)


class ExMachinaHandler(bjsonrpc.handlers.BaseHandler):
    def whattime(self):
        print "hup!"
        return time.time()

    def listfiles(self):
        a = augeas.Augeas()
        return a.match("/files/etc/*")
    
class ExMachinaClient():
    pass #TODO

def run_server(socket_path="/tmp/exmachina.sock"):
    # TODO: check for root permissions, warn if not root
    log.info('This is an INFO level message.')
    log.debug('This is a DEBUG level message.')
    log.warn('This is a WARN level message.')

    # TODO: if socket file exists, try to delete it

    if os.path.exists(socket_path):
        os.unlink(socket_path)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_path)
    sock.listen(1)

    serv = bjsonrpc.server.Server(sock, handler_factory=ExMachinaHandler)
    serv.serve()

# =============================================================================
# Command line handling
def main():

    global log
    parser = optparse.OptionParser(usage=
        "usage: %prog [options]\n"
        "%prog --help for more info."
    )
    parser.add_option("-v", "--verbose", 
        default=False,
        help="Show more debugging statements", 
        action="store_true")

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("Incorrect number of arguments")

    log = logging.getLogger()
    if options.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    run_server()

if __name__ == '__main__':
    main()
