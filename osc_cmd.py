"""Insta360 ONE R/ONE X control over Google OSC

See:
  https://github.com/Insta360Develop/Insta360_OSC
  https://developers.google.com/streetview/open-spherical-camera
"""
import sys
import json
import pprint
import http.client

# IP address of the Insta360 ONE R WiFi AP
OSC_HOST = '192.168.42.1'
OSC_HEADERS = {'Accept': 'application/json'}
INFO_URL = '/osc/info'
STATE_URL = '/osc/state'
CHECKFORUPDATE_URL = '/osc/checkForUpdates'
COMMAND_EXECUTE_URL = '/osc/commands/execute'
COMMAND_STATUS_URL = '/osc/commands/status'

def send_request(conn, *args, **kwargs):
    print('Request', *args)
    body = kwargs.get('body')
    # The body must be "str" or "bytes"
    if body is not None and not isinstance(body, (str, bytes)):
        kwargs['body'] = json.dumps(body)

    conn.request(*args, **kwargs, headers=OSC_HEADERS)

    resp = conn.getresponse()
    #print('  Responce headers:')
    #pprint.pprint(dict(resp.headers), indent=2)
    data = resp.read()
    print('  Responce read returned', len(data), 'bytes')
    return json.loads(data.decode())

def main(argv):
    """Main entry point"""
    conn = http.client.HTTPConnection(OSC_HOST)
    print('Connecting to', conn.host)
    conn.connect()

    # info request
    data = send_request(conn, 'GET', INFO_URL)
    pprint.pprint(data, indent=2)

    # state request
    data = send_request(conn, 'POST', STATE_URL, body={})
    pprint.pprint(data, indent=2)

    # camera.getOptions command
    data = send_request(conn, 'POST', COMMAND_EXECUTE_URL, body={
                "name": "camera.getOptions",
                "parameters": {
                    "optionNames":
                    ["iso", "isoSupport", "hdrSupport", "hdr", "totalSpace", "remainingSpace"]
                }
            })
    pprint.pprint(data, indent=2)

    conn.close()
    return 0

if __name__ == '__main__':
    ret = main(sys.argv[1:])
    if ret:
        exit(ret)
