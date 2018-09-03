import uuid
from flask_restful import Resource
from neo4j.v1.exceptions import ResultError
from connector import neo4j
from routes.utils import addargs, makeResponse
from graphtulip.createtlp import CreateTlp


class ShortestPathBetweenUsers(Resource):
    def get(self, user1_id, user2_id, max_hop):
        req = "MATCH path=shortestPath((u1:user {user_id: %d})-[*..%d]-(u2:user {user_id: %d}))RETURN path" % (
            user1_id, max_hop, user2_id)
        print(req)
        results = neo4j.query_neo4j(req)
        try:
            result = results.single()
            print(result['path'])
            # print(result['path'].start)
            # print(result['path'].end)
            print(type(result['path']))
            return 'I don\'t understand the result, sorry.', 202
        except ResultError:
            return makeResponse("ERROR : Cannot find a path between uid: %d and uid: %d with maximum %d hop" % (
                user1_id, user2_id, max_hop), 204)
