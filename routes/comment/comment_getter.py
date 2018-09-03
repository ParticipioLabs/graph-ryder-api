from flask_restful import Resource
from neo4j.v1.exceptions import ResultError
from connector import neo4j
from routes.utils import addargs, makeResponse
import datetime

class GetComment(Resource):
    def get(self, comment_id):
        req = "MATCH (find:comment {comment_id: %d}) RETURN find" % comment_id
        result = neo4j.query_neo4j(req)
        try:
            return makeResponse(result.single()['find'].properties, 200)
        except ResultError:
            return makeResponse("ERROR : Cannot find comment with cid: %d" % comment_id, 204)


class GetCommentHydrate(Resource):
    def get(self, comment_id):
        req = "MATCH (find:comment {comment_id: %d}) " % comment_id
        req += "OPTIONAL MATCH (find)<-[:AUTHORSHIP]-(author:user) "
        req += "OPTIONAL MATCH (find)-[:COMMENTS]->(post:post) "
        req += "RETURN find, author.user_id AS user_id, author.label AS user_name, post.post_id AS post_id, post.title AS post_title, post.url AS post_url"
        result = neo4j.query_neo4j(req)
        author = {}
        post = {}
        for record in result:
            comment = record['find'].properties
            try:
                if record['user_id']:
                    author['user_id'] = record['user_id']
                if record['user_name']:
                    author['user_name'] = record['user_name']
                if record['post_id']:
                    post['post_id'] = record['post_id']
                if record['post_title']:
                    post['post_title'] = record['post_title']
                if record['post_url']:
                    post['post_url'] = record['post_url']
            except KeyError:
                pass
        # annotations
        req = "MATCH (find:comment {comment_id: %d}) " % comment_id
        req += "OPTIONAL MATCH (find)<-[:ANNOTATES]-(a:annotation) "
        req += "OPTIONAL MATCH (a)-[:REFERS_TO]->(t:tag) "
        req += "RETURN a.annotation_id as annotation_id, a.timestamp as annotation_timestamp, t.tag_id as tag_id, t.label as tag_label"
        result = neo4j.query_neo4j(req)
        annotations = []
        annotations_id = []
        for record in result:
            annotation = {} 
            try:
                if record['tag_id'] and record['annotation_id'] not in annotations_id:
                    if record['annotation_id']:
                        annotation['annotation_id'] = record['annotation_id']
                    if record['annotation_timestamp']:
                        annotation['annotation_timestamp'] = record['annotation_timestamp']
                    if record['tag_id']:
                        annotation['tag_id'] = record['tag_id']
                    if record['tag_label']:
                        annotation['tag_label'] = record['tag_label']
                    annotations.append(annotation)
                    annotations_id.append(record['annotation_id'])
            except KeyError:
                pass

        # response comments
        req = 'MATCH (find:comment {comment_id: %d}) ' % comment_id
        req += 'OPTIONAL MATCH (find)<-[:COMMENTS]-(c2:comment) '
        req += 'OPTIONAL MATCH (c2:comment)<-[:AUTHORSHIP]-(author:user) '
        req += 'RETURN find.comment_id AS initial_comment_id, c2.comment_id AS response_id, c2.label AS response_label, c2.timestamp AS response_timestamp, author.user_id AS author_id, author.label AS author_label ORDER BY response_timestamp DESC'
        result = neo4j.query_neo4j(req)
        resp_comments = []
        for record in result:
            resp_comment = {}
            try:
                if record['response_id']:
                    resp_comment['comment_id'] = record['response_id']
                    if record['response_label']:
                        resp_comment['comment_label'] = record['response_label']
                    if record['response_timestamp']:
                        resp_comment['comment_timestamp'] = record['response_timestamp']
                    if record['author_id']:
                        resp_comment['user_id'] = record['author_id']
                    if record['author_label']:
                        resp_comment['user_label'] = record['author_label']
                    resp_comments.append(resp_comment)
            except KeyError:
                pass

        try:
            comment
        except NameError:
            return "ERROR : Cannot find post with pid: %d" % comment_id, 200
        comment['author'] = author
        comment['post'] = post
        comment['annotations'] = annotations
        comment['comments'] = resp_comments
        return makeResponse(comment, 200)


class GetComments(Resource):
    def get(self):
        req = "MATCH (c:comment)<-[:AUTHORSHIP]-(u:user) MATCH (c)-[:COMMENTS]->(p:post) RETURN c.comment_id AS comment_id, c.title AS title, c.content AS content, c.timestamp AS timestamp, u.user_id AS user_id, p.post_id AS post_id"
        req += addargs()
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            fmt_time = datetime.datetime.fromtimestamp(record['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
            comments.append({'comment_id': record['comment_id'], "title": record['title'], "content": record["content"], "date": fmt_time, "user_id": record["user_id"], "post_id": record["post_id"]})
        return makeResponse(comments, 200)


class GetCommentsLatest(Resource):
    def get(self):
        req = "MATCH (c: comment) <-[:AUTHORSHIP]- (u: user) RETURN c.comment_id AS comment_id, c.label AS comment_label, u.user_id AS user_id, u.label AS user_label, c.timestamp AS timestamp ORDER BY timestamp DESC LIMIT 5"
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            comments.append({'comment_id': record['comment_id'], "comment_label": record['comment_label'], "user_id": record['user_id'], "user_label": record['user_label'], "timestamp": record['timestamp']})
        return makeResponse(comments, 200)


class GetCommentsByAuthor(Resource):
    def get(self, author_id):
        req = "MATCH (author:user {user_id: %d})-[:AUTHORSHIP]->(c:comment) RETURN c" % author_id
        req += addargs()
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            comments.append(record['c'].properties)
        return makeResponse(comments, 200)


class GetCommentsOnPost(Resource):
    def get(self, post_id):
        req = "MATCH (c:comment)-[:COMMENTS]->(post:post { post_id: %d}) RETURN c" % post_id
        req += addargs()
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            comments.append(record['c'].properties)
        return makeResponse(comments, 200)


class GetCommentsOnComment(Resource):
    def get(self, comment_id):
        req = "MATCH (c:comment)-[:COMMENTS]->(comment:comment { comment_id: %d}) RETURN c" % comment_id
        req += addargs()
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            comments.append(record['c'].properties)
        return makeResponse(comments, 200)
