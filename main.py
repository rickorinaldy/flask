from flask import Flask, request, render_template, redirect, url_for
import requests
import json
import base64 
import pandas as pd

app = Flask(__name__)

def get_json(image):
    MODEL_ID = "39367c64-8c37-44e4-8fd2-e99b1aee4d3f"
    API_KEY = "ab29af47-dcca-11ed-9afe-7e9a2f3f8198"
    url = f'https://app.nanonets.com/api/v2/OCR/Model/{MODEL_ID}/LabelFile/'
    
    # Prepare the data for the request
    data = {'base64_data': image}
    response = requests.post(url, auth=requests.auth.HTTPBasicAuth(API_KEY, ''), data=data)
    dict_data = {"label":[], "text":[]}
    table_data = dict()
    data_json = json.loads(response.text)
    for data in data_json["result"][0]["prediction"]:
        if data["label"]=="table":
            for cell in data["cells"]:
                if cell["row"]==1:
                    table_data[cell["label"]] = []
                else: break   
    for data in data_json["result"][0]["prediction"]:
        if data["label"]=="table":
            row = 0
            for cell in data["cells"]:
                if row!=cell['row']:
                    row = cell['row']
                if len(table_data[cell["label"]])==row: continue
                table_data[cell["label"]].append(cell["text"])
        else:
            dict_data["label"].append(data["label"])
            dict_data["text"].append(data["ocr_text"])

    return table_data, dict_data

@app.route('/',  methods=['GET', 'POST'])
def index():
    return redirect(url_for('ijasah'))

@app.route('/ijasah')
def ijasah():
    return render_template('index.html', active_section='ijasah')

@app.route('/traskripnilai')
def traskripnilai():
    return render_template('iindex.html', active_section='traskripnilai')

@app.route('/extractindex/',methods=['POST'])  
def extractindex():
    if 'image' in request.files:
        image_data = request.files['image'].read()
        image_base64 = base64.b64encode(image_data)
        dict_data = dict()
        table_data = dict()
        table_data, dict_data = get_json(image_base64)
        
        df = pd.DataFrame(table_data)
        df2 = pd.DataFrame(dict_data)

        table_html1 = df2.to_html(classes='data', index=False)
        table_html2 = df.to_html(classes='data', index=False)
        
        return render_template('index.html', table1=table_html1, table2=table_html2, active_section='ijasah')
    else:
        return render_template('index.html', result_text=None, active_section='ijasah')

if __name__ == '__main__':
  app.run(port=5000)
