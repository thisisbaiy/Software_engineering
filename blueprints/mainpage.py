# @Author  : baiyu
# @Time    : 2023/5/19 22:41
# @File    : mainpage.py
# @Description
import csv
import datetime

from flask import Blueprint, render_template, request

bp = Blueprint("mainpage", __name__, url_prefix="/mainpage")


@bp.route("/index", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


# 读取csv文件某几列并以字典方式存储
def read_csv_data(filename, columns):
    #    columns = ['DATATIME', 'ROUND(A.POWER,0)', 'YD15']
    data = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for column in columns:
                if column in row:
                    if column not in data:
                        data[column] = []
                    data[column].append(row[column])
    return data


def filter_rows_by_date_range(filename, start_date, end_date):
    filtered_rows = []
    start_date = datetime.datetime.strptime(start_date, '%Y年%m月%d日')
    end_date = datetime.datetime.strptime(end_date, '%Y年%m月%d日')

    start_date_formatted = start_date.strftime('%Y-%m-%d')
    end_date_formatted = end_date.strftime('%Y-%m-%d')
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        count = 1
        next(reader)
        for row in reader:
            if len(row) >= 2:  # 确保行中至少有两个元素（日期和时间）
                datatime_str = row[1]
                datatime = datetime.datetime.strptime(datatime_str, '%Y-%m-%d %H:%M:%S')
                if start_date <= datatime <= end_date:
                    filtered_rows.append(row)
    return filtered_rows


def convert_date_range(date_range):
    start_date_str, end_date_str = date_range.split(' to ')
    return start_date_str, end_date_str


@bp.route("/changedata", methods=['GET', 'POST'])
def changedata():
    # 获取相关的三个参数
    wf = request.args.get("WF")
    province = request.args.get("province")
    timerage = request.args.get("timerage")  # 2022年01月10日 to 2022年01月12日
    start_date, end_date = convert_date_range(timerage)
    # 读取数据
    filename = 'pred\\0002out.csv'
    filtered_data = filter_rows_by_date_range(filename, start_date, end_date)
    ROUND_POWER_list = [item[2] for item in filtered_data]
    YD15_list = [item[3] for item in filtered_data]

    return {'ROUND_data': ROUND_POWER_list,
            'YD_data': YD15_list
         }
