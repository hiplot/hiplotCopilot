# hiplotCopilot

目前已支持简单的自动化数据预处理及hiplot文档问答功能，详细使用方法见`hipltoPreprocess.ipynb`和`hiplotDocQA.ipynb`

两项功能均依赖于openAI的chatGPT，需环境变量中配置密钥，可选择在`.env`文件中配置，示例如下，如有代理需额外配置访问地址

```
OPENAI_API_KEY = xxx
OPENAI_API_BASE = xxx
```

QA功能依赖于milvus向量数据库进行文本检索，可通过`docker-compose up -d`一键部署，部署完成后执行`make init_doc`将文档数据写入milvus
