#导入需要的包
import os
import warnings
import numpy as np
import pandas as pd
from paddlets import TSDataset
from paddlets.models.model_loader import load
from paddlets.transform import StandardScaler
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

def forecast(df, turbine_id, out_file,starttime,endtime):
    test_dataset = TSDataset.load_from_dataframe(
        df,
        time_col='DATATIME',
        target_cols=['ROUND(A.POWER,0)', 'YD15'],
        observed_cov_cols=[
            'WINDSPEED', 'PREPOWER', 'WINDDIRECTION', 'TEMPERATURE',
            'HUMIDITY', 'PRESSURE', 'ROUND(A.WS,1)'
        ],
        freq='15min',
        fill_missing_dates=True,
        fillna_method='pre')
    _,test_dataset=test_dataset.split(starttime) #开始时间之后的数据
    test_dataset,_=test_dataset.split(endtime)#结束时间之前的数据
    scaler = StandardScaler()
    scaler.fit(test_dataset)
    test_dataset_scaled = scaler.transform(test_dataset)
    # 模型加载
    # loaded_ckpt = load("model/ckpt_{}".format(str(turbine_id)))
    loaded_ckpt = load("model/model")
    # 模型预测
    result = loaded_ckpt.predict(test_dataset)
    # 获取预测数据
    result = result.to_dataframe()[19 * 4:]
    result = result.reset_index()
    # 传入风场风机ID
    result['TurbID'] = turbine_id
    # 重新调整字段名称和顺序
    result.rename(columns={"index": "DATATIME"}, inplace=True)
    result = result[['TurbID', 'DATATIME', 'ROUND(A.POWER,0)', 'YD15']]
    result.to_csv(out_file, index=False)

if __name__=="__main__":
    #id变量为风场号，根据id会选择不同文件，如果没有该id对应的数据，则报错
    id=2
    #开始时间戳和结束时间戳，序列长度必须大于等于1204条
    starttime='2020-02-01 00:45:00'
    endtime='2020-02-19 01:45:00'
    datafile='infile/'+str(id).zfill(4)+'in.csv'
    assert os.path.exists(datafile),f'file{datafile} not exist' #判断文件是否存在，不存在则报错
    # files = os.listdir('infile')
    if not os.path.exists('pred'):
        os.mkdir('pred')
    out_file = os.path.join('pred', str(id).zfill(4)+ 'out.csv')
    df = pd.read_csv(datafile,
                    parse_dates=['DATATIME'],
                    infer_datetime_format=True,
                    dayfirst=True,
                    dtype={
                        'WINDDIRECTION': np.float64,
                        'HUMIDITY': np.float64,
                        'PRESSURE': np.float64
                    })
    # 因为数据批次不同，数据集中有一些时间戳重复的脏数据，送入paddlets前要进行处理，本赛题要求保留第一个数据
    df = df.drop_duplicates(subset=['DATATIME'], keep='first')
    # 获取风机号
    turbine_id = df.TurbID[0]
    df = df.drop(['TurbID'], axis=1)
    # 裁剪倒数第二天5:00前的数据输入时间序列
    tail = df.tail(4 * (19 + 24)).index
    df = df.drop(tail)

    forecast(df, turbine_id, out_file,starttime,endtime)
    print('finish {}'.format(datafile))