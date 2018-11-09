import configparser
import os
import tempfile

from flask_restful import Resource, reqparse
from routes.utils import makeResponse
from tulip import *

config = configparser.ConfigParser()
config.read("config.ini")

parser = reqparse.RequestParser()


class GetLayoutAlgorithm(Resource):
    def get(self):
        return makeResponse(tlp.getLayoutAlgorithmPluginsList(), 200)


class DrawGraph(Resource):
    def __init__(self, **kwargs):
        self.gid_stack = kwargs['gid_stack']

    def get(self, public_gid, layout):
        # Dirty hack bug fix
        layout = 'GEM (Frick)'
        private_gid = self.gid_stack[public_gid]
        if not os.path.isfile("%s%s.tlp" % (config['exporter']['tlp_path'], private_gid)):
            return makeResponse("Unknow graph id : %s" % public_gid)
        tulip_graph = tlp.loadGraph("%s%s.tlp" % (config['exporter']['tlp_path'], private_gid))
        tulip_graph.applyLayoutAlgorithm(layout)
        path = tempfile.mkstemp()
        ds = tlp.getDefaultPluginParameters("SIGMA JSON Export", tulip_graph)
        tlp.exportGraph("SIGMA JSON Export", tulip_graph, path[1], ds)
        return makeResponse(path[1], 200, True)
