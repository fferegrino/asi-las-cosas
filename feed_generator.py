import podcastparser
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

output_dir = Path('output')
output_dir.mkdir(parents=True, exist_ok=True)

feed_url = 'https://fapi-top.prisasd.com/podcast/wradiomexico/asi_las_cosas/itunestfp/podcast.xml'

original_feed = podcastparser.parse(feed_url, urllib.request.urlopen(feed_url))

def identify_times(title):
    time_pattern = r'\d{2}:\d{2}'
    times = re.findall(time_pattern, title)
    return sorted(times)

new_episodes = []
for episode in original_feed['episodes']:
    parsed_times = identify_times(episode['title'])
    if parsed_times:
      episode['parsed_times'] = parsed_times
      new_episodes.append(episode)

original_feed['episodes'] = new_episodes

from feedgen.feed import FeedGenerator
fg = FeedGenerator()

fg.id(original_feed['link'])
fg.title(original_feed['title'])
fg.author( original_feed['itunes_owner'] )
fg.link( href=original_feed['link'], rel='self' )
fg.logo(original_feed['cover_url'])
fg.subtitle(original_feed['description'])
fg.description(original_feed['description'])
fg.language('es')

for episode in original_feed['episodes']:
    fe = fg.add_entry()
    fe.description(episode['description'])
    fe.id(episode['link'])
    fe.title(episode['title'])
    enclosure = episode['enclosures'][0]
    fe.enclosure(enclosure['url'], enclosure['file_size'], enclosure['mime_type'])
    date = datetime.fromtimestamp(episode['published'], tz=timezone.utc)
    fe.pubdate(date)

fg.rss_file(output_dir / 'feed.xml')
