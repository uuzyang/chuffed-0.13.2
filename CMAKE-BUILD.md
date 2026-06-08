# CMake 与构建说明

这个文件用于记录 Chuffed 项目中与 CMake、构建和配置相关的内容。

## 1. 生成构建目录

在项目根目录中运行：

```powershell
cd d:\work\research\chuffed-0.13.2
cmake -B build -S .
```

这会在 `build` 目录下生成 CMake 构建系统。

## 2. 编译可执行文件

生成后直接编译：

```powershell
cmake --build build
```

这会构建默认目标并生成 `fzn-chuffed.exe`。

## 3. 重新生成新的 `fzn-chuffed`

如果改动了源代码：

```powershell
cmake --build build
```

如果改动了 CMake 配置、选项或 `CMakeLists.txt`：

```powershell
cmake -B build -S .
cmake --build build
```

如果要指定 Debug 配置：

```powershell
cmake --build build --config Debug
```

## 4. 关闭 CP Profiler（推荐在 Windows 下避免网络依赖链接问题）

项目默认 `CP_PROFILER` 是开启的。该选项会编译 `thirdparty/cp-profiler-integration` 中的代码，支持 CP Profiler 集成。

如果不需要这个功能，可以关闭：

```powershell
cmake -B build -S . -DCP_PROFILER=OFF
cmake --build build
```

## 5. 常见问题

### 5.1 Windows 下链接失败：缺少 `Ws2_32`

如果在链接阶段出现类似：

- `undefined reference to __imp_WSAStartup`
- `undefined reference to __imp_send`
- `undefined reference to __imp_socket`

说明 Profiler 集成的 socket 代码需要 Windows Winsock 库，但当前没有正确链接。

解决办法：

- 关闭 `CP_PROFILER`，或者
- 在 `CMakeLists.txt` 中为 Windows 添加 `ws2_32` 链接库。

## 6. 其他命令

- 安装目标：

```powershell
cmake --build build --target install
```

- 编译 C++ 示例：

```powershell
cmake --build build --target examples
```

- 格式化源代码：

```powershell
cmake --build build --target format
```

## 7. 备注

这个文件后续可以继续补充与 CMake 配置、构建选项和项目定制相关的内容。

## 8. 在最终输出中包含统计信息

已将运行结束时的统计信息（例如总时间、节点数、重启次数、冲突数等）加入到 `fzn-chuffed` 的最终输出中。

- 实现方式：在 `chuffed/flatzinc/fzn-chuffed.cpp` 中，在求解完成后调用 `engine.printStats()`，因此 `fzn-chuffed` 在输出解后会打印以 `%%%%%mzn-stat:` 开头的标准统计行，便于被外部工具解析。
- 如果你不想在终端看到这些统计信息，可以在解析输出时过滤 `%%%%%mzn-stat:` 行，或修改源码以按需启用/禁用该打印。
