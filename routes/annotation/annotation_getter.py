from flask_restful import Resource, reqparse
from neo4j.v1 import ResultError
from connector import neo4j
from routes.utils import addargs, addTimeFilter, makeResponse

class GetAnnotation(Resource):
    """
    @api {get} /annotation/:id Single annotation information
    @apiName GetAnnotation
    @apiGroup Annotation

    @apiParam {Number} id Annotation unique ID.

    @apiSuccess {Json} object The annotation.
    """
    def get(self, annot_id):
        result = neo4j.query_neo4j("MATCH (find:annotation {annotation_id: %d}) RETURN find" % annot_id)
        try:
            return makeResponse(result.single()['find'].properties, 200)
        except ResultError:
            return makeResponse("ERROR : Cannot find annotation with id: %d" % annot_id, 204)


class GetAnnotations(Resource):
    def get(self):
        req = "MATCH (a:annotation) RETURN a.annotation_id AS annotation_id, a.quote AS quote"
        req += addargs()
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append({'annotation_id': record['annotation_id'], "quote": record['quote']})
        return makeResponse(annots, 200)


class GetAnnotationsOnPosts(Resource):
    def get(self):
        req = "MATCH (find:annotation) -[:ANNOTATES]-> (:post) RETURN find.annotation_id AS annotation_id, find.quote AS quote"
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append({'annotation_id': record['annotation_id'], "quote": record['quote']})
        return makeResponse(annots, 200)


class GetAnnotationsOnComments(Resource):
    def get(self):
        req = "MATCH (find:annotation) -[:ANNOTATES]-> (:comment) RETURN find.annotation_id AS annotation_id, find.quote AS quote"
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append({'annotation_id': record['annotation_id'], "quote": record['quote']})
        return makeResponse(annots, 200)


class GetAnnotationsByAuthor(Resource):
    def get(self, user_id):
        req = "MATCH (:user {user_id: %d})-[:AUTHORSHIP]->(a:annotation) RETURN a" % user_id
        req += addargs()
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append(record['a'].properties)
        return makeResponse(annots, 200)


class GetAnnotationsByPost(Resource):
    def get(self, post_id):
        req = "MATCH (p:post {post_id: %d})<-[:ANNOTATES]-(a:annotation) RETURN a" % post_id
        req += addargs()
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append(record['a'].properties)
        return makeResponse(annots, 200)


class GetAnnotationsByComment(Resource):
    def get(self, comment_id):
        req = "MATCH (c:comment {comment_id: %d})<-[:ANNOTATES]-(a:annotation) RETURN a" % comment_id
        req += addargs()
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append(record['a'].properties)
        return makeResponse(annots, 200)

