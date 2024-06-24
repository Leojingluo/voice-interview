from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import requests
import os
import tempfile

app = Flask(__name__)
CORS(app)

# 初始化 Hugging Face Transformers 的问答和总结模型
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

# 配置百度语音识别 API
BAIDU_APP_ID = '79204115'
BAIDU_API_KEY = 'IreBrZoLgSbGoOF5VdAbuZKJ'
BAIDU_SECRET_KEY = 'IPUmNDbfARMCGqT56LjEjniLkwd1xKY9W'

def transcribe_audio(audio_path):
    token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={BAIDU_API_KEY}&client_secret={BAIDU_SECRET_KEY}"
    response = requests.post(token_url)
    access_token = response.json()['access_token']

    with open(audio_path, 'rb') as f:
        audio_data = f.read()

    url = f"https://vop.baidu.com/server_api?dev_pid=1537&cuid={BAIDU_APP_ID}&token={access_token}"
    headers = {'Content-Type': 'audio/wav; rate=16000'}
    response = requests.post(url, headers=headers, data=audio_data)
    result = response.json()

    if result['err_no'] == 0:
        return result['result'][0]
    else:
        return "Error in transcription"


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']
    context = data.get('context', '')
    print(data)
    if(context==""):
        context="一共34个，包括23个省（河北、山西、辽宁、吉林、黑龙江、江苏、浙江、安徽、福建、江西、山东、河南、湖北、湖南、广东、海南、四川、贵州、云南、陕西、甘肃、青海、台湾）、5个自治区（内蒙古、广西、西藏、宁夏、新疆）、4个直辖市（北京、天津、上海、重庆）、2个特别行政区（香港、澳门）。"
    result = qa_pipeline(question=question, context=context)
    print(result)
    answer = result['answer']
    return jsonify({'answer': answer})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    # 使用临时文件保存上传的音频
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        audio_path = temp_audio_file.name
        audio_file.save(audio_path)

    # 使用百度语音识别 API 进行语音识别
    text = transcribe_audio(audio_path)

    # 删除临时文件
    os.remove(audio_path)

    return jsonify({'text': text})

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    conversation = data['conversation']

    print(data)
    conversation_text = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in conversation])
    summary = summarization_pipeline(conversation_text, max_length=100000000, min_length=30, do_sample=False)
    summarized_text = summary[0]['summary_text']
    print(summarized_text)
    return jsonify({'summary': summarized_text})

if __name__ == '__main__':
    app.run(debug=True)