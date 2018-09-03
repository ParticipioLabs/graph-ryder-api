from flask_restful import Resource, reqparse
from neo4j.v1.exceptions import ResultError
from connector import neo4j
from routes.utils import addargs, makeResponse

parser = reqparse.RequestParser()


class CountUsersByTimestamp(Resource):
    """
    @api {get} /users/count/timestamp?start=:start&end=:end Count users
    @apiName CountUsersByTimestamp
    @apiGroup User
    @apiDescription Count all users by timestamp

    @apiSuccess {Number} timestamp Timestamp of a step.
    @apiSuccess {Number} count Number of users.

    @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        [{
            "timestamp": 1315749060000,
            "count": 1
        },
        {
            "timestamp": 1316199060000,
            "count": 2
        },
        {
            "timestamp": 1316351640000,
            "count": 3
        }]
    """
    def get(self):
#        req = "MATCH (n:user) "
#        req += "RETURN n.timestamp AS timestamp ORDER BY timestamp ASC"
        req = "MATCH (n: user) -[:AUTHORSHIP]-> (e) "
        req += "RETURN n.user_id, min(e.timestamp) AS timestamp ORDER BY timestamp ASC"
        result = neo4j.query_neo4j(req)
        users = []
        count = 1
        for record in result:
            users.append({"count": count, "timestamp": record['timestamp']})
            count += 1
        return makeResponse(users, 200)


class CountUsers(Resource):
    """
    @api {get} /users/count Count users
    @apiName CountUsers
    @apiGroup User
    @apiDescription Count all users
    """
    def get(self):
        req = "MATCH (n:user) RETURN count(*) AS nb_users"
        result = neo4j.query_neo4j(req)
        try:
            return makeResponse(result.single()['nb_users'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)
