from app import app
from flask import render_template, g, request, send_from_directory
import flask_sijax

@app.template_filter('hasValue')
def hasValue(obj, value):
    return (value in obj)

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

    def scan(obj_response, model, multiple, parameters):
        #yield obj_response.script(u"$('#simplescan').prop('disabled', true);")
        
        device = getScanner(getScanners(), model)
        scan(device, multiple, parameters)       

        #obj_response.html('#scan_tbody', render_template('scan.html', scanner=device, scans=scans))

    if g.sijax.is_sijax_request:
        g.sijax.register_comet_callback('scan', scan)
        return g.sijax.process_request()

    return render_template('scanner.html', scanners=devices, scanner=device, scans=scans)