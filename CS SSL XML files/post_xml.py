#!/usr/bin/python

# <!--
# The MIT License (MIT)

# Copyright (c) 2015 Citrix Systems, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  -->

import glob
import json
import os
import os.path
import requests
import sys
import time
import xml.dom.minidom
import yaml

try:
    xmlFile = sys.argv[1]
except Exception as e:
    print str(e)
    sys.exit(0)

apic = sys.argv[2]

auth = {
    'aaaUser': {
        'attributes': {
            'name':'admin',
            'pwd':'netscaler!'
            }
        }
    }

status = 0
while( status != 200 ):
    url = 'https://%s/api/aaaLogin.json' % apic
    while(1):
        try:
            r = requests.post( url, data=json.dumps(auth), timeout=1, verify=False )
            break;
        except Exception as e:
            print "timeout"
    status = r.status_code
    print r.text
    cookies = r.cookies
    time.sleep(1)

def runConfig( status ):
            with open( xmlFile, 'r' ) as payload:
                if( status==200):
                    time.sleep(5)
                else:
                    raw_input( 'Hit return to process %s' % xmlFile )

                data = payload.read()
                print '++++++++ REQUEST (%s) ++++++++' % xmlFile
                print data
                print '-------- REQUEST (%s) --------' % xmlFile 
                url = 'https://%s/api/node/mo/.xml' % apic 
                r = requests.post( url,
                                   cookies=cookies,
                                   data=data, verify=False )
                result = xml.dom.minidom.parseString( r.text )
                status = r.status_code
                print '++++++++ RESPONSE (%s) ++++++++' % xmlFile
                print result.toprettyxml()
                print '-------- RESPONSE (%s) --------' % xmlFile
                print status

runConfig( status )
