# HGLRC C1 / 化骨龙 C1 — ExpressLRS 固件

本目录用于保存 HGLRC C1 遥控器内置 2.4GHz ExpressLRS TX 固件与构建说明。

## 已核对的官方目标

HGLRC C1 官方资料标注的 ELRS 固件名称为：

`DIY devices 2.4 GHz -> DIY ESP32 + E28 2.4GHz TX`

在 ExpressLRS 3.0.1 官方源码中，对应 PlatformIO target 为：

`DIY_2400_TX_ESP32_SX1280_E28_via_UART`

对应 board config：

`diy.tx_2400.e28`

## 版本

优先保留：
- ELRS 3.0.1（C1 实机常见、适合恢复测试）
- ELRS 3.3.1（用于对比测试）

## 重要说明

这里保存的是基于 ExpressLRS 官方源码、按 HGLRC C1 对应兼容 target 构建的固件。不要把 `HGLRC Hermes 2.4GHz TX` target 与 C1 混用；C1 官方资料指定的是 DIY ESP32 + E28 2.4GHz TX。

刷写失败时优先通过 USB/UART 恢复，不要反复尝试不匹配的 target。

官方上游： https://github.com/ExpressLRS/ExpressLRS
