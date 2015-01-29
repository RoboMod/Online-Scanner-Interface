import os, time
from datetime import datetime
import pyinsane.abstract as pyinsane
from PIL import Image

from flask import Flask, render_template, g, request, send_from_directory
from flask_bootstrap import Bootstrap
import flask_sijax

sijax_path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = Flask(__name__)

app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)

app.config['SIJAX_STATIC_PATH'] = sijax_path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)

def getScanners():
    devices = pyinsane.get_devices()
    return devices

def getScanner(scanners, model):
    device = None
    for scanner in scanners:
        if scanner.model == model:
            device = scanner
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
    return render_template('main.html')
    #return redirect(url_for('scanners'))
    
@app.route('/scans/<path:filename>')
def scans(filename):
    return send_from_directory(app.root_path + '/scans/', filename) 

@app.route('/scanners/')
def scanners():
    return render_template('scanners.html', scanners=getScanners())

@flask_sijax.route(app, '/scanner/<model>')
def scanner(model):
    devices = getScanners()
    device = getScanner(devices, model)
    
    scans = getScans(model)
    
    def simple_scan(obj_response, model, multiple, parameters):
        device = getScanner(getScanners(), model)
        
        scan_session = device.scan(multiple=multiple)
        try:
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        
        image = scan_session.images[0]
        path = "./scans/" + model + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".png"
        image.save(path)
        
        obj_response.html('#scan_tbody', render_template('scan.html', scanner=device, scans=scans))
        
    if g.sijax.is_sijax_request:
        g.sijax.register_callback('simple_scan', simple_scan)
        return g.sijax.process_request()
            
    return render_template('scanner.html', scanners=devices, scanner=device, scans=scans)


if __name__ == '__main__':
    app.run(debug=True)