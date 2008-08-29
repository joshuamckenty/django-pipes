import os, subprocess, signal, time

httppid = None

def setup():
    global httppid
    httpserver = os.path.join(os.path.dirname(__file__), "testhttpserver.py")
    httppid = subprocess.Popen([httpserver]).pid
    time.sleep(1) # give some time for the spawned HTTPServer to start

def teardown():
    print "\nTeardown"
    os.kill(httppid, signal.SIGKILL)
