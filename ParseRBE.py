"""
ParseRBE (Diabotical Map Parsing Lib)
Copyright (C) 2020 Sean Berwick <stringtheory@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct
import math
import copy
import sys

def main():

    # Simple example

    m = MapObject()
    m.Load('input_map_file.rbe')
    m.AddBlock(10, 20, 30)
    m.Save('output_map_file.rbe')
    

class MapObject:

    # TODO before organizing the architecture/porting:
    ############
    # AddBlocks(xyz, xyz) ----- Array or box
    # addTeleporter(xyz entrance, w, h, xyz exit, dir)
    # Set target
    # Set action
    # Clear properties
    # Delete blocks
    # Delete entity
    # https://liquipedia.net/arenafps/Diabotical_map_editing

    ##############
    # ADD: BLOCK #
    ##############
    def AddBlock(self, x, y, z, block_type=1, mats=None, mat_offs=None, orient=2):
        self.block_count += 1
        if mats == None:
            mats = {
                'front': 1,
                'left': 1,
                'back': 1,
                'right': 1,
                'top': 1,
                'bottom': 1
            }
        if mat_offs == None:
            mat_offs = {
                'front': {'x': 0, 'y': 0},
                'left': {'x': 0, 'y': 0},
                'back': {'x': 0, 'y': 0},
                'right': {'x': 0, 'y': 0},
                'top': {'x': 0, 'y': 0},
                'bottom': {'x': 0, 'y': 0}
            }
        newBlock = {
            'x': x,
            'y': y,
            'z': z,
            'type': block_type,
            'u1': 0,
            'mats': mats,
            'u2': 0,
            'mat_offs': mat_offs,
            'orient': orient,
            'u3': 0
        }
        self.blocks.append(newBlock)

    ###############
    # ADD: ENTITY #
    ###############
    def AddEntity(self, name, x=0.0, y=0.0, z=0.0, xrot=0.0, yrot=0.0, zrot=0.0, xscale=1.0, yscale=1.0, zscale=1.0, properties=[]):
        self.entity_count += 1
        newEnt = {
            'name_len': len(name),
            'name':     name,
            'x':        x,
            'y':        y,
            'z':        z,
            'xrot':     xrot,
            'yrot':     yrot,
            'zrot':     zrot,
            'xscale':   xscale,
            'yscale':   yscale,
            'zscale':   zscale,
            'property_count':   len(properties),
            'properties':       properties
        }
        self.entities.append(newEnt)

    ##################
    # FIND: ENTITIES #
    ##################
    def FindEntities(self, name):
        result = []
        for e in self.entities:
            if name.lower() in e['name'].lower():
                result.append(e)
        return result

    ###########################
    # LOAD & PARSE A MAP FILE #
    ###########################
    def Load(self, f):
        with open(f, 'rb') as f:
            self.rebm               = f.read(4).decode("utf-8")
            self.ver                = decodeInt(f.read(4))
            self.u1                 = decodeInt(f.read(16))

            self.material_count     = decodeInt(f.read(1))
            self.materials          = []
            for i in range(self.material_count - 1):
                c = decodeInt(f.read(4))
                m = {
                    'name_len': c,
                    'name':     f.read(c).decode("utf-8")
                    }
                self.materials.append(m)

            self.u2                 = decodeInt(f.read(4))

            self.bounds = {'minx': 0.0, 'maxx': 0.0, 'miny': 0.0, 'maxy': 0.0,  'minz': 0.0, 'maxz': 0.0}
            self.block_count        = decodeInt(f.read(4))
            self.blocks             = []
            for i in range(self.block_count):
                b = {
                    'x':        decodeInt(f.read(4)),
                    'y':        decodeInt(f.read(4)),
                    'z':        decodeInt(f.read(4)),
                    'type':     decodeInt(f.read(1)),
                    'u1':       decodeInt(f.read(12)),
                    'mats':     {
                        'front': decodeInt(f.read(1)),
                        'left': decodeInt(f.read(1)),
                        'back': decodeInt(f.read(1)),
                        'right': decodeInt(f.read(1)),
                        'top': decodeInt(f.read(1)),
                        'bottom': decodeInt(f.read(1)),
                    },
                    'u2':       decodeInt(f.read(1)),
                    'mat_offs': {
                        'front': {
                            'x': decodeInt(f.read(1)),
                            'y': decodeInt(f.read(1))
                        },
                        'left': {
                            'x': decodeInt(f.read(1)),
                            'y': decodeInt(f.read(1))
                        },
                        'back': {
                            'x': decodeInt(f.read(1)),
                            'y': decodeInt(f.read(1))
                        },
                        'right': {
                            'x': decodeInt(f.read(1)),
                            'y': decodeInt(f.read(1))
                        },
                        'top': {
                            'x': decodeInt(f.read(1)),
                            'y': decodeInt(f.read(1))
                        },
                        'bottom': {
                            'x': decodeInt(f.read(1)),
                            'y': decodeInt(f.read(1))
                        },
                    },
                    'orient':   decodeInt(f.read(1)),
                    'u3':       decodeInt(f.read(1))
                }
                self.blocks.append(b)
                self.bounds['minx'] = b['x'] if b['x'] < self.bounds['minx'] or self.bounds['minx'] == 0 else self.bounds['minx']
                self.bounds['maxx'] = b['x'] if b['x'] > self.bounds['maxx'] or self.bounds['maxx'] == 0 else self.bounds['maxx']
                self.bounds['miny'] = b['y'] if b['y'] < self.bounds['miny'] or self.bounds['miny'] == 0 else self.bounds['miny']
                self.bounds['maxy'] = b['y'] if b['y'] > self.bounds['maxy'] or self.bounds['maxy'] == 0 else self.bounds['maxy']
                self.bounds['minz'] = b['z'] if b['z'] < self.bounds['minz'] or self.bounds['minz'] == 0 else self.bounds['minz']
                self.bounds['maxz'] = b['z'] if b['z'] > self.bounds['maxz'] or self.bounds['maxz'] == 0 else self.bounds['maxz']

            self.u3_count           = decodeInt(f.read(4))
            self.u3_raw             = []
            for i in range(self.u3_count):
                self.u3_raw.append(f.read(16))

            self.entity_count       = decodeInt(f.read(4))
            self.entities           = []
            for i in range(self.entity_count):
                c = decodeInt(f.read(4))
                e = {
                    'name_len': c,
                    'name':     f.read(c).decode("utf-8"),
                    'x':        decodeFloat(f.read(4)),
                    'y':        decodeFloat(f.read(4)),
                    'z':        decodeFloat(f.read(4)),
                    'xrot':     radToDeg(decodeFloat(f.read(4))),
                    'yrot':     radToDeg(decodeFloat(f.read(4))),
                    'zrot':     radToDeg(decodeFloat(f.read(4))),
                    'xscale':   decodeFloat(f.read(4)),
                    'yscale':   decodeFloat(f.read(4)),
                    'zscale':   decodeFloat(f.read(4)),
                }
                e['property_count']         = decodeInt(f.read(4))
                e['properties']             = []
                for j in range(e['property_count']):
                    p = {}
                    c = decodeInt(f.read(4))
                    p['name_len'] = c
                    p['name'] = f.read(c).decode("utf-8")
                    c = decodeInt(f.read(4))
                    p['val_len'] = c
                    p['val'] = f.read(c).decode("utf-8")
                    e['properties'].append(p)
                self.entities.append(e)

            self.audio_count        = decodeInt(f.read(4))
            self.audio_raw          = []
            for i in range(self.audio_count):
                a = {
                    'audio_raw': f.read(12),
                    'child_count': decodeInt(f.read(4)),
                    'children': []
                }
                for j in range(a['child_count']):
                    a['children'].append(f.read(12))
                self.audio_raw.append(a)

            self.u4 = decodeInt(f.read(4))

            self.minimap_layer_count    = decodeInt(f.read(4))
            self.minimap_layers         = []
            for i in range(self.minimap_layer_count):
                ly = {
                    'height': decodeInt(f.read(4)),
                    'point_count': decodeInt(f.read(4)),
                    'points': []
                }
                for j in range(ly['point_count']):
                    p = {
                        'x': decodeInt(f.read(4)),
                        'y': decodeInt(f.read(4))
                    }
                    ly['points'].append(p)
                self.minimap_layers.append(ly)

            self.audio_prop_count       = decodeInt(f.read(4))
            self.audio_props            = []
            # for i in range(self.audio_prop_count):
            for i in range(self.audio_prop_count):
                a = {
                    'u1': f.read(138),
                    'name_len': decodeInt(f.read(4)),
                }
                a['name'] = f.read(a['name_len']).decode("utf-8")
                a['u2'] = f.read(14)
                a['u3_count'] = decodeInt(f.read(4))
                a['u3_raw'] = []
                for j in range(a['u3_count']):
                    a['u3_raw'].append(f.read(32))
                self.audio_props.append(a)
            
            self.u5 = f.read()

    ##########################
    # PACK & SAVE A MAP FILE #
    ##########################
    def Save(self, f):
        with open(f, 'wb') as f:
            f.write(encodeString(self.rebm))
            f.write(encodeInt(self.ver, 4))
            f.write(encodeInt(self.u1, 16))

            f.write(encodeInt(self.material_count, 1))
            for m in self.materials:
                f.write(encodeInt(m['name_len'], 4))
                f.write(encodeString(m['name']))

            f.write(encodeInt(self.u2, 4))

            f.write(encodeInt(self.block_count, 4))
            for b in self.blocks:
                f.write(encodeInt(b['x'], 4))
                f.write(encodeInt(b['y'], 4))
                f.write(encodeInt(b['z'], 4))
                f.write(encodeInt(b['type'], 1))
                f.write(encodeInt(b['u1'], 12))
                f.write(encodeInt(b['mats']['front'], 1))
                f.write(encodeInt(b['mats']['left'], 1))
                f.write(encodeInt(b['mats']['back'], 1))
                f.write(encodeInt(b['mats']['right'], 1))
                f.write(encodeInt(b['mats']['top'], 1))
                f.write(encodeInt(b['mats']['bottom'], 1))
                f.write(encodeInt(b['u2'], 1))
                f.write(encodeInt(b['mat_offs']['front']['x'], 1))
                f.write(encodeInt(b['mat_offs']['front']['y'], 1))
                f.write(encodeInt(b['mat_offs']['left']['x'], 1))
                f.write(encodeInt(b['mat_offs']['left']['y'], 1))
                f.write(encodeInt(b['mat_offs']['back']['x'], 1))
                f.write(encodeInt(b['mat_offs']['back']['y'], 1))
                f.write(encodeInt(b['mat_offs']['right']['x'], 1))
                f.write(encodeInt(b['mat_offs']['right']['y'], 1))
                f.write(encodeInt(b['mat_offs']['top']['x'], 1))
                f.write(encodeInt(b['mat_offs']['top']['y'], 1))
                f.write(encodeInt(b['mat_offs']['bottom']['x'], 1))
                f.write(encodeInt(b['mat_offs']['bottom']['y'], 1))
                f.write(encodeInt(b['orient'], 1))
                f.write(encodeInt(b['u3'], 1))

            f.write(encodeInt(self.u3_count, 4))
            for u3 in self.u3_raw:
                f.write(u3)

            f.write(encodeInt(self.entity_count, 4))
            for e in self.entities:
                f.write(encodeInt(e['name_len'], 4))
                f.write(encodeString(e['name']))
                f.write(encodeFloat(e['x']))
                f.write(encodeFloat(e['y']))
                f.write(encodeFloat(e['z']))
                f.write(encodeFloat(degToRad(e['xrot'])))
                f.write(encodeFloat(degToRad(e['yrot'])))
                f.write(encodeFloat(degToRad(e['zrot'])))
                f.write(encodeFloat(e['xscale']))
                f.write(encodeFloat(e['yscale']))
                f.write(encodeFloat(e['zscale']))
                f.write(encodeInt(e['property_count'], 4))
                for p in e['properties']:
                    f.write(encodeInt(p['name_len'], 4))
                    f.write(encodeString(p['name']))
                    f.write(encodeInt(p['val_len'], 4))
                    f.write(encodeString(p['val']))

            f.write(encodeInt(self.audio_count, 4))
            for a in self.audio_raw:
                f.write(a['audio_raw'])
                f.write(encodeInt(a['child_count'], 4))
                for c in a['children']:
                    f.write(c)

            f.write(encodeInt(self.u4, 4))

            f.write(encodeInt(self.minimap_layer_count, 4))
            for ly in self.minimap_layers:
                f.write(encodeInt(ly['height'], 4))
                f.write(encodeInt(ly['point_count'], 4))
                for p in ly['points']:
                    f.write(encodeInt(p['x'], 4))
                    f.write(encodeInt(p['y'], 4))

            f.write(encodeInt(self.audio_prop_count, 4))
            for a in self.audio_props:
                f.write(a['u1'])
                f.write(encodeInt(a['name_len'], 4))
                f.write(encodeString(a['name']))
                f.write(a['u2'])
                f.write(encodeInt(a['u3_count'], 4))
                for u3 in a['u3_raw']:
                    f.write(u3)

            f.write(self.u5)

def encodeInt(data, bytes):
    return data.to_bytes(bytes, "little", signed=True)
def encodeFloat(data):
    return bytearray.fromhex(struct.pack('<f', data).hex())
def encodeString(data):
    return data.encode()
def decodeInt(data):
    return int.from_bytes(data, "little", signed=True)
def decodeFloat(data):
    return struct.unpack('<f', data)[0]
def degToRad(degrees):
    return degrees * math.pi / 180
def radToDeg(radians):
    return radians * 180 / math.pi
if __name__ == '__main__':
    main()