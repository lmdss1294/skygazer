from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
from pymongo import MongoClient
import time
from datetime import datetime, timedelta
import pickle
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import RandomizedSearchCV


username = "lmdss1294"
password = "13519618"
cluster_url = "cluster0.jktknik.mongodb.net"
database_name = "cluster0"
collection_name = "your_collection_name"
# MongoClient를 사용하여 연결
client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority")
db = client[database_name]
collection = db[collection_name]



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        departure_time = request.form.get('time')
        input_datetime = datetime.strptime(departure_time, '%Y-%m-%dT%H:%M')
        previous_datetime = input_datetime.replace(minute=0)
        next_datetime = previous_datetime + timedelta(hours=1)

        previous_data = collection.find_one({"Datetime": previous_datetime})
        next_data = collection.find_one({"Datetime": next_datetime})
        # 선형 보간 비율 계산
        total_seconds = (next_datetime - previous_datetime).total_seconds()
        time_diff = (input_datetime - previous_datetime).total_seconds()
        interpolation_ratio = time_diff / total_seconds

        # 선형 보간하여 값을 계산
        interpolated_data = {}
        for key in previous_data:
            if key == "_id" or key == "Datetime":
                interpolated_data[key] = previous_data[key]
            else:
                interpolated_data[key] = previous_data[key] + (next_data[key] - previous_data[key]) * interpolation_ratio

        # 결과 출력
        L = [
            interpolated_data['풍향(deg)'],
            interpolated_data['풍속(KT)'],
            interpolated_data['시정'],
            interpolated_data['기온(°C)'],
            interpolated_data['강수량(mm)'],
            interpolated_data['적설량(mm)'] / 10  # mm를 cm로 변환
        ]


        # 모델 파일 로드
        with open("random_search (1).pkl", "rb") as file:
            model = pickle.load(file)

        y = model.predict([L])























        new_time = y[0]
        return render_template('result.html',new_time=new_time)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)