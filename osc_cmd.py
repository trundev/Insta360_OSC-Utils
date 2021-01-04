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

# Verbosity level (0, 1, 2 or 3)
VERBOSITY = 1

def send_request(conn, *args, **kwargs):
    """Send a generic OSC request"""
    if VERBOSITY > 1:
        print('Request', *args)
        if VERBOSITY > 2:
            print('  Request headers:')
            pprint.pprint(OSC_HEADERS, indent=2)
    body = kwargs.get('body')
    if VERBOSITY > 2 and body is not None:
            print('  Request body:')
            pprint.pprint(body, indent=2)
    # The body must be "str" or "bytes"
    if body is not None and not isinstance(body, (str, bytes)):
        kwargs['body'] = json.dumps(body)

    conn.request(*args, **kwargs, headers=OSC_HEADERS)

    resp = conn.getresponse()
    if VERBOSITY > 2:
        print('  Response headers:')
        pprint.pprint(dict(resp.headers), indent=2)
    data = resp.read()
    if VERBOSITY > 1:
        print('  Response read returned', len(data), 'bytes')
    if KEEP_RESPONSES:
        with open('%s%s.bin'%(args[0], args[1].replace('/', '-')), 'wb') as fd:
            fd.write(data)
    return json.loads(data.decode())

def run_command(conn, cmd_name, cmd_params):
    """Send an OSC command and wait for completion"""
    res = send_request(conn, 'POST', COMMAND_EXECUTE_URL, body={"name": cmd_name, "parameters": cmd_params})
    while res.get('state') == 'inProgress':
        if VERBOSITY > 1:
            print('  Command state "inProgress":', res.get('progress').get('completion'))
        if VERBOSITY > 2:
            pprint.pprint(res, indent=2)
        res = send_request(conn, 'POST', COMMAND_STATUS_URL, body={'id': res['id']})
        time.sleep(COMMAND_POLLING_DELAY)
    return res

def connect(host=OSC_HOST):
    """Connect to the OSC server"""
    conn = http.client.HTTPConnection(host)
    if VERBOSITY > 1:
        print('Connecting to', conn.host)
    conn.connect()
    return conn

def disconnect(conn):
    """Disconnect from the OSC server"""
    return conn.close()

def main(argv):
    """Main entry point"""
    if not argv:
        argv = ['info', 'state']

    conn = None
    while argv:
        # Parse options
        while argv[0][0] == '-':
            if argv[0][:2] == '-v':
                global VERBOSITY
                VERBOSITY = int(argv[0][2:])
            elif argv[0] == '-h':
                return print_help()
            else:
                return print_help('Unsupported option "%s"'%argv[0])
            # Proceed to the next option
            argv = argv[1:]
            if not argv:
                return print_help('Missing OSC command')

        # Must have a connection
        if conn is None:
            conn = connect()

        # Parse commands
        res = None
        if argv[0] == 'info':
            # info request
            res = send_request(conn, 'GET', INFO_URL)
        elif argv[0] == 'state':
            # state request
            res = send_request(conn, 'POST', STATE_URL, body={})
        elif argv[0] == 'checkForUpdates':
            # checkForUpdates request
            if len(argv) < 1:
                return print_help('Missing OSC checkForUpdates stateFingerprint')
            res = send_request(conn, 'POST', CHECKFORUPDATE_URL, body={'stateFingerprint': argv[1]})
            argv = argv[1:]
        elif argv[0] == 'command':
            # command execute/status request
            if len(argv) < 3:
                return print_help('Insufficient OSC command arguments: %s'%argv)
            res = run_command(conn, argv[1], json.loads(argv[2]))
            argv = argv[2:]
        else:
            return print_help('Unsupported command "%s"'%argv[0])
        # Proceed to the next argument
        argv = argv[1:]

        if res is not None:
            if VERBOSITY > 0:
                pprint.pprint(res, indent=2)
            else:
                print(json.dumps(res))

    if conn is not None:
        disconnect(conn)
    return 0

def print_help(err_msg=None):
    if err_msg:
        print('Error:', err_msg, file=sys.stderr)
    print('Usage:', sys.argv[0], '[<options>] <requests>...')
    print('    Options:')
    print('\t-h - This screen')
    print('\t-v<n> - Verbosity level 0, 1, 2 or 3')
    print('    Requests:')
    print('\tinfo  - Basic information about the camera')
    print('\tstate - Mutable values representing camera status')
    print('\tcheckForUpdates <stateFingerprint> - Compare the camera’s current fingerprint')
    print('\tcommand <cmd-name> <cmd-params>    - Execute command')
    print('    Command names:')
    print('\tcamera.getOptions - Get options and features of the camera device')
    print('\t   More commands here https://github.com/Insta360Develop/Insta360_OSC')
    print('\t   See also https://developers.google.com/streetview/open-spherical-camera/reference')
    print('')
    print('    Example:')
    print('\t%s info state command camera.getOptions "{\\"optionNames\\": [\\"iso\\"]}"'%sys.argv[0])
    print('\t%s -v2 command camera.takePicture {}'%sys.argv[0])
    return 0 if err_msg is None else 255

if __name__ == '__main__':
    ret = main(sys.argv[1:])
    if ret:
        exit(ret)
