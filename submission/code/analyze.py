"""All numbers in the submission come from this script. Run: python3 submission/code/analyze.py
Reads the cached JSON in data/ (produced by pull.py)."""
import json, collections as C, datetime as D
L = lambda t: {r['id']: r['fields'] for r in json.load(open(f'data/{t}.json'))}
dep, ppl, job, cand, app, itv, off = map(L, ["Departments","People","Job_Openings","Candidates","Applications","Interviews","Offers"])
d = lambda s: D.date.fromisoformat(s) if s else None
one = lambda f, k: (f.get(k) or [None])[0]
pct = lambda a, b: f"{a}/{b} = {100*a/b:.1f}%" if b else f"{a}/0"
def H(t): print(f"\n## {t}")

H("CLAIM 1: hires by source")
hired = [a for a in app.values() if a['Stage'] == 'Hired']
src = lambda a: cand[one(a,'Candidate')]['Source']
hs = C.Counter(src(a) for a in hired); asrc = C.Counter(src(a) for a in app.values()); csrc = C.Counter(c['Source'] for c in cand.values())
print("hired apps:", len(hired))
for s in csrc: print(f"  {s:12} candidates {csrc[s]:3} apps {asrc[s]:3} hires {hs[s]:2} | share of hires {pct(hs[s],len(hired))} | app->hire {pct(hs[s],asrc[s])}")
# referral mismatch: application has Referred By but candidate source isn't Referral
rb = [a for a in app.values() if a.get('Referred By')]
print("apps with Referred By:", len(rb), "candidate source of those:", C.Counter(src(a) for a in rb))
hr = [a for a in hired if a.get('Referred By')]
print("hires with Referred By set:", pct(len(hr), len(hired)), C.Counter(src(a) for a in hr))
hs2 = C.Counter('Referral' if a.get('Referred By') else src(a) for a in hired)
print("hire share if Referred By overrides Source:", {k: pct(v,len(hired)) for k,v in hs2.items()})
# hired stage vs accepted offers
acc_apps = {one(o,'Application') for o in off.values() if o['Status']=='Accepted'}
hired_ids = {k for k,a in app.items() if a['Stage']=='Hired'}
print("Hired w/o accepted offer:", len(hired_ids-acc_apps), "| accepted offer not Hired:", len(acc_apps-hired_ids))
for k in acc_apps-hired_ids: print("   ", app[k]['Application ID'], app[k]['Stage'], app[k]['Status'])
hsa = C.Counter(src(app[k]) for k in acc_apps)
print("share of ACCEPTED OFFERS by source:", {k: pct(v,len(acc_apps)) for k,v in hsa.items()})

H("CLAIM 2: offer acceptance")
st = C.Counter(o['Status'] for o in off.values()); n = len(off)
print(st)
print("VP-style accepted/all offers:", pct(st['Accepted'], n))
print("accepted/decided (excl pending):", pct(st['Accepted'], st['Accepted']+st['Declined']))
for o in off.values():
    if o['Status']=='Pending': print("  pending:", o['Offer ID'], 'offered', o['Offered On'], 'decision', o.get('Decision On'), 'app stage', app[one(o,'Application')]['Stage'])
for o in off.values():
    if o['Status']=='Declined': print("  declined:", o['Offer ID'], o.get('Decline Reason'), 'base', o['Base CTC'], 'expected', cand[one(app[one(o,'Application')],'Candidate')]['Expected CTC'])
# offer vs band / expected CTC
below = [o for o in off.values() if o['Base CTC'] < cand[one(app[one(o,'Application')],'Candidate')]['Expected CTC']]
print("offers below candidate expected CTC:", pct(len(below), n), C.Counter(o['Status'] for o in below))
ob = [o for o in off.values() if not (job[one(app[one(o,'Application')],'Opening')]['Salary Band Min'] <= o['Base CTC'] <= job[one(app[one(o,'Application')],'Opening')]['Salary Band Max'])]
print("offers outside opening salary band:", pct(len(ob), n), [(o['Offer ID'],o['Base CTC'],o['Status']) for o in ob])
dd = [(d(o['Decision On'])-d(o['Offered On'])).days for o in off.values() if o.get('Decision On')]
print("days offer->decision: min", min(dd), "max", max(dd), "negative:", sum(x<0 for x in dd))
bym = C.defaultdict(C.Counter)
for o in off.values(): bym[o['Offered On'][:7]][o['Status']] += 1
print("by offer month:", dict(sorted(bym.items())))

H("D4: data quality")
ids = C.Counter(a['Application ID'] for a in app.values())
dupid = {k:v for k,v in ids.items() if v>1}; print("duplicate Application IDs:", dupid)
for k,a in app.items():
    if a['Application ID'] in dupid: print("   ", a['Application ID'], a['Stage'], a['Applied On'], cand[one(a,'Candidate')]['Candidate ID'], job[one(a,'Opening')]['Req ID'])
pc = C.Counter(c['Phone'] for c in cand.values()); nm = C.Counter(c['Full Name'] for c in cand.values())
dupc = [c for c in cand.values() if pc[c['Phone']]>1]
print("candidates sharing a phone:", len(dupc))
for c in sorted(dupc, key=lambda c: c['Phone']): print("   ", c['Candidate ID'], 'group', sorted(pc).index(c['Phone']), c['Source'], c['Created On'])
print("names repeated:", sum(v>1 for v in nm.values()))
# per-candidate pair (candidate, opening) duplicates
pair = C.Counter((one(a,'Candidate'), one(a,'Opening')) for a in app.values())
print("same candidate+opening >1 application:", sum(v>1 for v in pair.values()))
# date ordering
seq = ['Applied On','Screened On','First Interview On','Final Interview On','Offered On','Closed On']
bad = C.Counter(); badrows = []
for a in app.values():
    ds = [(k, d(a.get(k))) for k in seq if a.get(k)]
    for (k1,v1),(k2,v2) in zip(ds, ds[1:]):
        if v2 < v1: bad[f"{k2} < {k1}"] += 1; badrows.append(a['Application ID'])
print("date-order violations:", dict(bad), "rows:", len(set(badrows)))
ac = [a for a in app.values() if d(a['Applied On']) < d(cand[one(a,'Candidate')]['Created On'])]
print("applied before candidate created:", len(ac))
jo = [a for a in app.values() if d(a['Applied On']) < d(job[one(a,'Opening')]['Opened On'])]
print("applied before opening opened:", len(jo))
# stage/status consistency
print("stage x status:", C.Counter((a['Stage'],a['Status']) for a in app.values()))
print("Closed w/o Closed On:", sum(a['Status']=='Closed' and not a.get('Closed On') for a in app.values()),
      "| Active with Closed On:", sum(a['Status']=='Active' and bool(a.get('Closed On')) for a in app.values()))
print("Rejected w/o reason:", sum(a['Stage']=='Rejected' and not a.get('Rejection Reason') for a in app.values()),
      "| reason on non-rejected:", C.Counter(a['Stage'] for a in app.values() if a.get('Rejection Reason') and a['Stage']!='Rejected'))
print("rejection reasons:", C.Counter(a.get('Rejection Reason') for a in app.values() if a['Stage']=='Rejected'))
print("Offered On on app but no Offer record:", sum(bool(a.get('Offered On')) != bool(a.get('Offers')) for a in app.values()))
mm = [o['Offer ID'] for o in off.values() if app[one(o,'Application')].get('Offered On') != o['Offered On']]
print("offer date mismatch app vs offer table:", mm)
print("Interview stage apps w/o interviews:", sum(a['Stage'] in ('Interview','Offer','Hired') and not a.get('Interviews') for a in app.values()))
print("Hired with no interview:", sum(a['Stage']=='Hired' and not a.get('Interviews') for a in app.values()))
# interviews
print("interview outcome x has score:", C.Counter((i['Outcome'], 'Score' in i) for i in itv.values()))
rec_score = C.defaultdict(list)
for i in itv.values():
    if 'Score' in i: rec_score[i['Recommendation']].append(i['Score'])
print("score range by recommendation:", {k:(min(v),max(v),round(sum(v)/len(v),2)) for k,v in rec_score.items()})
print("score scale:", sorted({i['Score'] for i in itv.values() if 'Score' in i})[:5], '...', sorted({i['Score'] for i in itv.values() if 'Score' in i})[-5:])
print("interviewer roles:", C.Counter(ppl[one(i,'Interviewer')]['Role'] for i in itv.values()))
fut = [i for i in itv.values() if i['Outcome']=='Completed' and i.get('Completed On') and d(i['Completed On']) > D.date(2026,8,27)]
print("completed in future vs data snapshot 2026-08-27:", len(fut))
print("max dates: applied", max(a['Applied On'] for a in app.values()), "offer", max(o['Offered On'] for o in off.values()))
# hires vs headcount
for jid,j in job.items():
    h = sum(1 for a in app.values() if one(a,'Opening')==jid and a['Stage']=='Hired')
    if h > j['Headcount'] or (j['Status']=='Filled' and h < j['Headcount']) or (j['Status'] in ('Cancelled','On Hold') and h): print("   req", j['Req ID'], j['Status'], 'headcount', j['Headcount'], 'hired', h)
print("department hired vs budget skipped (no actual headcount field)")
# CTC sanity
print("expected<current CTC:", sum(c['Expected CTC']<c['Current CTC'] for c in cand.values()), "| zero exp yrs w CTC>20L:", sum(c['Years Experience']==0 and c['Current CTC']>2000000 for c in cand.values()))
print("years exp range:", min(c['Years Experience'] for c in cand.values()), max(c['Years Experience'] for c in cand.values()))
print("candidate notes:", C.Counter(c.get('Notes','')[:60] for c in cand.values()).most_common(8))
ref_note = [c for c in cand.values() if c.get('Notes','').startswith('Referred internally')]
print("notes say 'Referred internally' -> Source:", C.Counter(c['Source'] for c in ref_note))
print("apps per candidate:", C.Counter(len(c['Applications']) for c in cand.values()))

H("SENSITIVITY")
import math
def wilson(k, n, z=1.96):
    p = k/n; den = 1+z*z/n; c = (p+z*z/(2*n))/den; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return f"{100*p:.1f}% [95% CI {100*(c-h):.1f}-{100*(c+h):.1f}]"
print("job-board hire share", wilson(7,26), "| referral hire share", wilson(7,26))
print("job-board app->hire", wilson(7,236), "| referral app->hire", wilson(7,13), "| non-JB app->hire", wilson(19,114))
print("acceptance all offers", wilson(26,36), "| decided only", wilson(26,31))
# stale pending: pending with a Decision On date, or >30 days old at snapshot
snap = D.date(2026,8,27)
for o in off.values():
    if o['Status']=='Pending': print("  ", o['Offer ID'], "age days", (snap-d(o['Offered On'])).days, "has decision date", bool(o.get('Decision On')))
print("if the 3 pendings older than 30d are declines:", pct(26, 26+5+3), "| if all 5 pendings decline:", pct(26,36), "| if all 5 accept:", pct(31,36))
# duplicate-person effect
dupcids = {k for k,c in cand.items() if pc[c['Phone']]>1}
print("hires among duplicated people:", [(cand[one(a,'Candidate')]['Candidate ID'], src(a)) for a in hired if one(a,'Candidate') in dupcids])
print("apps from duplicated people:", sum(one(a,'Candidate') in dupcids for a in app.values()), C.Counter(src(a) for a in app.values() if one(a,'Candidate') in dupcids))
# multi-app job-board candidates
print("job-board candidates with 2 apps:", sum(1 for c in cand.values() if c['Source']=='Job Board' and len(c['Applications'])==2))
print("JB app->hire per CANDIDATE:", pct(7, csrc['Job Board']), "| referral per candidate:", pct(7, csrc['Referral']))
# rejection "Comp Expectation" and accept rate by offer vs expected
for lab, grp in [("offer>=expected", [o for o in off.values() if o not in below]), ("offer<expected", below)]:
    s = C.Counter(o['Status'] for o in grp); print(lab, dict(s), "decided accept", pct(s['Accepted'], s['Accepted']+s['Declined']))
# time to hire by source
t2h = C.defaultdict(list)
for a in hired: t2h[src(a)].append((d(a['Closed On'])-d(a['Applied On'])).days)
print("median days apply->hire by source:", {k: sorted(v)[len(v)//2] for k,v in t2h.items()})
print("recruiter app counts (anonymised):", sorted(C.Counter(one(a,'Recruiter') for a in app.values()).values()))
