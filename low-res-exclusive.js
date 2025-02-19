export default {
  async fetch(request) {
    const url = "https://d1172c8beu3ui6.cloudfront.net/hpclist_ios_mobile.json";

    try {
      const response = await fetch(url);
      if (!response.ok) {
        return new Response("Failed to fetch channel data", { status: 500 });
      }

      const channels = await response.json();
      let playlist = "#EXTM3U\n\n";

      channels.forEach(channel => {
        const streamUrl = channel.chsurl.split("?")[0]; // Extract base URL ending in .m3u8
        const params = new URLSearchParams(channel.chsurl.split("?")[1]); // Extract query parameters

        const tvgId = channel.chid;
        const tvgChNo = params.get("ads.channel") || "";
        const tvgLanguage = params.get("ads.language") || "";
        const channelName = params.get("ads.channel_name") || "Unknown";

        playlist += `#EXTINF:-1 tvg-id="${tvgId}" tvg-chno="${tvgChNo}" tvg-language="${tvgLanguage}", ${channelName}\n${streamUrl}\n\n`;
      });

      return new Response(playlist, {
        headers: { "Content-Type": "text/plain" },
      });
    } catch (error) {
      return new Response("Error processing request", { status: 500 });
    }
  },
};
