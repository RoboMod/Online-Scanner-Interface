from __future__ import unicode_literals

import os, time
from datetime import datetime
import pyinsane.abstract as pyinsane
from PIL import Image

from flask import Flask, render_template, g, request, send_from_directory
from flask_bootstrap import Bootstrap
import flask_sijax

# activate debug mode
DEBUG = False

app = Flask(__name__)

app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)

sijax_path = os.path.join(app.root_path, 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = sijax_path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)

@app.template_filter('hasValue')
def hasValue(obj, value):
    return (value in obj)

def getScanners():
    devices = pyinsane.get_devices()
    # load pickle devices if no one connect (only for debugging)
    if len(devices) == 0:
        import pickle
        f = open('devices.dump', 'rb')
        devices = pickle.load(f)
        f.close()
    return devices

def getScanner(scanners, model):
    device = None
    for scanner in scanners:
        if scanner.model == model:
            device = scanner
            #device.options['source'].constraint.remove("ADF")
    return device

def getScans(model):
    fileInfos = []
    for f in os.listdir(app.root_path + '/scans/'):
        if f.startswith(model) and (f.endswith('jpeg') or f.endswith('png') or f.endswith('tiff')):
            size = os.path.getsize(app.root_path + '/scans/' + f)
            ctime = time.ctime(os.path.getctime(app.root_path + '/scans/' + f))
            fileInfos.append({"name":f, "size":size, "ctime":ctime})
    return fileInfos

@app.route('/')
def index():
    return render_template('index.html', scanners=getScanners())

@app.route('/about')
def about():
    return render_template('about.html', scanners=getScanners())

@app.route('/scans/<path:filename>')
def scans(filename):
    return send_from_directory(app.root_path + '/scans/', filename)

@app.route('/scanners/')
def scanners():
    devices = getScanners()
    scans = {}
    for device in devices:
        scans[device.model] = getScans(device.model)

    return render_template('scanners.html', scanners=devices, scans=scans)

@flask_sijax.route(app, '/scanner/<model>')
def scanner(model):
    devices = getScanners()
    device = getScanner(devices, model)

    scans = getScans(model)

    def scan(obj_response, model, multiple, parameters): #TODO: use parameters
        device = getScanner(getScanners(), model)
        multiple = int(multiple)
        
        # check if multiple scans possible
        if (multiple == 1) and (not "ADF" in device.options['source'].constraint):
            return
        else:
            device.options['source'].value = "ADF"
        
        #yield obj_response.script(u"$('#simplescan').prop('disabled', true);")
        
        if not DEBUG:
            # set parameters
            #for p in parameters.keys():
            #    device.options[p].value = parameters[p]
            print "bla"
            # start scan
            scan_session = device.scan(multiple=multiple)
            
            # run scan session
            if multiple:
                try:
                    while True:
                        try:
                            scan_session.scan.read()
                        except EOFError:
                            pass
                except StopIteration:
                    pass
                
                # save images
                path_base = "./scans/" + model + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "_"
                for i in range(0, len(scan_session.images)):
                    image = scan_session.images[i]
                    image.save(path + i + ".png")
            else:
                try:
                    while True:
                        scan_session.scan.read()
                except EOFError:
                    pass

                # save image
                image = scan_session.images[0]
                path = "./scans/" + model + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".png"
                image.save(path)

        #obj_response.html('#scan_tbody', render_template('scan.html', scanner=device, scans=scans))

    if g.sijax.is_sijax_request:
        g.sijax.register_comet_callback('scan', scan)
        return g.sijax.process_request()

    return render_template('scanner.html', scanners=devices, scanner=device, scans=scans)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
