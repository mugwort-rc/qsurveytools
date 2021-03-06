title: アンケートソース

# アンケートソース

![source.png](img/source.png)

最初の行はアンケート設定で定義した**[ID]**列と同じ値が必要になります。

**注：値が一致しない列は集計時に無視されます。**

2行目は入力補助目的で設問名等が入力できます。
必要ない場合は何も入力せずそのままにしておいてください。

**注：2行目を消すと2行目に位置するレコードが読み飛ばされます。**

3行目以降はアンケートの入力欄になります。

**注：ID列に値が入力されていない行は集計時に除外されます。（無効票を除外する際などに使用します。）**

## 単数回答 { #single }

選択肢に対応させた番号を入力してください。

**注意**：
選択肢は`1`から始まります。

不正な値が入力された場合、集計時にその値を選択肢として追加します。

不正な値の例：

* 複数回答形式で入力した
* 全角数字
* 数以外の文字が含まれる（例：`.`や`,`など）

## 複数回答 { #multiple }

選択肢に対応させた番号を`,`で区切って入力してください。

**注意**：
選択肢は`1`から始まります。

不正な値が入力された場合、集計時にその値を選択肢として追加します。

不正な値の例：

* 全角数字
* 全角記号
* 数以外の文字が含まれる（例：`.`など）

### 複数回答変換

#### 複数列→`,`区切り変換

アンケート調査会社等に調査を依頼した場合、複数回答欄が各列に展開されたもので返ってくることがあります。

列方向に展開された複数回答を`,`区切りの形式に変換するツールがあります。

使い方：

1. `便利ツール/②複数回答入力形式変換ツール.exe`を起動します。
2. 処理したいExcelファイルを開き、複数回答の列を選択します。
3. ツールの「作成」ボタンを押します。
4. 自動的にクリップボードに内容がコピーされます。

注意：

このツールは、範囲指定したセルの一番左を`1`として`,`区切りのテキストを生成します。

入力の有無で判定していますので、未回答を`0`埋め等している場合は、事前に置換してセルを空にしておく必要があります。

#### `,`区切り→複数列変換

集計結果を検証する際、`,`区切りでは不便なため、複数回答を複数列変換する機能があります。

アンケート集計ツールに入力ファイルを設定した状態で、「設定/展開出力」タブの「[複数回答を展開する]」ボタンを押すと複数回答を列方向に展開したファイルを生成します。


[ID]: settings.html#id
[複数回答を展開する]: aggregation.html#expand_multiple_answer
