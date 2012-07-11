#!/usr/bin/env python

# Author: bnewbold <bnewbold@robocracy.org>
# Date: July 2012
# License: GPLv3 (see http://www.gnu.org/licenses/gpl-3.0.html)

import os
import sys
import optparse
import logging
import socket
import subprocess
import stat

import bjsonrpc
import bjsonrpc.handlers
import bjsonrpc.server
import augeas

import time # TODO

log = logging.getLogger(__name__)

def run_service(servicename, action, timeout=10):
    """This function mostly ripped from StackOverflow:
    http://stackoverflow.com/questions/1556348/python-run-a-process-with-timeout-and-capture-stdout-stderr-and-exit-status
    """
    # ensure service name isn't tricky trick
    script = "/etc/init.d/" + os.path.split(servicename)[1]

    if not os.path.exists(script):
        return "ERROR: so such service"

    command_list = [script, action]
    log.info("running: %s" % command_list)
    proc = subprocess.Popen(command_list,
                            bufsize=0,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    poll_seconds = .250
    deadline = time.time() + timeout
    while time.time() < deadline and proc.poll() == None:
        time.sleep(poll_seconds)

    if proc.poll() == None:
        if float(sys.version[:3]) >= 2.6:
            proc.terminate()
        raise Exception("Timeout: %s" % command_list)

    stdout, stderr = proc.communicate()
    return stdout, stderr, proc.returncode

class ExMachinaHandler(bjsonrpc.handlers.BaseHandler):
    
    def _setup(self):
        self.augeas = augeas.Augeas()

    def test_whattime(self):
        log.debug("whattime")
        return time.time()

    def test_listfiles(self):
        log.debug("listfiles")
        return self.augeas.match("/files/etc/*")

    # ------------- Augeas API Passthrough -----------------
    def augeas_save(self):
        log.info("augeas: saving config")
        return self.augeas.save()

    def augeas_set(self, path, value):
        log.info("augeas: set %s=%s" % (path, value))
        return self.augeas.set(path.encode('utf-8'),
                               value.encode('utf-8'))

    def augeas_setm(self, base, sub, value):
        log.info("augeas: setm %s %s = %s" % (base, sub, value))
        return self.augeas.setm(base.encode('utf-8'),
                                sub.encode('utf-8'),
                                value.encode('utf-8'))

    def augeas_get(self, path):
        # reduce verbosity
        log.debug("augeas: get %s" % path)
        return self.augeas.get(path.encode('utf-8'))

    def augeas_match(self, path):
        # reduce verbosity
        log.debug("augeas: match %s" % path)
        return self.augeas.match("%s" % path.encode('utf-8'))

    def augeas_insert(self, path, label, before=True):
        log.info("augeas: insert %s=%s" % (path, value))
        return self.augeas.insert(path.encode('utf-8'),
                                  label.encode('utf-8'),
                                  before=before)

    def augeas_move(self, src, dst):
        log.info("augeas: move %s -> %s" % (src, dst))
        return self.augeas.move(src.encode('utf-8'), dst.encode('utf-8'))

    def augeas_remove(self, path):
        log.info("augeas: remove %s" % path)
        return self.augeas.remove(path.encode('utf-8'))

    # ------------- Service Control -----------------
    def initd_status(self, servicename):
        return run_service(servicename, "status")

    def initd_start(self, servicename):
        return run_service(servicename, "start")

    def initd_stop(self, servicename):
        return run_service(servicename, "stop")

    def initd_restart(self, servicename):
        return run_service(servicename, "restart")
    
class ExMachinaClient():
    pass #TODO

def run_server(socket_path="/tmp/exmachina.sock"):
    # TODO: check for root permissions, warn if not root

    if os.path.exists(socket_path):
        os.unlink(socket_path)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_path)
    sock.listen(1)

    serv = bjsonrpc.server.Server(sock, handler_factory=ExMachinaHandler)

    # TODO: group permissions only?
    os.chmod(socket_path, 0777)

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
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)

    if options.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    run_server()

if __name__ == '__main__':
    main()
