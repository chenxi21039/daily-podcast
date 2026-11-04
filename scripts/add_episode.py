#!/usr/bin/env python3
"""用法: python3 scripts/add_episode.py <mp3路径> <标题> <描述> <日期YYYY-MM-DD> [--slug xxx]"""
import sys,os,json,shutil,subprocess,argparse,datetime,html
from email.utils import format_datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE='https://chenxi21039.github.io/daily-podcast'
TZ=datetime.timezone(datetime.timedelta(hours=8))
# ---- 频道配置 ----
CHANNEL=dict(title='信任阶梯',author='西西弗',email='chenxi21039@users.noreply.github.com',cover='cover-v2.jpg',
  desc='聊 AI Agent 与人机协作：怎样一步步建立对 AI 的信任，把方法论变成每天的工作流。')
CH=CHANNEL
def esc(s):return html.escape(s,quote=True)
def hms(s):s=int(round(s));return f'{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}'
def build(eps):
    eps=sorted(eps,key=lambda e:e['pubdate'],reverse=True)
    items=''.join(f'''
  <item>
    <title>{esc(e['title'])}</title>
    <description>{esc(e['description'])}</description>
    <itunes:summary>{esc(e['description'])}</itunes:summary>
    <enclosure url="{BASE}/episodes/{e['file']}" length="{e['bytes']}" type="audio/mpeg"/>
    <guid isPermaLink="false">{e['guid']}</guid>
    <pubDate>{e['pubdate_rfc']}</pubDate>
    <itunes:duration>{hms(e['duration'])}</itunes:duration>
    <itunes:explicit>false</itunes:explicit>
  </item>''' for e in eps)
    feed=f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{CH['title']}</title>
  <link>{BASE}/</link>
  <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
  <language>zh-cn</language>
  <description>{esc(CH['desc'])}</description>
  <itunes:author>{esc(CH['author'])}</itunes:author>
  <itunes:owner><itunes:name>{esc(CH['author'])}</itunes:name><itunes:email>{CH['email']}</itunes:email></itunes:owner>
  <managingEditor>{CH['email']} ({esc(CH['author'])})</managingEditor>
  <itunes:image href="{BASE}/{CH['cover']}"/>
  <image><url>{BASE}/{CH['cover']}</url><title>{CH['title']}</title><link>{BASE}/</link></image>
  <itunes:category text="Technology"/>
  <itunes:explicit>false</itunes:explicit>
  <itunes:block>yes</itunes:block>{items}
</channel>
</rss>
'''
    open(os.path.join(ROOT,'feed.xml'),'w').write(feed)
    li=''.join(f'<li><b>{esc(e["title"])}</b>（{e["pubdate"]}，{hms(e["duration"])}）<br>{esc(e["description"])}<br><audio controls preload="none" src="episodes/{e["file"]}"></audio></li>' for e in eps)
    open(os.path.join(ROOT,'index.html'),'w').write(f'''<!doctype html><html lang="zh-cn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{CH['title']}</title></head>
<body style="font-family:sans-serif;max-width:720px;margin:auto;padding:16px">
<img src="{CH['cover']}" width="160" alt="封面"><h1>{CH['title']}</h1><p>主理：{esc(CH['author'])}</p><p>{esc(CH['desc'])}</p>
<p>订阅地址（在苹果播客 / Pocket Casts 中“通过 URL 添加”）：<br><code>{BASE}/feed.xml</code></p>
<h2>剧集</h2><ul>{li}</ul></body></html>''')
if __name__=='__main__' and sys.argv[1:]==['--rebuild']:
    build(json.load(open(os.path.join(ROOT,'episodes.json'))));sys.exit()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mp3');p.add_argument('title');p.add_argument('description');p.add_argument('date');p.add_argument('--slug',default='episode')
    a=p.parse_args()
    d=datetime.datetime.strptime(a.date,'%Y-%m-%d').replace(hour=8,tzinfo=TZ)
    fn=f'{a.date}-{a.slug}.mp3';dst=os.path.join(ROOT,'episodes',fn)
    if os.path.abspath(a.mp3)!=dst: shutil.copyfile(a.mp3,dst)
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',dst]).strip())
    jp=os.path.join(ROOT,'episodes.json');eps=json.load(open(jp)) if os.path.exists(jp) else []
    eps=[e for e in eps if e['file']!=fn]
    eps.append(dict(file=fn,title=a.title,description=a.description,pubdate=a.date,pubdate_rfc=format_datetime(d),guid=f'daily-podcast-{a.date}-{a.slug}',bytes=os.path.getsize(dst),duration=dur))
    json.dump(eps,open(jp,'w'),ensure_ascii=False,indent=1);build(eps);print('ok',fn,hms(dur))

def rebuild():
    build(json.load(open(os.path.join(ROOT,'episodes.json'))))
