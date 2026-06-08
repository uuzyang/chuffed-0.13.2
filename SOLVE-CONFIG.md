# 求解配置说明

此文件用于记录 Chuffed 中与求解配置、搜索启发式、分支策略等相关的内容。

## 变量选择启发式（VarBranch）

支持的 FlatZinc 变量选择注释：

- `input_order`：按变量在模型中出现的顺序选择
- `first_fail` / `most_constrained`：选择当前域最小的变量
- `anti_first_fail`：选择当前域最大的变量
- `smallest`：选择最小下界变量
- `smallest_largest`：选择最大上界最小的变量
- `largest`：选择最大上界变量
- `largest_smallest`：选择最小下界最大的变量
- `occurrence`：选择出现次数最多或约束度最高的变量
- `max_regret`：选择最大后悔值变量
- `random_order`：随机顺序选择变量
- `impact`：影响度启发式，只有在编译时启用 `SUPPORT_VAR_IMPACT` 时可用

### 回退行为

如果变量选择注释无法识别，Chuffed 会回退到 `input_order`。

## 值选择启发式（ValBranch）

支持的 FlatZinc 值选择注释：

- `default`：默认值选择
- `indomain` / `indomain_min`：选择变量当前域的最小值
- `indomain_max`：选择变量当前域的最大值
- `indomain_median`：选择变量当前域的中位值
- `indomain_split`：对域进行二分，选择左半部分
- `indomain_reverse_split`：对域进行二分，选择右半部分

### 未支持或会报错的注释

以下注释目前在 Chuffed 中未实现，使用时会触发错误：

- `indomain_middle`
- `indomain_random`

如果值选择注释无法识别，会回退到 `default`。

## 示例

```minizinc
solve :: int_search(x, first_fail, indomain_min) satisfy;
solve :: bool_search(bools, random_order, default) satisfy;
```

## 其它求解配置

后续任何与求解配置相关的内容（例如 `--sbps`、`--introduced-heuristic`、重启策略、分支策略、搜索记录等）都将记录到本文件中。