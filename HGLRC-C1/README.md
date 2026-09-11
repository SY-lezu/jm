# HGLRC C1 / 化骨龙 C1 — ExpressLRS 固件与恢复资料

本目录用于保存 HGLRC C1 遥控器内置 2.4GHz ExpressLRS TX 的恢复资料。

## 先看结论

HGLRC 官方资料给 C1 标注的 ELRS target 是：

`DIY devices 2.4 GHz -> DIY ESP32 + E28 2.4GHz TX`

但是 **C1 原厂固件不是“普通 DIY E28 固件直接刷进去就完全等价”**。

2026 年 8 月，一位 DRAGON_V2.0 版 C1 用户从原机导出了 stock ELRS binary，并对比发现原厂固件是基于 ELRS 3.2 的 HGLRC 定制版本；至少存在 UART inversion 等与普通 DIY E28 构建不同的设置。刷普通 DIY E28 后可能出现：

- USB 仍只显示 CH340 串口；
- 摇杆/按键对 ELRS 模块无响应；
- C1 的 Wi-Fi/Bind/功率快捷控制失效；
- 甚至可能因功率控制失效而长期卡在高功率。

这与 C1 的硬件结构有关：摇杆/按键由独立 MM32 主控采集，再通过串口/CRSF 类链路送给 ESP32+E28 ELRS 模块。USB-C 本身主要用于充电与刷写，因此 Windows 看到 CH340 并不等于遥控器控制链路正常。

## 官方 target 对照

ExpressLRS 3.x 官方源码中，普通兼容 target 为：

`DIY_2400_TX_ESP32_SX1280_E28_via_UART`

board config：

`diy.tx_2400.e28`

这个 target 只能作为硬件基础参考，**不能再把它标成 HGLRC C1 原厂固件**。

## DRAGON_V2.0 原机 stock dump

来源讨论：
https://www.reddit.com/r/fpv/comments/1vkwwpz/updating_hglrc_c1_remote_to_elrs_41/

原作者分享的 stock dump：
https://files.catbox.moe/ap0jfk.bin

仓库中的 `.github/workflows/fetch-hglrc-c1-stock.yml` 会从原始分享地址下载该文件，计算 SHA256、大小，并尝试使用 esptool 做 ESP32 镜像信息检查；成功后写入：

`HGLRC-C1/stock/`

注意：该文件来自社区用户的原机备份，不是 HGLRC 官网发布/签名的固件。因此仓库会明确标注 provenance，不把它冒充为“官方发布包”。

## 对当前故障的建议

如果 C1 在刷普通 DIY E28 后出现“只能看到 CH340、摇杆没反应、Wi-Fi 进不去”，不要继续反复刷 3.3.1/4.x 通用固件。优先恢复与原机逻辑兼容的 stock ELRS 镜像，再验证：

1. C1 上电后 ELRS 模块是否正常启动；
2. 摇杆/按键是否能传到 ELRS；
3. Wi-Fi/Bind 快捷操作是否恢复；
4. 最后再做对频与飞控 Receiver 页验证。

上游 ExpressLRS：
https://github.com/ExpressLRS/ExpressLRS
