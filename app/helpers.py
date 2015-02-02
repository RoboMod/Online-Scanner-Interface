import os, time
from datetime import datetime
import pyinsane.abstract as pyinsane
from PIL import Image

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

def scan(device, multiple, parameters):    
    # check if multiple scans possible
    if (multiple == 1) and (not "ADF" in device.options['source'].constraint):
        return
    else:
        device.options['source'].value = "ADF"
        
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
            