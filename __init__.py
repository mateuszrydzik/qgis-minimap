# -*- coding: utf-8 -*-
def classFactory(iface):
    from .minimap import MinimapPlugin
    return MinimapPlugin(iface)
