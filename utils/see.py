import argparse
import os
import pandas as pd
import json
import random
import subprocess
import pprint
import numpy as np

def fetch_file_from_hdfs(hdfs_path, local_path):
    """ 从 HDFS 拉取文件到本地目录 """
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    
    local_file_path = os.path.join(local_path, os.path.basename(hdfs_path))
    subprocess.run(['hdfs', 'dfs', '-get',  hdfs_path, local_file_path], check=True)
    
    return local_file_path

def get_file_extension(file_path):
    """ 获取文件扩展名 """
    return os.path.splitext(file_path)[1].lower()

def print_data_structure(data, indent=0):
    """递归打印数据结构的类型信息，以树形结构的方式显示，处理 numpy 数组"""
    indent_str = "\t" * indent  # 使用制表符来表示缩进
    
    if isinstance(data, dict):
        print(f"{indent_str}{{")
        for key, value in data.items():
            print(f"{indent_str}'{key}' : {type(value)}")
            print_data_structure(value, indent + 1)  # 递归打印字典的值
        print(f"{indent_str}}}")
    elif isinstance(data, list):
        print(f"{indent_str}Type: list")
        for index, item in enumerate(data):
            print(f"{indent_str}\tIndex: {index}, Type: {type(item)}")
            print_data_structure(item, indent + 1)  # 递归打印列表的每一项
    elif isinstance(data, np.ndarray):
        print(f"{indent_str}Type: numpy.ndarray, Shape: {data.shape}, Element type: {data.dtype}")
        # 处理大数组，进行截断显示
        print_data_structure(data[0], indent + 1)
        print(f"{indent_str}")  # 通过截断来避免打印过多元素
    else:
        pass

def print_file_lines(file_path, head_count, tail_count, random_count):
    """ 根据传入参数打印指定行数 """
    # 检测文件后缀并读取文件
    extension = get_file_extension(file_path)
    
    if extension == '.csv':
        df = pd.read_csv(file_path)
    elif extension == '.json':
        df = pd.read_json(file_path)
    elif extension == '.jsonl':
        df = pd.read_json(file_path, lines=True)
    elif extension == '.parquet':
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")
    
    # 打印文件总行数
    print(f"=========Total Lines==========")
    print(f"{len(df)}")

    # 打印数据结构信息
    print("==========File structure and types==========")
    print_data_structure(dict(df.iloc[0]))
    
    # 打印前几行
    if head_count > 0:
        print(f"==========Printing first {head_count} lines=================")
        for i in range(head_count):
            if i >= len(df):
                break
            pprint.pprint(dict(df.iloc[i]), width=120)
    
    # 打印后几行
    if tail_count > 0:
        print(f"==========Printing last {tail_count} lines=================")
        for i in range(len(df) - tail_count, len(df)):
            if i < 0:
                break
            pprint.pprint(dict(df.iloc[i]), width=120)
    
    # 打印随机几行
    if random_count > 0:
        print(f"==========Printing {random_count} random lines==========")
        random_indices = random.sample(range(len(df)), random_count)
        for i in random_indices:
            pprint.pprint(dict(df.iloc[i]), width=120)

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="Process a file from HDFS or local and display its lines.")
    parser.add_argument('file', help="Path to the file (HDFS or local).")
    parser.add_argument('-n', '--head', type=int, default=1, help="Number of lines to print from the head.")
    parser.add_argument('-t', '--tail', type=int, default=0, help="Number of lines to print from the tail.")
    parser.add_argument('-r', '--random', type=int, default=0, help="Number of random lines to print.")
    
    args = parser.parse_args()

    # 确定文件路径，如果是 HDFS 路径，则先拉取文件
    file_path = args.file
    # if file_path.startswith('hdfs://'):
    #     # 如果是 HDFS 路径，先下载到本地
    #     file_path = fetch_file_from_hdfs(file_path, './temp')
    
    # 打印文件内容
    print_file_lines(file_path, args.head, args.tail, args.random)

if __name__ == '__main__':
    main()
