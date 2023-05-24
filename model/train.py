import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import datetime
import paddlets
from paddlets import TSDataset
from paddlets import TimeSeries
from paddlets.models.forecasting import MLPRegressor, LSTNetRegressor
from paddlets.transform import Fill, StandardScaler
from paddlets.metrics import MSE, MAE
from paddlets.analysis import AnalysisReport, Summary
from paddlets.datasets.repository import get_dataset
import warnings
warnings.filterwarnings('ignore')


def data_preprocess(data_dir):
    files = os.listdir(data_dir)
    # 第一步，完成数据格式统一
    for f in files:
        # 获取文件路径
        data_file = os.path.join(data_dir, f)
        # 获取文件名后缀
        data_type = os.path.splitext(data_file)[-1]
        # 获取文件名前缀
        data_name = os.path.splitext(data_file)[0]
        # 如果是excel文件，进行转换
        if data_type == '.xlsx':
            # 需要特别注意的是，在读取excel文件时要指定空值的显示方式，否则会在保存时以字符“.”代替，影响后续的数据分析
            data_xls = pd.read_excel(data_file, index_col=0, na_values='')
            data_xls.to_csv(data_name + '.csv', encoding='utf-8')
            # 顺便删除原文件
            os.remove(data_file)
    # 第二步，完成多文件的合并，文件目录要重新更新一次
    files = os.listdir(data_dir)
    for f in files:
        # 获取文件路径
        data_file = os.path.join(data_dir, f)
        # 获取文件名前缀
        data_basename = os.path.basename(data_file)
        # 检查风机数据是否有多个数据文件
        if len(data_basename.split('-')) > 1:
            merge_list = []
            # 找出该风机的所有数据文件
            matches = [ f for f in files if (f.find(data_basename.split('-')[0] + '-') > -1)]
            for i in matches:
                # 读取风机这部分数据
                data_df = pd.read_csv(os.path.join(data_dir, i), index_col=False, keep_default_na=False)
                merge_list.append(data_df)
            if len(merge_list) > 0:
                all_data = pd.concat(merge_list,axis=0,ignore_index=True).fillna(".")
                all_data.to_csv(os.path.join(data_dir, data_basename.split('-')[0]+ '.csv'),index=False)
            for i in matches:
                # 删除这部分数据文件
                os.remove(os.path.join(data_dir, i))
            # 更新文件目录
            files = os.listdir(data_dir)


data_preprocess('功率预测竞赛赛题与数据集')

df = pd.read_csv('功率预测竞赛赛题与数据集/02.csv',parse_dates=['DATATIME'],infer_datetime_format=True,dayfirst=True,dtype={'WINDDIRECTION':np.float64, 'HUMIDITY':np.float64, 'PRESSURE':np.float64})
df.drop_duplicates(subset = ['DATATIME'],keep='first',inplace=True)

target_cov_dataset = TSDataset.load_from_dataframe(
    df,
    time_col='DATATIME',
    target_cols=['ROUND(A.POWER,0)', 'YD15'],
    observed_cov_cols=['WINDSPEED', 'PREPOWER', 'WINDDIRECTION', 'TEMPERATURE',
       'HUMIDITY', 'PRESSURE', 'ROUND(A.WS,1)'],
    freq='15min',
    fill_missing_dates=True,
    fillna_method = 'pre'
)
_ , train_dataset = target_cov_dataset.split('2021-04-30 04:45:00')
train_dataset, val_test_dataset = train_dataset.split('2021-07-31 04:45:00')
val_dataset, test_dataset = val_test_dataset.split('2021-08-31 04:45:00')
# 最后一天的工况数据需要预测ROUND(A.POWER,0)和YD15两个字段，而且输入数据只到前一天的早上5点
test_dataset, pred_dataset = test_dataset.split('2021-09-30 04:45:00')

scaler = StandardScaler()
scaler.fit(train_dataset)

train_dataset_scaled = scaler.transform(train_dataset)
val_test_dataset_scaled = scaler.transform(val_test_dataset)
val_dataset_scaled = scaler.transform(val_dataset)
test_dataset_scaled = scaler.transform(test_dataset)

lstm = LSTNetRegressor(
    in_chunk_len = (24 + 19) * 7 * 4,
    out_chunk_len = (24 + 19) * 4,
    max_epochs=10,
    optimizer_params= dict(learning_rate=5e-3),
)
def train():
    lstm.fit(train_dataset_scaled, val_dataset_scaled)
    lstm.save("./model", network_model=True, dygraph_to_static=True)
if __name__ == '__main__':
    train()