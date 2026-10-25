# C/C++ 库 NAPI 交叉编译指南

> 当 Level 1（ohpm）和 Level 2（原生 API）都无法满足需求时，可通过 NAPI 桥接 C/C++ 开源库。

---

## 适用场景

- 音视频处理（FFmpeg）
- 图像算法（OpenCV）
- 加解密（OpenSSL）
- 其他计算密集型的 C/C++ 库

---

## 方式一：CMake 构建（最常见）

```bash
cmake \
  -DCMAKE_TOOLCHAIN_FILE=${OHOS_SDK}/native/build/cmake/ohos.toolchain.cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DOHOS_ARCH=arm64-v8a \
  ..
ninja -C build
```

### 关键环境变量

| 变量 | 说明 |
|------|------|
| `OHOS_SDK` | HarmonyOS SDK 路径 |
| `OHOS_ARCH` | 目标架构：`arm64-v8a`（手机）/ `armeabi-v7a` / `x86_64`（模拟器）|
| `CMAKE_TOOLCHAIN_FILE` | SDK 自带的工具链文件 |

---

## 方式二：oh-compile-script（推荐）

基于 Conan 2.x 的自动化编译工具，已预置 100+ 常用库的依赖管理：

```bash
git clone https://gitee.com/aspect1103/oh-compile-script.git
pip install conan==2.x
python3 build.py --lib=ffmpeg --arch=arm64-v8a
```

### 支持的库（部分）

- FFmpeg（完整 7 大核心库）
- OpenSSL
- libjpeg-turbo
- libpng
- zlib
- curl

---

## 编译产物验证

```bash
# 检查是否为 ARM aarch64 架构
file libxxx.so       # 期望: ELF 64-bit LSB shared object, ARM aarch64

# 检查导出符号
nm -D libxxx.so | grep <目标函数>
```

---

## 在 ArkTS 项目中使用

1. 将 `.so` 文件放入 `entry/libs/arm64-v8a/`
2. 编写 NAPI 绑定层（C/C++）
3. 在 `CMakeLists.txt` 中配置
4. ArkTS 侧通过 `import xxx from 'libxxx.so'` 调用

---

## 注意事项

- 交叉编译的 .so 必须匹配目标设备架构
- 模拟器用 `x86_64`，真机用 `arm64-v8a`
- Debug 包体积会显著增大，Release 模式编译
- 某些库可能需要禁用不支持的系统调用
