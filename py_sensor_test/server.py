import time
from datetime import datetime

from gevent import monkey; monkey.patch_all()
from flask import Flask, render_template, request, json, Response

from gevent import queue
from gevent.pywsgi import WSGIServer

import matplotlib.pyplot as plt
import numpy as np
import math

app = Flask(__name__)
# app.debug = True


def conv_float(val:str):
    try:
        f = float(val)
    except ValueError:
        return 0.0
    else:
        return f

class RotMat():
    def __init__(self, m11:str, m12:str, m13:str, m21:str, m22:str, m23:str, m31:str, m32:str, m33:str):
        self.mat = [ conv_float(m11),
                    conv_float(m12),
                    conv_float(m13),
                    conv_float(m21),
                    conv_float(m22),
                    conv_float(m23),
                    conv_float(m31),
                    conv_float(m32),
                    conv_float(m33),
                ]

    def __str__(self):
        return '[ {:.2f}, {:.2f}, {:.2f}\n {:.2f}, {:.2f}, {:.2f}\n {:.2f}, {:.2f}, {:.2f} ]'.format(self.mat[0],self.mat[1],self.mat[2],self.mat[3],self.mat[4],self.mat[5],self.mat[6],self.mat[7],self.mat[8])

class Rot():
    def __init__(self, alpha:str, beta:str, gamma:str):
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.gamma = float(gamma)

    def __str__(self):
        return 'alpha : {:.2f}, beta : {:.2f}, gamma : {:.2f}'.format(self.alpha, self.beta, self.gamma)

    def append(self, d_alpha, d_beta, d_gamma):
        if len(d_alpha) >= 100: d_alpha.pop(0)
        if len(d_beta) >= 100: d_beta.pop(0)
        if len(d_gamma) >= 100: d_gamma.pop(0)
        d_alpha.append(self.alpha)
        d_beta.append(self.beta)
        d_gamma.append(self.gamma)

class Acceleration():
    def __init__(self, x:str, y:str, z:str):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        return 'acc_x : {:.2f}, acc_y : {:.2f}, acc_z : {:.2f}'.format(self.x, self.y, self.z)

class Pos():
    def __init__(self, latitude:str, longitude:str, altitude:str):
        self.latitude = conv_float(latitude)
        self.longitude = conv_float(longitude)
        self.altitude = conv_float(altitude)

    def __str__(self):
        return 'latitude : {}, longitude : {}, altitude : {:.2f}'.format(self.latitude, self.longitude, self.altitude)

class Vec():
    def __init__(self, x:str, y:str, z:str):
        self.x = conv_float(x)
        self.y = conv_float(y)
        self.z = conv_float(z)

    def __str__(self):
        return 'x : {}, y : {}, z : {:.2f}'.format(self.x, self.y, self.z)


data = []
d_alpha = []
d_beta = []
d_gamma = []
fig, axes = plt.subplots(3,1)
alines, = axes[0].plot(np.array(range(0,100)), np.zeros(100))
blines, = axes[1].plot(np.array(range(0,100)), np.zeros(100))
glines, = axes[2].plot(np.array(range(0,100)), np.zeros(100))
plt.pause(.01)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pose', methods=['post'])
def post_pose():
    # print(request.form)
    rot = Rot(request.form['alpha'], request.form['beta'], request.form['gamma'])
    acc = Acceleration(request.form['x'], request.form['y'], request.form['z'])
    pos = Pos(request.form['lati'], request.form['longi'], request.form['alt'])
    mat = RotMat(request.form['m11'], request.form['m12'], request.form['m13'],request.form['m21'], request.form['m22'], request.form['m23'],request.form['m31'], request.form['m32'], request.form['m33'])
    # print(mat)
    heading = Vec(request.form['hx'], request.form['hy'], request.form['hz'])
    heading2 = [heading.x, -heading.y, heading.z]
    yaw = math.degrees(math.atan2(heading2[1], heading2[0]))
    pitch = math.degrees(math.acos(heading2[2]))
    print(heading)
    print(heading2)
    print('yaw: {}, pitch: {}'.format(yaw, pitch))
    data.append([rot, acc, pos])
    rot.append(d_alpha, d_beta, d_gamma)
    # print(d_alpha)
    # ref: https://qiita.com/hausen6/items/b1b54f7325745ae43e47
    # ref: https://aiacademy.jp/media/?p=154
    # print(rot)
    x = np.array(range(0, len(d_alpha)))
    y = np.array(d_alpha)
    alines.set_data(x, y)
    axes[0].set_ylim([y.min(), y.max()])
    y = np.array(d_beta)
    blines.set_data(x, y)
    axes[1].set_ylim([y.min(), y.max()])
    y = np.array(d_gamma)
    glines.set_data(x, y)
    axes[2].set_ylim([y.min(), y.max()])
    # print(x)
    # print(y)
    plt.pause(.01)
    return b''

@app.route('/time')
def doyouhavethetime():
    def generate():
        while True:
            yield "{}\n".format(datetime.now().isoformat())
            time.sleep(1)
    return Response(generate(), mimetype='text/plain')

print('Serving on https://:443')
# see src/gevent/tests/test__ssl.py for how to generate
server = WSGIServer(('0.0.0.0', 443), app, keyfile='server.key', certfile='server.crt')
# to start the server asynchronously, call server.start()
# we use blocking serve_forever() here because we have no other jobs
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    print('done')
    # for rot, acc, pos in data:
    #     print(rot)
    #     print(acc)
    #     print(pos)

