import json

# 定义一个字典，值是列表
data = {
    "name": "John",
    "age": 30,
    "city": "New York",
    "hobbies": [1, 2, 3]
}

# 将字典转化为 JSON 格式
json_data = json.dumps(data)

# 打印转化后的 JSON 数据
print(json_data)
