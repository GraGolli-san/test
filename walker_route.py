#!/usr/bin/env python


import glob
import os
import sys
import time

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from enum import IntEnum, auto

class RouteMode(IntEnum):
    RouteSave = auto()
    RouteLoad = auto()


class RouteData():

    def __init__(self, elapsed_time, transform):
        self.elapsed_time = elapsed_time
        self.transform = transform
        self.loc = transform.location
        self.rot = transform.rotation

    def __str__(self):
        return f'{self.elapsed_time:.3f} {self.loc.x:.3f} {self.loc.y:.3f} {self.loc.z:.3f} {self.rot.pitch:.1f} {self.rot.yaw:.1f} {self.rot.roll:.1f}'



class WalkerRoute():

    def __init__(self, world, delta_seconds, mode):
        self.world = world
        self.delta_seconds = delta_seconds
        self.elapsed_time = 0.0
        self.mode = mode

        self.map_name = world.get_map().name
        self.dirname = f'{self.map_name}_WalkerRoute'
        self.all_walker_actors = []
        self.file_pointers = []

    def __del__(self):
        # ファイルをクローズ
        for fp in self.file_pointers:
            fp.close()


    def init_save(self):
        # 全walker_actor取得
        for actor in  self.world.get_actors():
            if ("walker.pedestrian." in actor.type_id):
                # print(actor)
                self.all_walker_actors.append(actor)

        # ファイルポインタの作成
        os.makedirs(self.dirname, exist_ok=True)
        for i in range(len(self.all_walker_actors)):
            filename = "%s\\w%06d.txt" % (self.dirname, i)
            # print(filename)
            self.file_pointers.append(open(filename,mode='w'))

    def tick_save(self):
        # ファイルへ位置情報の書き込み
        for i in range(len(self.all_walker_actors)):
            trans = self.all_walker_actors[i].get_transform()
            # loc = trans.location
            # rot = trans.rotation
            # trans_str = f'{self.elapsed_time:.3f} {loc.x:.3f} {loc.y:.3f} {loc.z:.3f} {rot.pitch:.1f} {rot.yaw:.1f} {rot.roll:.1f}\n'
            rdata = RouteData(self.elapsed_time, trans)
            trans_str = str(rdata) + "\n"
            self.file_pointers[i].write(trans_str)

        self.elapsed_time += self.delta_seconds


    def init_load(self):
        
