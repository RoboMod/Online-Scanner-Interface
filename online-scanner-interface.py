from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import pyinsane.abstract as pyinsane

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('main.html')
    #return redirect(url_for('scanner'))

@app.route('/scanners/')
@app.route('/scanners/<model>')
def scanners(model=None):
    devices = pyinsane.get_devices()
    return render_template('scanners.html', scanners=devices)

if __name__ == '__main__':
    app.run(debug=True)