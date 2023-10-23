from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load your data from the CSV file
data = pd.read_csv("server\processedData.csv", encoding='utf-8')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/analyze/<condition>", methods=["GET"])
def analyze(condition):
    try:
        top = data[data['condition'] == condition][['drugName', 'usefulness']].sort_values(by='usefulness', ascending=False)
        top = top.drop_duplicates(subset=['drugName']).head(10).reset_index(drop=True)
        return render_template('results.html', condition=condition, drugs=top.to_dict(orient='records'))
    except KeyError:
        return render_template('error.html', error_message='Condition not found')
@app.route("/analyze", methods=["POST"])
def recommended_medicines():
    condition = request.form.get("condition")
    if not condition:
        return render_template('error.html', error_message='Condition not provided')
    
    recommended_medicines_list = recommend_medicines_by_condition(condition, data, num_recommendations=10)
    if recommended_medicines_list == "No data available for this condition.":
        return render_template('error.html', error_message='Condition not found in data')
    
    return render_template('results.html', recommended_medicines=recommended_medicines_list)



def recommend_medicines_by_condition(condition, data, num_recommendations=5):
    condition_data = data[data['condition'] == condition]
    
    if condition_data.empty:
        return "No data available for this condition."
    
    avg_usefulness_by_drug = condition_data.groupby('drugName')['usefulness'].mean()
    recommended_medicines = avg_usefulness_by_drug.nlargest(num_recommendations).index.tolist()
    
    return recommended_medicines


if __name__ == "__main__":
    app.run(debug=True)
