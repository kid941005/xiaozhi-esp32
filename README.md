# XiaoZhi NAS Music（bread-compact-wifi / ESP32-S3-N16R8）

在 [78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) **v2.6.0**（上游 `4de00ae`）基础上，为 **面包板 bread-compact-wifi（ESP32-S3-N16R8，SSD1306 128x32）** 增加 NAS 音乐播放能力，继续使用官方/自建 xiaozhi 服务器。

音乐子系统源码来自社区项目 [jianglixi-oss/xiaozhi-nas-tf-music](https://github.com/jianglixi-oss/xiaozhi-nas-tf-music)（`592704a`），已按 LF 归一化导入并合并上游 v2.6.0。本项目与小智、微雪官方无隶属关系；上游原始说明见 [README_UPSTREAM.md](README_UPSTREAM.md)。

## 本 fork 相对上游的差异（13 个固件文件）

| 文件 | 改动 |
|---|---|
| `main/audio/music_stream.{h,cc}` | MP3 解码（`esp_mp3_dec_*` + `esp_ae_rate_cvt`→24 kHz、ID3v2 跳过、8 KB 解码缓冲在堆上） |
| `main/audio/audio_service.{h,cc}` | `PushMusicPcm` 音乐 PCM 播放队列 |
| `main/notify/notify_player.{h,cc}` | mp3 源复用通知播放器 |
| `main/application.{h,cc}` | `RequestMusic` / `RequestMusicStop` / `GetMusicStatus` |
| `main/boards/bread-compact-wifi/music_tools.cc` | 设备侧 MCP：`self.music.play_url` / `self.music.status` / `self.music.stop` |
| `main/boards/bread-compact-wifi/config.json` | 新增变体 `bread-compact-wifi-music` |
| `main/Kconfig.projbuild`、`main/CMakeLists.txt` | `CONFIG_WAVESHARE_NAS_TF_MUSIC` 开关与源文件选择 |

> TF/SD 工具只在微雪 `esp32-s3-audio-board-music` 变体编译；本板无 SD 引脚，`music_tools.cc` 只保留 play_url / status / stop。

## 两条播放路径（都能出声，互不替代）

1. **服务端插件路径**（官方原版固件同样可用）：`play_music` 函数 → 服务端 ffmpeg/pydub 解码 → 24 kHz 单声道 Opus → TTS 队列。说“播放某某”即可触发；曲库来自容器内 `music_dir`（默认 `/opt/xiaozhi/music`）。
2. **设备本地直链路径**（本 fork 独有）：服务返回音频直链 → 调 `self.music.play_url` → 设备本地 MP3 解码播放；播放期间关闭语音处理（`EnableVoiceProcessing(false)`），可用唤醒词打断。

## 编译与烧写

ESP-IDF 需 **6.1（release/v6.1）**，最低 6.0.1。Windows 下用 PowerShell 的 `export.ps1` 激活环境。

```sh
python scripts/build.py bread-compact-wifi --name bread-compact-wifi-music --language zh-CN --zip
```

- **`--language zh-CN` 必加**：v2.6.0 默认 en-US，会选中 `wn9_hiesp`（Hi ESP）唤醒词；中文构建把 `wn9_nihaoxiaozhi_tts`（你好小智）打包进 assets 分区。
- 产物：`releases/v2.6.0_bread-compact-wifi-music.zip`（内含 `merged-binary.bin`）。
- 首次全量烧录 `0x0` 会清空 NVS（需重新配网与激活）；只升级应用时把 `build/xiaozhi.bin` 烧到 `0x20000`，保留配网与激活。

## 已知限制

- 板级输出固定 24 kHz 单声道（`config.h` 的 `AUDIO_OUTPUT_SAMPLE_RATE 24000` + NoAudioCodec Simplex），无损音源收益≈0。
- 设备本地路径只解 MP3（`music_stream.cc` 仅调用 `esp_mp3_dec_*`）；FLAC/M4A/AAC/OGG 由服务端插件路径支持。
- 服务端插件路径播放时麦克风不关闭，可能把自己播放的音乐识别为环境噪音。
- 无暂停续播、上下首、进度跳转、歌词；TF 功能仅微雪变体。
- 上游同步评估见 `docs/merge_v2.6.0_assessment.md`，仓库核查见 `docs/repo_audit_v2.6.0.md`。

## 来源与许可

沿用 [MIT 许可证](LICENSE)，保留上游版权声明。MCP 桥接程序来自 [78/mcp-calculator](https://github.com/78/mcp-calculator)（MIT）；第三方组件各自许可证继续适用，详见 [第三方说明](THIRD_PARTY_NOTICES.md)。
