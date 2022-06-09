import torch
from torch import nn
from torchmetrics import MetricCollection, Accuracy, Precision, Recall
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup,BertForSequenceClassification
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
import tokenizer_bert
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--fold', type=str)
parser.add_argument('--cuda_id', type=str)
parser.add_argument('--lr', type=str)
args = parser.parse_args()

#時刻の取得
import datetime
import os

dt_now = tokenizer_bert.dt_now

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
print('***level1***')

device = torch.device("cuda:"+args.cuda_id)#if torch.cuda.is_available() else "cpu"

dataloader_train_l1 = tokenizer_bert.dataloader_train_l1
#dataloader_val_l1 = tokenizer_bert.dataloader_val_l1
dataloader_test_l1= tokenizer_bert.dataloader_test_l1

class BertForSequenceClassification_pl(pl.LightningModule):
        
    def __init__(self, model_name, num_labels, lr):
        # model_name: Transformersのモデルの名前
        # num_labels: ラベルの数
        # lr: 学習率

        super().__init__()
        
        # 引数のnum_labelsとlrを保存。
        # 例えば、self.hparams.lrでlrにアクセスできる。
        # チェックポイント作成時にも自動で保存される。
        self.save_hyperparameters()
        
        self.criterion = nn.CrossEntropyLoss()
        
        # BERTのロード
        self.bert_sc = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )
        self.bert_sc = self.bert_sc.cuda(int(args.cuda_id))
        
        
    # 学習データのミニバッチ(`batch`)が与えられた時に損失を出力する関数を書く。
    # batch_idxはミニバッチの番号であるが今回は使わない。
    def training_step(self, batch, batch_idx):
        output = self.bert_sc(**batch)
        train_loss = output.loss
        
        labels = batch.pop('labels') # バッチからラベルを取得
        labels_predicted = output.logits.argmax(-1)
        num_correct = ( labels_predicted == labels ).sum().item()
        accuracy= num_correct/labels.size(0) #精度
       
        performance = {'loss':train_loss,
                'batch_preds': labels_predicted,
                'batch_labels': labels}
        
        return performance
    
    def training_epoch_end(self,outputs,mode="train"):
        # batch毎のlossの平均を計算
        loss = torch.tensor([x['loss'] for x in outputs])
        epoch_loss = torch.div(loss.sum(),torch.tensor(loss.size()))
        self.log(f"{mode}_loss", epoch_loss, logger=True)

        # accuracy計算
        epoch_preds = torch.cat([x['batch_preds'] for x in outputs])
        epoch_labels = torch.cat([x['batch_labels'] for x in outputs])
        num_correct = (epoch_preds == epoch_labels).sum().item()
        epoch_accuracy = num_correct / len(epoch_labels)
        self.log(f"{mode}_accuracy", epoch_accuracy, logger=True,prog_bar = True)
        
        metric_collection = MetricCollection([
            Accuracy(),
            Precision(num_classes=6, average='macro'),
            Recall(num_classes=6, average='macro')
        ]).cuda(int(args.cuda_id))#.type_as(batch)
        metric = metric_collection(epoch_preds, epoch_labels)
        self.log_dict(metric) # Accuracy,Precision,Recallのログをとる。
    
    # 検証データのミニバッチが与えられた時に、
    # 検証データを評価する指標を計算する関数を書く。
    def validation_step(self, batch, batch_idx):
        output = self.bert_sc(**batch)
        val_loss = output.loss
        self.log('val_loss', val_loss) # 損失を'val_loss'の名前でログをとる。
        
        labels = batch.pop('labels') # バッチからラベルを取得
        labels_predicted = output.logits.argmax(-1)
        num_correct = ( labels_predicted == labels ).sum().item()
        accuracy= num_correct/labels.size(0) #精度
        self.log('val_accuracy', accuracy) # 精度を'val_accuracy'の名前でログをとる。
    
    # テストデータのミニバッチが与えられた時に、
    # テストデータを評価する指標を計算する関数を書く。
    def test_step(self, batch, batch_idx):
        output = self.bert_sc(**batch)
        test_loss = output.loss
        
        labels = batch.pop('labels') # バッチからラベルを取得
        labels_predicted = output.logits.argmax(-1)
        performance = {'loss':test_loss,
                'batch_preds': labels_predicted,
                'batch_labels': labels}
        
        return performance
        
        
    def test_epoch_end(self, outputs):
        return self.training_epoch_end(outputs, "test")
        
    
    # 学習に用いるオプティマイザを返す関数を書く。
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.lr)

"""
# EarlyStoppingの設定
# 1epochで'val_loss'が0.05以上減少しなければ学習をストップ
early_stop_callbacks = EarlyStopping(
    monitor='train_loss', 
    min_delta=0.05, 
    patience=1, 
    mode='min')       
"""
# PyTorch Lightningモデルのロード
model = BertForSequenceClassification_pl(
    MODEL_NAME, num_labels=6, lr=float(args.lr)
)

"""
レベル1：ARG or nonARG
"""
# 学習時にモデルの重みを保存する条件を指定
checkpoint_l1 = pl.callbacks.ModelCheckpoint(
    monitor='train_loss',
    mode='min',
    save_top_k=1,
    save_weights_only=True,
    dirpath='model_l1/',
)

# 学習の方法を指定
trainer_l1 = pl.Trainer(
    #early_stop_callback=True,
    gpus=1,
    max_epochs=6,
    callbacks = [checkpoint_l1]
)

# ファインチューニングを行う。
trainer_l1.fit(model, train_dataloaders = dataloader_train_l1)

best_model_path = checkpoint_l1.best_model_path # ベストモデルのファイル
print('l1ベストモデルのファイル: ', checkpoint_l1.best_model_path)
print('l1ベストモデルの検証データに対する損失: ', checkpoint_l1.best_model_score)

test = trainer_l1.test(dataloaders=dataloader_test_l1)
print('Level1: ',test)

# PyTorch Lightningモデルのロード
model_l1 = BertForSequenceClassification_pl.load_from_checkpoint(
    best_model_path
) 

# Transformers対応のモデルを./model_transformesに保存
model_l1.bert_sc.save_pretrained('./model_transformers_l1' )

print("***level1:finish***")