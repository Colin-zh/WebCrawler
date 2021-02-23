#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def tx2bd(lng,lat):
    import math
    x_pi = (3.14159265358979324 * 3000.0) / 180.0
    x,y = float(lng),float(lat)
    z = math.sqrt( x * x + y * y) + 0.0002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi)
    lng = z * math.cos(theta) + 0.0065
    lat = z * math.sin(theta) + 0.006
    return (lng, lat)
