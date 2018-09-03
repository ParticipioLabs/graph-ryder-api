from flask_restful import Resource, reqparse
from neo4j.v1.exceptions import ResultError
from connector import neo4j
from routes.utils import addargs, makeResponse

parser = reqparse.RequestParser()

class CountByTimestamp(Resource):
    def get(self, type, min, max):
        req = "MATCH (n:%s) WHERE n.timestamp >= %d AND n.timestamp <= %d RETURN n.timestamp AS timestamp ORDER BY timestamp ASC" % (type, min, max)
        req += addargs()
        result = neo4j.query_neo4j(req)
        val = []
        count = 1
        for record in result:
            val.append({"count": count, "timestamp": record['timestamp']})
            count += 1
        return makeResponse(val, 200)
