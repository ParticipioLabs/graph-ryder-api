from flask_restful import Resource, reqparse
from neo4j.v1.exceptions import ResultError
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


class GetAnnotationHydrate(Resource):
    """
    @api {get} /annotation/hydrate/:id Single annotation information
    @apiName GetAnnotationHydrate
    @apiGroup Annotation

    @apiParam {Number} id Annotation unique ID.

    @apiSuccess {Json} object The annotation.
    """
    def get(self, annotation_id):
        req = "MATCH (find:annotation {annotation_id: %d})" % annotation_id
        req += "MATCH (find)-[:ANNOTATES]->(x)"
        req += 'RETURN find, labels(x) as test'
        result = neo4j.query_neo4j(req)
        #annotation = result.single()['find'].properties
        annotateComment=False
        for record in result:
            annotation = record['find'].properties
            try:
                if "comment" in record["test"]:
                    annotateComment=True
            except KeyError:
                return makeResponse("ERROR : Impossible to identify 'entity_type' for annotation with aid: %d" % annotation_id, 205)

        if annotateComment:
            req = "MATCH (find:annotation {annotation_id: %d})-[:REFERS_TO]->(t: tag)  " % annotation_id
            req += "MATCH (find)-[:ANNOTATES]->(c:comment)"
            req += "MATCH (c)<-[:AUTHORSHIP]-(u:user)"
            req += 'RETURN find, c.comment_id as entity_id, c.title as entity_title, c.timestamp as entity_timestamp, u.user_id as user_id, u.label as user_name, "comment" as entity_type, t.tag_id as tag_id, t.label as tag_label ORDER BY c.timestamp DESC'
        else:
            req = "MATCH (find:annotation {annotation_id: %d})-[:REFERS_TO]->(t: tag) " % annotation_id
            req += "MATCH (find)-[:ANNOTATES]->(p:post)"
            req += "MATCH (p)<-[:AUTHORSHIP]-(u:user)"
            req += 'RETURN find, p.post_id as entity_id, p.title as entity_title, p.timestamp as entity_timestamp, u.user_id as user_id, u.label as user_name, "post" as entity_type, t.tag_id as tag_id, t.label as tag_label ORDER BY p.timestamp DESC'

        result = neo4j.query_neo4j(req)
        for record in result:
            try:
                annotation['user_id'] = record['user_id']
                annotation['user_name'] = record['user_name']
                annotation['entity_id'] = record['entity_id']
                annotation['entity_title'] = record['entity_title']
                annotation['entity_timestamp'] = record['entity_timestamp']
                annotation['entity_type'] = record['entity_type']
                annotation['tag_id'] = record['tag_id']
                annotation['tag_label'] = record['tag_label']
            except KeyError:
                return makeResponse("ERROR : Cannot find annotation with aid: %d" % annotation_id, 203)

        try:
            annotation
        except NameError:
            return makeResponse("ERROR : Cannot find annotation with aid: %d" % annotation_id, 204)
        return makeResponse(annotation, 200)


class GetAnnotations(Resource):
    def get(self):
        req = "MATCH (a:annotation)-[:REFERS_TO]->(t:tag) MATCH (a)-[:ANNOTATES]-(x) RETURN a.annotation_id AS annotation_id, a.quote AS quote, t.tag_id AS tag_id, CASE x.post_id WHEN null THEN 'comment' ELSE 'post' END AS entity_type, CASE x.post_id WHEN null THEN x.comment_id ELSE x.post_id END AS entity_id"
        req += addargs()
        result = neo4j.query_neo4j(req)
        annots = []
        for record in result:
            annots.append({'annotation_id': record['annotation_id'], "quote": record['quote'], "tag_id": record['tag_id'], "entity_type": record["entity_type"], "entity_id": record["entity_id"]})
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

