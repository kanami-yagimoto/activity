import random
import torch
from torch import nn
from torch.utils.data import DataLoader
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup,BertForSequenceClassification
#import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--fold', type=str)
parser.add_argument('--cuda_id', type=str)
parser.add_argument('--lr', type=str)
args = parser.parse_args()

#時刻の取得
import datetime
import os

dt_now = datetime.datetime.now()
dir_name = './result/'+str(dt_now)
os.makedirs(dir_name ,exist_ok=True)

#logging
import logging
import transformers
transformers.logging.set_verbosity_info()

logger = logging.getLogger(__name__)
logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO)

# 事前学習モデル
MODEL_NAME = 'prot_bert_bfd'
print('model')

# カテゴリーのリスト
l0_dict = {'arg' : 0,'nonarg' : 1}
l1_dict = {
    'antibiotic target alteration' : 0,
    'antibiotic target replacement':1,
    'antibiotic target protection':2,
    'antibiotic inactivation':3,
    'antibiotic efflux':4,
    'others':5,
}

# トークナイザのロード
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME,do_lower_case=False)
print('tokenize')

# 各データの形式を整える
max_length = 1576

device = torch.device("cuda:"+args.cuda_id ) #if torch.cuda.is_available() else "cpu"

def read_input_l1(input_file):

    n = -1
    dataset_for_loader = []
    data = [] 

    with open(input_file) as f:
        for seq in f.readlines():
            if seq.startswith('>') == 1:
                # 前の配列をトークン化する
                seq = seq.replace('>', '')
                id_list = seq.split('|')
                data.append({})
                n += 1
                data[n]['seq'] = ''
                if (id_list[5] == 'reduced permeability to antibiotic') or (id_list[5] == 'resistance by absence'):
                    data[n]['label'] = l1_dict['others']
                else:
                    data[n]['label'] = l1_dict[id_list[5]]

            else:
                seq = seq.replace('\n','').replace('',' ').lstrip(' ')
                data[n]['seq'] += seq        
    print('l1_length:',n+1)  

    for n in range(n+1):
        encoding = tokenizer(
                                    data[n]['seq'],
                                    max_length=max_length,  
                                    padding='max_length',
                                    truncation=True
                                      )
        encoding['labels'] = data[n]['label'] # ラベルを追加
        encoding = { k: torch.tensor(v, device=device) for k, v in encoding.items()}
        #encoding.to(device)
        dataset_for_loader.append(encoding) 
        
        
    return dataset_for_loader

def read_input_l0(input_file):

    n = -1
    dataset_for_loader = []
    data = [] 

    with open(input_file) as f:
        for seq in f.readlines():
            if seq.startswith('>') == 1:
                n += 1
                # 前の配列をトークン化する
                seq = seq.replace('>', '')
                id_list = seq.split('|')
                data.append({})
                data[n]['seq'] = ''
                if id_list[0] == 'sp':
                    data[n]['label'] = l0_dict['nonarg']
                else:
                    data[n]['label'] = l0_dict['arg']
            else:
                   data[n]['seq'] += seq  
                
    print('l0_length:',n+1)  

    for n in range(n+1):
        encoding = tokenizer(
                                    data[n]['seq'],
                                    max_length=max_length,  
                                    padding='max_length',
                                    truncation=True
                                      )
        encoding['labels'] = data[n]['label'] # ラベルを追加
        encoding = { k: torch.tensor(v, device=device) for k, v in encoding.items()}
        dataset_for_loader.append(encoding)
    return dataset_for_loader

dataset_train_l0 = read_input_l0('./5_fold_data/level_0/fold_'+ args.fold +'_train.fasta')
dataset_train_l1 = read_input_l1('./5_fold_data/level_1/fold_'+ args.fold +'_train.fasta')
#dataset_train = dataset_train_arg + dataset_train_nonarg

dataset_test_l0 = read_input_l0('./5_fold_data/level_0/fold_'+ args.fold +'_test.fasta')
dataset_test_l1 = read_input_l1('./5_fold_data/level_1/fold_'+ args.fold +'_test.fasta')

# データセットからデータローダを作成
# 学習データはshuffle=Trueにする。
dataloader_train_l0 = DataLoader(
    dataset_train_l0, batch_size=8, shuffle=True
) 
dataloader_train_l1 = DataLoader(
    dataset_train_l1, batch_size=8, shuffle=True
) 
#dataloader_val = DataLoader(dataset_val, batch_size=1)
dataloader_test_l0 = DataLoader(dataset_test_l0, batch_size=8,shuffle=True)
dataloader_test_l1 = DataLoader(dataset_test_l1, batch_size=8,shuffle=True)

print('tokenize:finish')