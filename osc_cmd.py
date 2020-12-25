"""Insta360 ONE R/ONE X control over Google OSC

See:
  https://github.com/Insta360Develop/Insta360_OSC
  https://developers.google.com/streetview/open-spherical-camera
"""
import sys
import json
import time
import pprint
import http.client

# IP address of the Insta360 ONE R WiFi AP
OSC_HOST = '192.168.42.1'
OSC_HEADERS = {'Accept': 'application/json', 'X-XSRF-Protected': 1}
INFO_URL = '/osc/info'
STATE_URL = '/osc/state'
CHECKFORUPDATE_URL = '/osc/checkForUpdates'
COMMAND_EXECUTE_URL = '/osc/commands/execute'
COMMAND_STATUS_URL = '/osc/commands/status'

# Keep time-gap betweeen status polling requests
COMMAND_POLLING_DELAY = 1

# Keep each response in a file for debugging purposes
KEEP_RESPONSES = False

def send_request(conn, *args, **kwargs):
    """Send a generic OSC request"""
    print('Request', *args)
    body = kwargs.get('body')
    # The body must be "str" or "bytes"
    if body is not None and not isinstance(body, (str, bytes)):
        kwargs['body'] = json.dumps(body)

    conn.request(*args, **kwargs, headers=OSC_HEADERS)

    resp = conn.getresponse()
    #print('  Response headers:')
    #pprint.pprint(dict(resp.headers), indent=2)
    data = resp.read()
    print('  Response read returned', len(data), 'bytes')
    if KEEP_RESPONSES:
        with open('%s%s.bin'%(args[0], args[1].replace('/', '-')), 'wb') as fd:
            fd.write(data)
    return json.loads(data.decode())

def run_command(conn, cmd_name, cmd_params):
    """Send an OSC command and wait for completion"""
    res = send_request(conn, 'POST', COMMAND_EXECUTE_URL, body={"name": cmd_name, "parameters": cmd_params})
    while res.get('state') == 'inProgress':
        print('  Command state "inProgress":', res.get('progress').get('completion'))
        #pprint.pprint(res, indent=2)
        res = send_request(conn, 'POST', COMMAND_STATUS_URL, body={'id': res['id']})
        time.sleep(COMMAND_POLLING_DELAY)
    return res

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
    data = run_command(conn, "camera.getOptions", {
                "optionNames":
                ["iso", "isoSupport", "hdrSupport", "hdr", "totalSpace", "remainingSpace"]
            })
    pprint.pprint(data, indent=2)

    # camera.takePicture command
    data = run_command(conn, COMMAND_EXECUTE_URL, {"name": "camera.takePicture"})
    pprint.pprint(data, indent=2)

    conn.close()
    return 0

if __name__ == '__main__':
    ret = main(sys.argv[1:])
    if ret:
        exit(ret)
