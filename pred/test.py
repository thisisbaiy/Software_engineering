from datetime import datetime


def convert_date_range(date_range):
    start_date_str, end_date_str = date_range.split(' to ')

    start_date = datetime.strptime(start_date_str, '%Y年%m月%d日')
    end_date = datetime.strptime(end_date_str, '%Y年%m月%d日')

    start_date_formatted = start_date.strftime('%Y-%m-%d')
    end_date_formatted = end_date.strftime('%Y-%m-%d')

    return start_date_formatted, end_date_formatted


date_range = "2022年01月10日 to 2022年01月12日"
start_date, end_date = convert_date_range(date_range)
print("Start Date:", start_date)
print("End Date:", end_date)
