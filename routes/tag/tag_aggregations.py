from flask_restful import Resource, reqparse
from neo4j.v1 import ResultError
from connector import neo4j
from routes.utils import addargs, makeResponse

parser = reqparse.RequestParser()


class CountAllTag(Resource):
    def get(self):
        req = "MATCH (:tag) RETURN count(*) AS nb_tags"
        result = neo4j.query_neo4j(req)
        try:
            return makeResponse(result.single()['nb_tags'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)
            
class CountTagsByParent(Resource):
    def get(self, parent_tag_id):
        req = "MATCH (t:tag {tag_id : %d})<-[:IS_CHILD]-(:tag) RETURN count(*) AS nb_child" % parent_tag_id
        result = neo4j.query_neo4j(req)
        try:
            return makeResponse(result.single()['nb_child'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)

