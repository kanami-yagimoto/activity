# activity
柳本香菜美が今まで実装したプログラム
## バイオインフォマティクス特論
学部４年前期に受講した早稲田大学大学院先進理工学研究科の授業「バイオインフォマティクス特論」内の課題として実装したプログラム
※Pythonで実装
### 第４回　Needleman-Wunschアルゴリズムによる大域アラインメント計算プログラム
- bioinfo_4.py:入力配列`seq_x`,`seq_y`の最適アラインメントとそのスコアを計算する`alignment`関数
- bioinfo_4_1.py：`seq_file.txt`に記載されている配列のアラインメントをbioinfo_4.pyに計算させ出力
- bioinfo_4_2.py:長さnの配列を2本自動生成したのち`alignment`関数にペアワイズアラインメントを実行させ，その実行時間を計測
### 第5回　Smith-Watermanアルゴリズムによる局所アラインメント計算プログラム
- bioinfo_5.py：テキストファイルに記述されている配列を読み込む`file_open`関数，局所アラインメントを計算する`local_alignment`関数，大域アラインメントを計算する`global_alignment`関数(bioinfo_4.pyの`alignment`関数と同じ内容)
- bioinfo_5_2.py：コマンドライン引数なしで大域アラインメントを，`-local`のオプションありで局所アラインメントを実行
### 第８~11回：普通のサイコロと6の出力確率のみ大きいサイコロについての隠れマルコフモデル(HMM)
以下のアルゴリズムで最適パス(最大の確率で出力する状態遷移)，同時確率(最適パスが出力される確率)を算出する
- bioinfo_8.py:viterbiアルゴリズム
- bioinfo_9_fwd.py:forwardアルゴリズム
- bioinfo_10_bkw.py:backwardアルゴリズム

- bioinfo_11.py：事後デコーディング(各位置で事後状態確率が最も高い状態を選択する方法)とviterbiアルゴリズムの精度比較
- bioinfo_12.py:Baum-Welchアルゴリズムでパラメタを推定した後にbioinfo_11.pyと同様の操作を行う
 
## 研究活動
自然言語処理モデルBERTにタンパク質で事前学習させたモデル([ProtBert-BFD](https://huggingface.co/Rostlab/prot_bert_bfd)に分類器(BERTの文章分類ライブラリ[BertForSequenceClassification](https://huggingface.co/docs/transformers/model_doc/bert#transformers.BertForSequenceClassification)を接続させ，抗生物質耐性の原因となるタンパク質でファインチューニングしたモデル
※Pythonで実装
- tokenizer_bert.py:入力配列をトークン化
- level0.py:入力タンパク質が耐性を持つor持たないの２クラス分類
- level1.py:耐性を与えるタンパク質について，そのメカニズムを６クラス分類

## シューティングゲーム開発
学部１年次で受講したJavaの必修授業では，５人のグループでシューティングゲームを作成した．このゲームのルールは画面上部から玉が落ちてきて，玉が画面下部の的を通ったタイミングに合わせてマウスで的をクリックする．そしてクリックのタイミングが合えば音がなり点数が入るというものだ．このゲーム作成の中で，私は玉を描画し玉が上から的まで動く部分を担当した．玉を動かすスピードはゲームのレベルに合わせて４種類設定した．
※Javaで実装
- 後ほどプログラムをアップロードします
