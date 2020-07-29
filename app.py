#Gold Mastery Test.py

from flask import Flask, request
from flask_restful import Resource, Api

from sklearn import metrics

import pandas as pd
import sqlite3
import json

app = Flask(__name__)
api = Api(app)

class Submit(Resource):
    def post(self):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        
        data = request.get_json()
        name = data["name"]
        email = data["email"]
        x = data["x"]
        # print(x)

        x_df = pd.DataFrame(columns=['imei', 'pred'])
        
        
        imei = list(x.keys())
        pred = list(x.values())
        x_df['imei'] = imei
        x_df['pred'] = pred
        x_df['imei'] = x_df['imei'].astype('int64')
        x_df.index = x_df['imei']        
        x_df.drop('imei', axis=1, inplace=True)
        x_df

        y = pd.read_sql_query('SELECT * FROM answer', con=connection)
        y.index = y['imei']
        y['imei'] = y['imei'].astype('int64')
        y.drop('imei', axis=1, inplace=True)

        result = pd.concat([x_df, y], axis=1)
                
        score = metrics.accuracy_score(result['pred'], result['status'])
        
        query = "INSERT INTO Submissions (Name, Email, Score) VALUES (?, ?, ?)"
        cursor.execute(query, (name, email, score))
        connection.commit()
        connection.close()



        return {'message':f'Accuracy Score: {score * 100}%'}

class Scores(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = 'SELECT * FROM Submissions'

        results = pd.read_sql_query(query, con=connection)
        results = results.to_dict()

        connection.close()

        return {'message':results}

api.add_resource(Submit, '/submit')
api.add_resource(Scores, '/scores')


# app.run()