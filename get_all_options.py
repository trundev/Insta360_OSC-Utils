"""Get all Google OSC options

See:
  https://developers.google.com/streetview/open-spherical-camera/reference/options
"""
import sys
import osc_cmd
import pprint

# All Google OSC options as of Jan 2-nd, 2021 (58 options)
OSC_OPTIONS = [
    'captureMode',
    'captureModeSupport',
    'captureStatus',
    'captureStatusSupport',
    'exposureProgram',
    'exposureProgramSupport',
    'iso',
    'isoSupport',
    'shutterSpeed',
    'shutterSpeedSupport',
    'aperture',
    'apertureSupport',
    'whiteBalance',
    'whiteBalanceSupport',
    'exposureCompensation',
    'exposureCompensationSupport',
    'fileFormat',
    'fileFormatSupport',
    'exposureDelay',
    'exposureDelaySupport',
    'sleepDelay',
    'sleepDelaySupport',
    'offDelay',
    'offDelaySupport',
    'totalSpace',
    'remainingSpace',
    'remainingPictures',
    'gpsInfo',
    'dateTimeZone',
    'hdr',
    'hdrSupport',
    'exposureBracket',
    'exposureBracketSupport',
    'gyro',
    'gyroSupport',
    'gps',
    'gpsSupport',
    'imageStabilization',
    'imageStabilizationSupport',
    'wifiPassword',
    'previewFormat',
    'previewFormatSupport',
    'captureInterval',
    'captureIntervalSupport',
    'captureNumber',
    'captureNumberSupport',
    'remainingVideoSeconds',
    'pollingDelay',
    'delayProcessing',
    'delayProcessingSupport',
    'clientVersion',
    'photoStitchingSupport',
    'photoStitching',
    'videoStitchingSupport',
    'videoStitching',
    'videoGPSSupport',
    'videoGPS',
    '_vendorSpecific',
]

def main(argv):
    """Main entry point"""
    conn = osc_cmd.connect()
    if conn is None:
        return 1

    # Try all options one-by-one to isolate unsupported one's
    supported = {}
    unsupported = []
    for opt in OSC_OPTIONS:
        print('Trying: %s...'%opt)
        res = osc_cmd.run_command(conn, 'camera.getOptions', {"optionNames": [opt]})
        if 'results' in res:
            opts = res['results']['options']
            res = opts.get(opt)
            pprint.pprint(res, indent=2)
        else:
            res = None

        if res is None:
            unsupported.append(opt)
            print('Option %s is not supported'%(opt), file=sys.stderr)
            pprint.pprint(res, indent=2)
            # Workaround:
            # No response after unsupported option
            osc_cmd.disconnect(conn)
            conn = osc_cmd.connect()
        else:
            supported[opt] = res

    osc_cmd.disconnect(conn)

    print('')
    print('Summary')
    print('Supported options:')
    pprint.pprint(supported, indent=2)
    print('Unsupported options:')
    pprint.pprint(unsupported, indent=2)
    print('Total %d supported and %d unsupported of %d options'%(
            len(supported), len(unsupported), len(OSC_OPTIONS)))
    return 0

if __name__ == '__main__':
    ret = main(sys.argv[1:])
    if ret:
        exit(ret)
