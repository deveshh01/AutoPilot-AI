"""Pull every table from the Airtable base once and cache as JSON under data/.
Respects 5 req/s limit; paginates 100 records/page. Token read from env (.env)."""
import os, json, time, sys, urllib.request, urllib.parse
for l in open('.env'):
    k, _, v = l.strip().partition('=')
    os.environ.setdefault(k, v)
T, B = os.environ['AIRTABLE_TOKEN'], os.environ['AIRTABLE_BASE']
TABLES = ["Departments","People","Job Openings","Candidates","Applications","Interviews","Offers","Findings"]
def get(url):
    for _ in range(5):
        try:
            r = urllib.request.Request(url, headers={"Authorization": f"Bearer {T}"})
            return json.load(urllib.request.urlopen(r, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(31); continue
            raise
os.makedirs('data', exist_ok=True)
for t in TABLES:
    recs, off = [], None
    while True:
        u = f"https://api.airtable.com/v0/{B}/{urllib.parse.quote(t)}?pageSize=100" + (f"&offset={off}" if off else "")
        d = get(u); recs += d['records']; off = d.get('offset'); time.sleep(0.25)
        if not off: break
    json.dump(recs, open(f'data/{t.replace(" ","_")}.json','w'))
    print(t, len(recs))
