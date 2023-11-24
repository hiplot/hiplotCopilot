import pika
import json

from common.print_color import print_green

# RabbitMQ 服务器的连接参数
rabbitmq_credentials = pika.PlainCredentials(username='lxs', password='root')
rabbitmq_parameters = pika.ConnectionParameters(host='127.0.0.1', credentials=rabbitmq_credentials)
connection = pika.BlockingConnection(rabbitmq_parameters)
channel = connection.channel()
queue_name = 'common'


def send_task(task_id: str, module_name: str, plugin_name: str):
    channel.queue_declare(queue=queue_name, durable=True)
    prefix = "/home/lxs/code/ospp/user"
    input_prefix = f"{prefix}/input/{task_id}"
    output_prefix = f"{prefix}/output/{task_id}"
    message = {
        "inputFile": f"{input_prefix}/data.txt",
        "confFile": f"{input_prefix}/data.json",
        "outputFilePrefix": output_prefix,
        "module": module_name,
        "tool": plugin_name,
        "ID": task_id,
        "Name": "common"
    }
    message_json = json.dumps(message)
    channel.basic_publish(exchange="", routing_key=queue_name, body=message_json.encode(encoding="utf-8"))
    connection.close()
    print_green(f"任务{task_id}已提交")
