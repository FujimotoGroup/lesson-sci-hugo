---
title: "最初のハミルトニアン"
linkTitle: "最初のハミルトニアン"
lesson: 1
weight: 1
duration: "20 min"
toc: true
summary: "1サイト・s軌道の模型を作り、実空間行列とΓ点の固有値を読む。"
prerequisites:
  - "PythonでNumPy配列を作れる"
  - "リポジトリ直下で uv sync を実行済み"
objectives:
  - "TBModelを作る5段階の流れを実行できる"
  - "H_RとH(k)の違いを説明できる"
  - "Γ点の固有値を自分で確認できる"
---

{{< goal >}}
1サイト・1軌道だけの模型を構築し、オンサイトエネルギー `0.2` が
実空間ハミルトニアンとΓ点の固有値に現れるところまで確認します。
{{< /goal >}}

[Lesson 1の完成コードを開く](/code/lesson-01.py)

## 1. 最小の結晶を用意する

単純立方格子の原点にSiを1サイトだけ置き、そのサイトへs軌道を1本割り当てます。

```python
import numpy as np
import symham as sh

lattice = 2.0 * np.eye(3, dtype=float)
positions = np.array([[0.0, 0.0, 0.0]], dtype=float)
numbers = ["Si"]
orbitals = [sh.OrbitalRep.s()]
```

ここで `positions` はCartesian座標ではなく**分率座標**です。一方、後で `Hk` に渡す
k点はCartesian座標 `[1/Å]` です。

## 2. 対称性許容基底を作る

SymHamの基本処理は、モデル作成から基底計算までの5段階です。

```python
model = sh.TBModel(
    lattice,
    positions,
    numbers,
    orbitals,
    symprec=1e-6,
)

model.enumerate_bonds(
    r_cut=0.0,
    T_range=0,
    include_onsite=False,
)
model.classify_bonds_by_symmetry()
model.build_bond_orbit_basis()
```

`include_onsite=False` なので、今回は対称性パラメータ `e0` を生成しません。オンサイト値は
次の節でliteralな値として直接与えます。

{{< predict >}}
`r_cut=0.0`、`T_range=0`、`include_onsite=False` のとき、
`model.param_names` には何が入るでしょうか。実行する前に予想してください。
{{< /predict >}}

```python
print("param_names:", model.param_names)
```

{{< expected-output >}}
param_names: []
{{< /expected-output >}}

## 3. 実空間ハミルトニアンを作る

`atomic_onsite` は、対称性基底の係数ではなくliteralなオンサイトエネルギーを指定する入口です。

```python
H_R = model.real_space_hamiltonian(
    {},
    atomic_onsite={("Si", "s"): 0.2},
)

print("H_R[(0, 0, 0)]:")
print(H_R[(0, 0, 0)])
```

{{< expected-output >}}
H_R[(0, 0, 0)]:
[[0.2+0.j]]
{{< /expected-output >}}

`H_R` は格子並進 $T$ をキー、軌道基底上の行列を値とする辞書です。今回はサイト間
ホッピングがないため、$T=(0,0,0)$ のブロックだけが残ります。

## 4. Γ点で評価する

Blochハミルトニアンは、実空間ブロックから

$$
H(k) = \sum_T H(T) e^{i k \cdot T}
$$

として作られます。Γ点では $k=0$ なので位相因子はすべて1です。

```python
gamma = np.array([0.0, 0.0, 0.0], dtype=float)
H_gamma = model.Hk(gamma, H_R)
eigenvalues = np.linalg.eigvalsh(H_gamma)

print("eigenvalues at Gamma:", eigenvalues)
```

{{< expected-output >}}
eigenvalues at Gamma: [0.2]
{{< /expected-output >}}

## 5. 自分で変更する

{{< exercise >}}
`atomic_onsite` の値を `0.2` から `-0.3` に変更してください。

1. `H_R[(0,0,0)]` を予想する
2. Γ点の固有値を予想する
3. コードを実行して確認する
{{< /exercise >}}

{{< hint >}}
この模型にはホッピングがありません。したがって $H(k)$ はk点によらず同じ1×1行列です。
{{< /hint >}}

{{< solution >}}
`atomic_onsite={("Si", "s"): -0.3}` と変更すると、実空間行列は
`[[-0.3+0.j]]`、Γ点の固有値は `[-0.3]` になります。
{{< /solution >}}

## Check

- `TBModel` 作成後の3つの前処理を順番に呼べた
- `H_R` が実空間ブロックの辞書であると説明できる
- `atomic_onsite` と `params["e0"]` を同じものとして扱っていない
- Γ点の固有値を `np.linalg.eigvalsh` で確認できた

次のLessonでは最近接ボンドを追加し、対称性パラメータ `t0` が複数の
$H(T)$ ブロックへ展開される様子を調べます。
