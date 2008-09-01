#! /usr/bin/env python

import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse

from django.utils import simplejson

class TestHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parts = urlparse(self.path)
        query = parts[2]
        params = [param.split("=") for param in parts[4].split("&")]
        if query == "/book/":
            if params and params[0][0] == "id":
                id = int(params[0][1])
                if id == 1:
                    title = "SICP"
                elif id == 2:
                    title = "jQuery programming"
                else:
                    title = "NA"
                self.wfile.write(
                    simplejson.dumps(
                        {'id':id,'title':title}
                    )
                )
            else:
                self.wfile.write("")
        elif query == "/timeout/":
            time.sleep(4)
            self.wfile.write("")
        else:
            self.wfile.write("")
    def do_POST(self):
        parts = urlparse(self.path)
        query = parts[2]
        self.wfile.write(simplejson.dumps("success"))

HTTPServer(('localhost',9090), TestHTTPRequestHandler).serve_forever()
