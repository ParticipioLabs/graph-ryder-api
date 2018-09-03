from flask_restful import Resource, reqparse
from neo4j.v1.exceptions import ResultError
from connector import neo4j
from routes.utils import addargs, addTimeFilter, makeResponse

parser = reqparse.RequestParser()

class GetTag(Resource):
    def get(self, tag_id):
        result = neo4j.query_neo4j("MATCH (find:tag {tag_id: %d}) RETURN find" % tag_id)
        try:
            return makeResponse(result.single()['find'].properties, 200)
        except ResultError:
            return makeResponse("ERROR : Cannot find tag with tid: %d" % tag_id, 204)

class GetTags(Resource):
    def get(self):
        req = "MATCH (t:tag) RETURN t.tag_id AS tag_id, t.label AS label"
        req += addargs()
        result = neo4j.query_neo4j(req)
        tags = []
        for record in result:
            tags.append({'tag_id': record['tag_id'], "label": record['label']})
        return makeResponse(tags, 200)
        
class GetTagsByParent(Resource):
    def get(self, parent_tag_id):
        req = "MATCH (parent:tag {tag_id : %d})<-[:IS_CHILD]-(child:tag) RETURN child" % parent_tag_id
        result = neo4j.query_neo4j(req)
        tags = []
        for record in result:
            tags.append(record['child'].properties)
        return makeResponse(tags, 200)

class GetTagHydrate(Resource):
    """
    @api {get} /tag/hydrate/:id Single tag information + annotation/posts/comments
    @apiName GetTagHydrate
    @apiGroup Tag
    @apiDescription Get tag info and its annotations/comments/posts list (only aid/cid/pid, title and timestamp)

    @apiParam {Number} id Tag unique ID.

    @apiSuccess {Json} object The tag.
    """
    def get(self, tag_id):
        # Get tag node
        req = "MATCH (find:tag {tag_id: %d}) RETURN find" % tag_id
        result = neo4j.query_neo4j(req)
        tag = result.single()['find'].properties
        # Get annotation's posts
        req = "MATCH (find:tag {tag_id: %d})" % tag_id
        req += " MATCH (find)<-[:REFERS_TO]-(a:annotation)"
        req += " MATCH (a)-[:ANNOTATES]->(p:post)"
        req += ' MATCH (p)<-[:AUTHORSHIP]-(u:user)'
        req += ' RETURN a.annotation_id AS annotation_id, a.timestamp AS annotation_timestamp, p.post_id as post_id, p.title as post_title, p.timestamp as post_timestamp, u.user_id as user_id, u.label as user_name ORDER BY post_timestamp DESC'
        result = neo4j.query_neo4j(req)
        annotations_posts = []
        annotations_posts_id = []

        for record in result:
            try:
                if record['annotation_id'] and record['annotation_id'] not in annotations_posts_id:
                    annotation = {}
                    annotation['annotation_id'] = record['annotation_id']
                    annotation['post_id'] = record['post_id']
                    annotation['post_title'] = record['post_title']
                    annotation['post_timestamp'] = record['post_timestamp']
                    annotation['user_id'] = record['user_id']
                    annotation['user_name'] = record['user_name']
                    annotations_posts.append(annotation)
                    annotations_posts_id.append(annotation['annotation_id'])
            except KeyError:
                pass
        # Get annotation's comments
        req = "MATCH (find:tag {tag_id: %d})" % tag_id
        req += " MATCH (find)<-[:REFERS_TO]-(a:annotation)"
        req += " MATCH (a)-[:ANNOTATES]->(c:comment)"
        req += ' MATCH (c)<-[:AUTHORSHIP]-(u:user)'
        req += ' RETURN a.annotation_id AS annotation_id, a.timestamp AS annotation_timestamp, c.comment_id as comment_id, c.title as comment_title, c.timestamp as comment_timestamp, u.user_id as user_id, u.label as user_name ORDER BY comment_timestamp DESC'
        result = neo4j.query_neo4j(req)
        annotations_comments = []
        annotations_comments_id = []

        for record in result:
            try:
                if record['annotation_id'] and record['annotation_id'] not in annotations_comments_id:
                    annotation = {}
                    annotation['annotation_id'] = record['annotation_id']
                    annotation['comment_id'] = record['comment_id']
                    annotation['comment_title'] = record['comment_title']
                    annotation['comment_timestamp'] = record['comment_timestamp']
                    annotation['user_id'] = record['user_id']
                    annotation['user_name'] = record['user_name']
                    annotations_comments.append(annotation)
                    annotations_comments_id.append(annotation['annotation_id'])
            except KeyError:
                pass

        try:
            tag
        except NameError:
            return makeResponse("ERROR : Cannot find tag with tid: %d" % tag_id, 204)
        tag['posts'] = annotations_posts
        tag['comments'] = annotations_comments
        return makeResponse(tag, 200)

