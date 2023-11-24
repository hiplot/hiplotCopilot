from langchain import PromptTemplate

# {sentence}
extract_params = PromptTemplate.from_template(
    """
    帮我从下面这句话中提取出image_description和filepath两个参数
    {sentence}
    你需要返回一个json对象
    """
)

# {json_data}
explain_title = PromptTemplate.from_template(
    """
    我有这样一份json数据，其中title为一个数组，表示数据的列标题，data为一个二维数组，其中每一个一维数组表示数据数据的一行，跟标题一一对应
    请你结合数据内容帮我解释每个标题可能代表的含义
    {json_data}
    你的回答需要是一个json对象，key表示标题抿成，value表示每个标题的含义
    """
)

# {description_json} {input_json}
select_params = PromptTemplate.from_template(
    """
    我有两份json数据，第一份为可供选择的变量名及其描述，第二份为需要输入的变量名及其描述，帮我从第一份数据中选择合适的值填充到第二份数据的每个对象中
    {description_json}
    {input_json}
    你的回答需要是一个json对象，key表示需要输入的变量名，value表示被选择用于输入的变量名
    """
)

# {image_type} {documents}
get_plugin_name = PromptTemplate.from_template(
    """
    根据下面的description，从documents中提取出于一个描述相符的插件
    description:
    {image_description}
    documents:
    {documents}
    你需要返回一个json对象
    """
)

