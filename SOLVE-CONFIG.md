# 求解配置说明

此文件用于记录 Chuffed 中与求解配置、搜索启发式、分支策略等相关的内容。

## 变量选择启发式（VarBranch）

支持的 FlatZinc *变量选择注释*：

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

## 内部可用的变量选择枚举

`chuffed/branching/branching.h` 中还定义了一组完整的 `VarBranch` 枚举，包含更多内部变量启发式：

- `VAR_DEFAULT`：自动搜索
- `VAR_INORDER`：输入顺序
- `VAR_SIZE_MIN`：最小域（对应 `first_fail`）
- `VAR_SIZE_MAX`：最大域（对应 `anti_first_fail`）
- `VAR_MIN_MIN`：最小下界（对应 `smallest`）
- `VAR_MIN_MAX`：最大下界（对应 `largest_smallest`）
- `VAR_MAX_MIN`：最小上界（对应 `smallest_largest`）
- `VAR_MAX_MAX`：最大上界（对应 `largest`）
- `VAR_DEGREE_MIN`：最小度数
- `VAR_DEGREE_MAX`：最大度数
- `VAR_REGRET_MIN_MAX`：最大最小后悔值（对应 `max_regret`）
- `VAR_REGRET_MAX_MAX`：最大最大后悔值
- `VAR_REDUCED_COST`：基于 MIP 的最大减少成本
- `VAR_PSEUDO_COST`：基于 MIP 的最大伪成本
- `VAR_ACTIVITY`：最大 VSIDS 活动度
- `VAR_RANDOM`：随机顺序
- `VAR_IMPACT`：影响度启发式（需要 `SUPPORT_VAR_IMPACT`）

### 说明

目前 FlatZinc 的 `ann2ivarsel` 只将一部分注释映射到这些枚举值，因此并非所有内部枚举值都有对应的 FlatZinc 注释名称。比如 `VAR_DEGREE_MIN`、`VAR_REDUCED_COST`、`VAR_PSEUDO_COST`、`VAR_ACTIVITY` 等并没有在当前代码中直接暴露为 FlatZinc 注释。

## 内部可用的值选择枚举

`chuffed/branching/branching.h` 中的 `ValBranch` 枚举也包含更多内部值选择策略：

- `VAL_DEFAULT`：默认策略
- `VAL_MIN`：最小值
- `VAL_MAX`：最大值
- `VAL_MIDDLE`：中间值
- `VAL_MEDIAN`：中位数
- `VAL_SPLIT_MIN`：域左半部分
- `VAL_SPLIT_MAX`：域右半部分
- `VAL_RANDOM`：随机值

### 说明

当前 FlatZinc 的 `ann2ivalsel` 只映射了 `VAL_DEFAULT`、`VAL_MIN`、`VAL_MAX`、`VAL_MEDIAN`、`VAL_SPLIT_MIN`、`VAL_SPLIT_MAX`。`VAL_MIDDLE` 和 `VAL_RANDOM` 在源码中被注释掉/标记为暂不支持。
