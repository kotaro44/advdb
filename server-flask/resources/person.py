from flask import Flask, jsonify, abort, make_response, request
from flask.ext.restful import Resource, reqparse, fields, marshal, marshal_with
from database import graphene, data_types
from collections import namedtuple
from py2neo import Node, Relationship

graph = graphene.get_database()
cypher = graph.cypher

class Person(Resource):

    def __init__(self):
        #Request parser to get the params in a sexy way
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('person_id', type=str, location='json')
        self.reqparse.add_argument('email', type=str, required=True,
                                   location='json')
        self.reqparse.add_argument('name', type=str, location='json',
                                   required=True)
        self.reqparse.add_argument('gender', type=str, location='json')
        self.reqparse.add_argument('age', type=int, location='json')
        self.reqparse.add_argument('interested_in', type=str,
                                   location='json')
        self.reqparse.add_argument('height', type=int, location='json',
                                   default=160)
        self.reqparse.add_argument('likes')
        super(Person, self).__init__()

    @marshal_with(data_types.user_fields)
    def get(self, id):
        user = graph.find_one('Person', property_key='person_id',
                              property_value=id)
        if not user:
            return ({"error": "user does not exist"})

        u = user.properties
        u['likes'] = []
        u['likes'].append({'movies_liked' : self.get_liked_movies(id), 'tvshows_liked': self.get_liked_tvshows(id)})

        return u

    def put(self, id):
        args = self.reqparse.parse_args()
        user = graph.find_one('Person', property_key='person_id',
                              property_value=id)
        if user:
            user.properties['person_id']=id
            user.properties['email']=args['email']
            user.properties['name']=args['name']
            user.properties['gender']=args['gender']
            user.properties['age']=args['age']
            user.properties['interested_in']=args['interested_in']
            user.properties['height']=args['height']
            user.properties['likes'] = user.properties['likes']
            user.push()
            return ({"Put": user.properties})
        else:
            newPerson = Node(
                'Person',
                person_id=id,
                email=args['email'],
                name=args['name'],
                gender=args['gender'],
                age=args['age'],
                interested_in=args['interested_in'],
                height=args['height'],
                )

            try:
                graph.create(newPerson)
                return ({'Put': newPerson.properties}, 200)
            except:
                return ({'error': 'User was not created'}, 200)

    def post(self, id):
        args = self.reqparse.parse_args()
        user = graph.find_one('Person', property_key='person_id',
                              property_value= id)
        if user:
            return user.properties
        else:
            newPerson = Node(
                'Person',
                person_id=id,
                email=args['email'],
                name=args['name'],
                gender=args['gender'],
                age=args['age'],
                interested_in=args['interested_in'],
                height=args['height'],
                likes=args['likes'],
                )

            graph.create(newPerson)
            return ({'created': newPerson.properties}, 200)


    def get_liked_movies (self, personid):
        watched_movies= cypher.execute("MATCH (a:Person{person_id: {A}}),(m:Movie) MATCH (a)-[:WATCHED]-(m) return m", A=personid)
        subgraph_person = watched_movies.to_subgraph()
        nodelist = []
        for node in subgraph_person.nodes:
            nodelist.append(node.properties['movie_id'])
        return nodelist

    def get_liked_tvshows(self, personid):
        watched_shows= cypher.execute("MATCH (a:Person{person_id: {A}}),(m:TV_Show) MATCH (a)-[:WATCHED]-(m) return m", A=personid)
        subgraph_person = watched_shows.to_subgraph()
        nodelist = []
        for node in subgraph_person.nodes:
            nodelist.append(node.properties['tvshow_id'])
        return nodelist



    def delete(self, id):
        pass
