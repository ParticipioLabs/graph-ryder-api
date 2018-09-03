from flask_restful import Resource
from neo4j.v1.exceptions import ResultError
from connector import neo4j
from routes.utils import addargs, makeResponse


class GetUser(Resource):
    """
    @api {get} /user/:id Single user information
    @apiName GetUser
    @apiGroup User

    @apiParam {Number} id User unique ID.

    @apiSuccess {Json} object The user.
    """
    def get(self, user_id):
        req = "MATCH (find:user {user_id: %d}) RETURN find" % user_id
        result = neo4j.query_neo4j(req)
        try:
            return makeResponse(result.single()['find'].properties, 200)
        except ResultError:
            return makeResponse("ERROR : Cannot find user with uid: %d" % user_id, 204)


class GetUserHydrate(Resource):
    """
    @api {get} /user/hydrate/:id Single user information + posts/comments
    @apiName GetUserHydrate
    @apiGroup User
    @apiDescription Get user info and his comments/posts list (only comment_id/post_id, title and timestamp)

    @apiParam {Number} id User unique ID.

    @apiSuccess {Json} object The user.
    """
    def get(self, user_id):
        # Get user properties
        req = "MATCH (find:user {user_id: %d}) RETURN find" % user_id
        result = neo4j.query_neo4j(req)
        user = result.single()['find'].properties
        # Get user's posts
        req = "MATCH (find:user {user_id: %d})" % user_id
        req += " MATCH (find)-[:AUTHORSHIP]->(p:post)"
        req += ' RETURN p.post_id AS post_id, p.label AS post_label, p.timestamp AS timestamp ORDER BY p.timestamp DESC'
        result = neo4j.query_neo4j(req)
        posts = []
        posts_id = []

        for record in result:
            try:
                if record['post_id'] and record['post_id'] not in posts_id:
                    post = {}
                    post['post_id'] = record['post_id']
                    post['label'] = record['post_label']
                    post['timestamp'] = record['timestamp']
                    posts.append(post)
                    posts_id.append(post['post_id'])
            except KeyError:
                pass
        # Get user's comments
        req = "MATCH (find:user {user_id: %d})" % user_id
        req += " MATCH (find)-[:AUTHORSHIP]->(c:comment)"
        req += " OPTIONAL MATCH (c)-[:COMMENTS]->(p:post)"
        req += ' RETURN c.comment_id AS comment_id, c.label AS comment_label, c.timestamp AS timestamp, p.post_id AS comment_parent_post_id, p.label AS comment_parent_post_label ORDER BY c.timestamp DESC'
        result = neo4j.query_neo4j(req)
        comments_id = []
        comments = []

        for record in result:
            try:
                if record['comment_id'] and record['comment_id'] not in comments_id:
                    comment = {}
                    comment['comment_id'] = record['comment_id']
                    comment['label'] = record['comment_label']
                    comment['timestamp'] = record['timestamp']
                    comment['comment_parent_post_id'] = record['comment_parent_post_id']
                    comment['comment_parent_post_label'] = record['comment_parent_post_label']
                    comments.append(comment)
                    comments_id.append(comment['comment_id'])
            except KeyError:
                pass

        try:
            user
        except NameError:
            return makeResponse("ERROR : Cannot find user with user_id: %d" % user_id, 204)
        user['posts'] = posts
        user['comments'] = comments
        return makeResponse(user, 200)


class GetUsers(Resource):
    """
    @api {get} /users/?limit=:limit&orderBy:order Users lists
    @apiName GetUsers
    @apiGroup User
    @apiDescription Get all users

    @apiParam {Number} [limit] Array size limit
    @apiParam {String} [order=uid:desc] "field:[desc|asc]"

    @apiSuccess {Json} array Users list.
    """
    def get(self):
        req = "MATCH (n:user) RETURN n.user_id AS user_id, n.label AS label"
        req += addargs()
        result = neo4j.query_neo4j(req)
        users = []
        for record in result:
            users.append({'user_id': record['user_id'], "label": record['label']})
        return makeResponse(users, 200)
