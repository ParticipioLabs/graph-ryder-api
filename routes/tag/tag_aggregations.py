from flask_restful import Resource, reqparse
from neo4j.v1.exceptions import ResultError
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

class TagsByDate(Resource):
    def get(self, timestamp1, timestamp2, limit):
        req = "match (n)<-[:ANNOTATES]-(a:annotation)-[:REFERS_TO]->(t:tag) where n.timestamp > %d and n.timestamp < %d and ('post' in labels(n) or 'comment' in labels(n)) return t.tag_id as id, t.label as label, count(t) as count order by count desc limit %d" % (timestamp1, timestamp2, limit)
        result = neo4j.query_neo4j(req)
        tags=[]
        for record in result:
            tags.append({'id': record['id'], "label": record['label'], "count": record['count']})

        try:
            return makeResponse(tags, 200)
        except ResultError:
            return makeResponse("ERROR", 500)

class CoocurrencesByTag(Resource):
    def get(self, tag_id):
        req = "MATCH (t1: tag {tag_id: %d})--(a1: annotation)-[:ANNOTATES]->(e:post)<-[:ANNOTATES]-(a2:annotation)--(t2: tag) where t1<>t2 return t2, count(e) as count order by count desc" % tag_id
        result = neo4j.query_neo4j(req)
        tags = []
        for record in result:
            tag = record['t2'].properties
            if record['count']:
                tag['count'] = record['count']
            tags.append(tag) 
        try:
            return makeResponse(tags,200)
        except ResultError:
            return makeResponse("ERROR",500)

class ContentWithCommonTags(Resource):
    def get(self, tag_id1, tag_id2):
        req = "MATCH (find:tag {tag_id: %d}) RETURN find" % tag_id1
        result = neo4j.query_neo4j(req)
        tag1 = result.single()['find'].properties

        req = "MATCH (find:tag {tag_id: %d}) RETURN find" % tag_id2
        result = neo4j.query_neo4j(req)
        tag2 = result.single()['find'].properties

        response = {}
        if tag1['tag_id'] <= tag2['tag_id']:
            response['tag_src'] = tag1
            response['tag_dst'] = tag2
        else:
            response['tag_src'] = tag2
            response['tag_dst'] = tag1

        req = "match (t1: tag {tag_id: %d})<-[:REFERS_TO]-(a: annotation)-[:ANNOTATES]->(e) " % tag_id1
        req += "match (e)<-[:ANNOTATES]-(a2: annotation)-[:REFERS_TO]->(t2: tag {tag_id: %d}) " % tag_id2
        req += "match (e)<-[:AUTHORSHIP]-(u: user) "
        req += "return distinct t1.tag_id, CASE e.post_id when null then e.comment_id else e.post_id end as id, CASE e.post_id WHEN null THEN 'comment' ELSE 'post' END as entity_type, e.timestamp as timestamp, e.label as label, u.user_id as user_id, u.label as user_label, t2.tag_id ORDER BY e.timestamp DESC"
        result = neo4j.query_neo4j(req)

        tags = []
        for record in result:
            tags.append({'id': record['id'], "entity_type": record['entity_type'], "timestamp": record['timestamp'], 'label': record['label'], 'user_id': record['user_id'], 'user_label': record['user_label']}) 

        response['list'] = tags
        try:
            tags
        except ResultError:
            return makeResponse("ERROR",500)
        return makeResponse(response, 200)

class ContentWithCommonTagsByDate(Resource):
    def get(self, tag_id1, tag_id2, start_date, end_date):
        req = "match (t1: tag {tag_id: %d})<-[:REFERS_TO]-(a: annotation)-[:ANNOTATES]->(e) " % tag_id1
        req += "match (e)<-[:ANNOTATES]-(a2: annotation)-[:REFERS_TO]->(t2: tag {tag_id: %d}) " % tag_id2
        req += "match (e)<-[:AUTHORSHIP]-(u: user) "
        req += "where e.timestamp >= %d and e.timestamp <= %d " % (start_date, end_date)
        req += "return distinct t1.tag_id, CASE e.post_id when null then e.comment_id else e.post_id end as id, CASE e.post_id when null then 'comment' else 'post' end as entity_type, e.timestamp as timestamp, e.label as label, u.user_id as user_id, u.label as user_label, t2.tag_id ORDER BY e.timestamp DESC"
        result = neo4j.query_neo4j(req)

        tags = []
        for record in result:
            tags.append({'id': record['id'], "entity_type": record['entity_type'], "timestamp": record['timestamp'], 'label': record['label'], 'user_id': record['user_id'], 'user_label': record['user_label']}) 
        try:
            return makeResponse(tags,200)
        except ResultError:
            return makeResponse("ERROR",500)

