本项目需要安装的python库有：flask，flask_cors，transformers，tempfile。

本项目使用python的flask框架作为后端管理，并使用vue简单地实现前端页面。后台使用Hugging Face Transformers实现1个文本回答，使用tempfile生成百度语音到文本的音频文件。
在后端，主要通过Hugging Face Transformers根据用户提出的问题在前端页面生成相应的答案。
通过调用百度语音识别API接口，在前端将语音输入的音频文件转换为文本。



/ask
方法:POST
接受包含问题的JSON请求。
调用OpenAI的API并使用GPT模型生成答案。
返回包含生成的答案的JSON响应。
/transcribe:
方法:POST
接受包含音频文件的请求。
使用百度语音识别API将音频文件转换为文本。
返回包含转录文本的JSON响应。

/summarize：
方法：post
返回包含生成摘要的JSON响应。
