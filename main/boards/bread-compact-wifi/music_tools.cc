#include "sdkconfig.h"
#ifdef CONFIG_WAVESHARE_NAS_TF_MUSIC

#include <string>

#include "application.h"
#include "mcp_server.h"

// NAS MP3 tools for boards without an SD slot.
// The waveshare audio board additionally exposes TF card tools; those are
// intentionally omitted here because this board has no SD slot and GPIO40/41/42
// are already used by the volume-up button and the OLED I2C bus.
void InitializeAudioBoardMusicTools() {
    auto& mcp = McpServer::GetInstance();
    mcp.AddTool("self.music.status",
                "Get actual music status: idle, queued, playing, completed, failed or stopped.",
                PropertyList(), [](const PropertyList&) -> ReturnValue {
                    static const char* names[] = {"idle",      "queued", "playing",
                                                  "completed", "failed", "stopped"};
                    int status = Application::GetInstance().GetMusicStatus();
                    return std::string(names[status >= 0 && status < 6 ? status : 0]);
                });
    mcp.AddTool(
        "self.music.play_url",
        "Play an HTTP/HTTPS MP3 URL returned by the NAS music search tool. "
        "This queues playback and ends the current voice session; do not announce playback as "
        "completed.",
        PropertyList({Property("url", kPropertyTypeString).SetMaxLength(2048)}),
        [](const PropertyList& p) -> ToolResult {
            auto url = p["url"].value<std::string>();
            if ((!url.starts_with("http://") && !url.starts_with("https://")) ||
                url.find_first_of("\r\n\t ") != std::string::npos ||
                url.find('@') != std::string::npos)
                return std::unexpected("Expected HTTP/HTTPS MP3 URL without embedded credentials");
            Application::GetInstance().RequestMusic(std::move(url));
            return std::string("Playback requested; actual download/decoding may still fail.");
        });
    mcp.AddTool("self.music.stop", "Stop NAS music and cancel any queued music request.",
                PropertyList(), [](const PropertyList&) -> ReturnValue {
                    Application::GetInstance().RequestMusicStop();
                    return std::string("Stop requested.");
                });
}
#endif
