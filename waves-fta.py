import requests
import json
from datetime import datetime

headers = {
    "User-Agent": "okhttp/4.12.0",
    "Connection": "keep-alive",
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "devicetype": "4",
    "devicemodel": "Realme RMX3261",
    "country": "Nepal",
    "age": "100",
    "deviceid": "020000000000",
    "version": "139",
    "iskid": "0",
    "langid": "1",
    "langcode": "1",
    "istempuser": "false",
    "isdefault": "0"
}

categories = [
    {
        "id": 1,
        "name": "News",
        "slug": "news",
        "description": "News Category",
        "priority": 1,
        "url": "https://api.wavespb.com/api/V1/getLiveChannelsV2/0/0/70"
    },
    {
        "id": 2,
        "name": "Entertainment",
        "slug": "entertainment",
        "description": "Entertainment Category",
        "priority": 2,
        "url": "https://api.wavespb.com/api/V1/getLiveChannelsV2/0/0/71"
    },
    {
        "id": 3,
        "name": "Devotional",
        "slug": "devotional",
        "description": "Devotional Category",
        "priority": 3,
        "url": "https://api.wavespb.com/api/V1/getLiveChannelsV2/0/0/72"
    },
    {
        "id": 4,
        "name": "Music",
        "slug": "music",
        "description": "Music Category",
        "priority": 4,
        "url": "https://api.wavespb.com/api/V1/getLiveChannelsV2/0/0/73"
    },
    {
        "id": 5,
        "name": "DD National Channels",
        "slug": "dd-national",
        "description": "Doordarshan National Channels",
        "priority": 5,
        "url": "https://api.wavespb.com/api/V1/getLiveChannelsV2/0/0/76"
    },
    {
        "id": 6,
        "name": "DD Regional Channels",
        "slug": "dd-regional",
        "description": "Doordarshan Regional Channels",
        "priority": 6,
        "url": "https://api.wavespb.com/api/V1/getLiveChannelsV2/0/0/77"
    }
]

feeds = []
channel_counter = 1
m3u_lines = []

# M3U8 header
m3u_header = [
    "#EXTM3U",
    "# Only Free-To-Air Streams",
    "# Scrapped by @sunilprregmi",
    f"# Scrapped on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "# Relay server is for playback",
    ""
]

m3u_lines.extend(m3u_header)

for cat in categories:
    try:
        res = requests.get(cat["url"], headers=headers)
        res.raise_for_status()
        channels_raw = res.json().get("data", [])

        channels = []
        for ch in channels_raw:
            channel_number = str(channel_counter).zfill(3)
            channel_counter += 1

            channel = {
                "channel_id": ch["id"],
                "channel_number": channel_number,
                "channel_country": "IN",
                "channel_category": cat["name"],
                "channel_name": ch["title"],
                "channel_slug": ch["title"].lower().replace(" ", "-"),
                "channel_logo": ch["thumbnail"],
                "channel_poster": ch["poster_url"]
            }

            # Add to feeds JSON
            channels.append(channel)

            # Add to M3U playlist
            m3u_lines.append(
                f'#EXTINF:-1 tvg-id="{channel["channel_id"]}" tvg-chno="{channel["channel_number"]}" '
                f'tvg-name="{channel["channel_slug"]}" tvg-logo="{channel["channel_logo"]}" '
                f'group-title="{cat["name"]}", {channel["channel_name"]}'
            )
            m3u_lines.append("#KODIPROP:inputstream=inputstream.adaptive")
            m3u_lines.append("#KODIPROP:inputstream.adaptive.manifest_type=hls")
            m3u_lines.append("#EXTVLCOPT:http-user-agent=Dalvik/2.1.0 (Linux; U; Android 12; RMX3261 Build/ace2873.0)")
            m3u_lines.append(f'https://in1.sunilprasad.com.np/wavespb/{channel["channel_id"]}/master.m3u8')
            m3u_lines.append("")

        feeds.append({
            "category_id": cat["id"],
            "category_name": cat["name"],
            "category_slug": cat["slug"],
            "category_description": cat["description"],
            "category_priority": cat["priority"],
            "channels": channels
        })

    except Exception as e:
        print(f"❌ Failed to fetch {cat['name']}: {e}")

# Save JSON
with open("waves.json", "w", encoding="utf-8") as f:
    json.dump({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feeds": feeds
    }, f, ensure_ascii=False, indent=2)

# Save M3U8
with open("waves-fta.m3u8", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))

print(f"✅ waves.json and waves-fta.m3u8 generated with {channel_counter - 1} channels.")
