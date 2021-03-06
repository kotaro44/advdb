from flask import Flask, jsonify, abort, make_response, request
from flask.ext.restful import  Resource, reqparse, fields, marshal, marshal_with
from database import graphene, data_types
from py2neo import Node, Relationship

graph = graphene.get_database()

class Movies(Resource):

    def __init__(self):
      super(Movies, self).__init__()
        
    @marshal_with(data_types.movie_list)
    def get(self):
    
        movies = graph.find('Movie', property_key=None,
                               property_value=None, limit= 200)
        movies_object = []
        for movie in movies:
            movies_object.append(movie.properties)
        return {'movies' : movies_object}

