---
title: "測定値の中心とばらつき"
linkTitle: "測定値の中心とばらつき"
lesson: 1
weight: 1
duration: "20 min"
toc: true
summary: "5回の測定から平均と標準偏差を求め、値の意味を読む。"
prerequisites:
  - "Pythonでリストを作れる"
  - "ターミナルでPythonを実行できる"
objectives:
  - "測定値の平均を計算できる"
  - "標準偏差をばらつきの指標として説明できる"
  - "計算結果を単位付きで報告できる"
---

{{< goal >}}
同じ物体の長さを5回測ったデータから平均と標準偏差を計算し、
「代表値」と「測定のばらつき」を分けて読めるようになります。
{{< /goal >}}

[Lesson 1の完成コードを開く](/code/lesson-01.py)

## 1. 測定データを用意する

ある物体の長さを5回測り、次の値を得たとします。単位はcmです。

```python
measurements = [10.1, 9.9, 10.0, 10.2, 9.8]
```

{{< predict >}}
平均は `10.0 cm` より大きいでしょうか、小さいでしょうか、それとも同じでしょうか。
計算する前に、値の並びから予想してください。
{{< /predict >}}

## 2. 平均を計算する

Python標準ライブラリの `statistics.fmean` を使って平均を求めます。

```python
from statistics import fmean

mean = fmean(measurements)
print(f"mean: {mean:.2f} cm")
```

{{< expected-output >}}
mean: 10.00 cm
{{< /expected-output >}}

平均 $\bar{x}$ は、測定値 $x_i$ の合計を測定回数 $n$ で割った値です。

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i
$$

## 3. ばらつきを計算する

平均だけでは、各測定がどれくらい散らばっているかは分かりません。
ここでは標本標準偏差を計算します。

```python
from statistics import stdev

spread = stdev(measurements)
print(f"sample standard deviation: {spread:.3f} cm")
```

{{< expected-output >}}
sample standard deviation: 0.158 cm
{{< /expected-output >}}

標準偏差の単位は元の測定値と同じcmです。このデータでは、測定値が平均のまわりに
およそ `0.16 cm` のスケールで散らばっています。

## 4. 自分で変更する

{{< exercise >}}
最後の測定値を `9.8` から `9.0` に変更してください。

1. 平均がどう変わるか予想する
2. 標準偏差がどう変わるか予想する
3. コードを実行して確認する
{{< /exercise >}}

{{< hint >}}
`9.0` はほかの4つの値から大きく離れています。平均への影響と、ばらつきへの影響を
別々に考えてみましょう。
{{< /hint >}}

{{< solution >}}
データを `[10.1, 9.9, 10.0, 10.2, 9.0]` にすると、平均は `9.84 cm`、
標本標準偏差は約 `0.483 cm` です。平均は少し下がり、ばらつきは大きくなります。
{{< /solution >}}

## Check

- 平均と標準偏差を計算できた
- 2つの値がそれぞれ何を表すか説明できる
- 計算結果を単位付きで報告できた

次のLessonを作るときは、同じ構成を使って予想・実行・解釈・変更を一つずつ組み立てます。
