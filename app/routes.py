import os
import pandas as pd
from flask import request, jsonify, render_template
from app import app
from dowhy import CausalModel

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_path = ''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    global file_path
    file = request.files['file']
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return jsonify({'columns': columns})


@app.route('/analyze', methods=['POST'])
def analyze():
    # file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    # if not file_list:
    #     return jsonify({'error': 'No files uploaded'}), 400
    # file = file_list[1]
    # file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    df = pd.read_csv(file_path)
    print(df)
    treatment = request.json['treatment']
    outcome = request.json['outcome']
    common_causes = request.json.get('common_causes', [])
    print(treatment)
    print(outcome)
    print(common_causes)
    print(df)
    # 只对数值列进行均值填充
    df.fillna(df.select_dtypes(include='number').mean(), inplace=True)

    if df.empty:
        return jsonify({'error': 'Data is empty after preprocessing'}), 400

    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=common_causes
    )

    # 标识因果估计量
    identified_estimand = model.identify_effect()

    # 使用线性回归进行因果效应估计
    estimate = model.estimate_effect(identified_estimand,
                                     method_name="backdoor.linear_regression")

    effect = estimate.value
    response = {}

    effect = estimate.value
    response = {}

    if effect is not None:
        if abs(effect) > 0.01:
            response[
                'message'] = f"在控制了混杂变量(可选的)后，{treatment}对{outcome}的平均因果效应为{effect:.2f}。这意味着在其他条件相同的情况下，{treatment}每增加一个单位，{outcome}平均增加{effect:.2f}个单位。"
        else:
            response['message'] = "没有检测到影响。"
    else:
        response['message'] = "无法计算因果效应。"

    return jsonify(response)


