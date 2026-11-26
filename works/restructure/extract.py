import os,re,struct,shutil,sys
sys.path.insert(0,'/home/claude/tools')
from iemodel import *
SRC='/home/claude/bg2mock/override'; DST='/home/claude/build/out'
shutil.rmtree(DST,ignore_errors=True)
def L(n): return n.lower()
T=['CLB','SCL','RES','SWS','BLS','WNG','APO']
MAP={}   # OLD (no ext) -> NEW
def keep(old,new=None): MAP[old.upper()]=(new or old).upper()
# kit
for o,n in [('NY#BDL01','NY#KL01'),('NY#BDM10','NY#KM10'),('NY#BDM15','NY#KM15'),('NY#VSC10','NY#KSC10'),('NY#VSC15','NY#KSC15'),('NY#VRE15','NY#KRE15')]: keep(o,n)
# transformations
for c in T:
    for s in ['','E','B','C']: keep('NY#T'+c+s)
for r in ['NY#TCBT','NY#TCLE','NY#TCLR','NY#TRSI','NY#TWBF']+[f'NY#TC{w}{i}' for w in 'WO' for i in range(1,6)]: keep(r)
keep('NY#BDCLI','NY#TCLI')
# breath line
for o,n in [('NY#BDLK','NY#BLIK'),('NY#BDLG','NY#BLIG'),('NY#TBWL','NY#BLIL'),('NY#BDBRE','NY#BROAR'),('NY#BDBRI','NY#BLINB'),('NY#BDBRC','NY#BLINC'),('NY#TBWN0','NY#BLIN')]: keep(o,n)
# darkness
for o,n in [('NY#TGDK','NY#SDRK'),('NY#TGDP','NY#SDRKP'),('NY#ROTB','NY#SDRKB'),('NY#ROTC','NY#SDRKC')]: keep(o,n)
# HLA + Nydra'Nath
for o,n in [('NY#THCA','NY#HANC'),('NY#THCAB','NY#HANCB'),('NY#THCAC','NY#HANCC'),('NY#TANE','NY#HANCE'),
            ('NY#TANC','NY#CNYD'),('NY#TANB','NY#CNYDB'),('NY#TANL','NY#CNYDL'),('NY#TANF','NY#CNYDF'),('NY#TANR','NY#CNYDR'),
            ('NY#TANCS','NY#CNYDS'),('NY#TANW','NY#CNYDW'),('NY#TANP','NY#CNYDP'),('NY#TANI','NY#CNYDI'),
            ('NY#BDWAV','NY#CWAV'),('NY#BDWVT','NY#CWVT'),('NY#BDWVH','NY#CWVH')]: keep(o,n)
# files present in mock
files={}
for f in os.listdir(SRC):
    b,e=os.path.splitext(f); files.setdefault(b.upper(),[]).append(f)
STATES=['CLB','SCL','RES','SWS','BLS','WNG','APO','LV10','LV15']
st_by_val={}; has_by_row={}
for line in open(f'{SRC}/splstate.ids'):
    p=line.split()
    if len(p)==2 and p[1].startswith('NY_BDD_'): st_by_val[int(p[0])]=p[1][7:]
lines=open(f'{SRC}/splprot.2da').read().splitlines()
for i,line in enumerate(lines):
    p=line.split()
    if p and p[0].startswith('NY#HAS_'): has_by_row[i-3]=p[0][7:]   # row index = line - 3 (0-based lines)
PRO=['NY#SDRKP','NY#BLIL','NY#CNYDL','INAREANP']
pro_by_val={}
for line in open(f'{SRC}/projectl.ids'):
    p=line.split()
    if len(p)==2:
        try: v=int(p[0],0)
        except: continue
        nm=MAP.get(p[1].upper(),p[1].upper())
        if nm in PRO: pro_by_val[v+1]=nm
import subprocess
ids=subprocess.run(['/home/claude/bg2mock/weidu','--game','/home/claude/bg2mock','--biff-get','projectl.ids','--out','/tmp'],capture_output=True)
for line in open('/tmp/projectl.ids'):
    p=line.split()
    if len(p)==2 and p[1].upper() in PRO: pro_by_val[int(p[0],0)+1]=p[1].upper()
print('states',st_by_val); print('has',has_by_row); print('pro',pro_by_val)
EXT={'.spl':'spl','.itm':'itm','.cre':'cre','.eff':'eff','.pro':'pro','.vvc':'vvc','.bam':'bam','.wav':'wav','.bcs':None}
missing=[]; outs=[]
for old,new in MAP.items():
    if old not in files: missing.append(old); continue
    for f in files[old]:
        ext=os.path.splitext(f)[1].lower()
        if EXT.get(ext) is None: continue
        d=f'{DST}/{EXT[ext]}'; os.makedirs(d,exist_ok=True)
        dp=f'{d}/{L(new)}{ext}'; shutil.copy(f'{SRC}/{f}',dp); outs.append(dp)
print('missing',missing)
# resref renaming inside binaries
pairs=sorted(MAP.items(),key=lambda x:-len(x[0]))
for p in outs:
    if p.endswith(('.bam','.wav')): continue
    b=bytearray(open(p,'rb').read())
    for old,new in pairs:
        if old==new: continue
        for o,n in ((old,new),(old.lower(),new)):
            ob=o.encode()+ (b'\0' if len(o)<8 else b''); nb=n.encode().ljust(len(ob),b'\0') if len(n)<=len(o) else None
            # field-aware: replace 8-byte field contents
            i=0
            while True:
                i=b.find(o.encode(),i)
                if i<0: break
                end=i+len(o)
                if len(o)<8 and (end>=len(b) or b[end]!=0): i+=1; continue
                b[i:i+8]=n.encode().ljust(8,b'\0')[:8] if len(o)==8 else (n.encode()+b'\0'*(8-len(n)))[:8] if b[i:i+8].endswith(b'\0'*(8-len(o))) else b[i:i+8]
                i+=8
    open(p,'wb').write(b)
# placeholders
def ph_spl(p):
    r=Res(p); notes=[]
    for hb,el in r.heads:
        po=0x26 if r.kind==b'SPL ' else 0x2a
        v=struct.unpack_from('<H',hb,po)[0]
        if v>1:
            if v in pro_by_val: struct.pack_into('<H',hb,po,3000+PRO.index(pro_by_val[v]))
            else: notes.append(f'projectile {v}')
    for e in r.all_effects():
        op=eop(e); p2=ep2(e)
        if op==328:
            s=st_by_val.get(p2); 
            if s in STATES: struct.pack_into('<i',e,8,1000+STATES.index(s))
            else: notes.append(f'328 state {p2}')
        if op in (318,324,326):
            s=has_by_row.get(p2)
            if s in STATES: struct.pack_into('<i',e,8,2000+STATES.index(s))
            else: notes.append(f'{op} row {p2}')
    r.save(p); return notes
for p in outs:
    if p.endswith(('.spl','.itm')):
        n=ph_spl(p)
        if n: print(os.path.basename(p),n)

# ---------------------------------------------------------------- post fixes
O=DST
def clear_strings(p):
    b=bytearray(open(p,'rb').read())
    if b[:4] in (b'SPL ',b'ITM '):
        for o in (0x08,0x0c,0x50,0x54): struct.pack_into('<i',b,o,-1)
    elif b[:4]==b'CRE ':
        for o in (0x08,0x0c): struct.pack_into('<i',b,o,-1)
    open(p,'wb').write(b)
    if b[:4] in (b'SPL ',b'ITM '):
        r=Res(p)
        for e in r.all_effects():
            if eop(e)==139: struct.pack_into('<i',e,4,-1)
        r.save(p)
for p in outs:
    if p.endswith(('.spl','.itm','.cre')): clear_strings(p)
def prune(p,cond):
    r=Res(p); r.glob=[e for e in r.glob if not cond(e)]
    for h in r.heads: h[1]=[e for e in h[1] if not cond(e)]
    r.save(p)
known=set(os.path.splitext(os.path.basename(x))[0].upper() for x in outs)
prune(f'{O}/spl/ny#km15.spl',lambda e: eres(e)=='NY#VMI15')
prune(f'{O}/spl/ny#tswse.spl',lambda e: eop(e)==206)          # added at install
prune(f'{O}/itm/ny#cnydw.itm',lambda e: eop(e)==206)          # rebuilt below
r=Res(f'{O}/itm/ny#cnydw.itm')
for res in ('NY#BLIN','NY#SDRK'): r.glob.append(mk_eff(206,tg=1,p1=-1,tm=2,res=res))
r.save(f'{O}/itm/ny#cnydw.itm')
# --- Black Dragon Breath: Line, wizard level 2
r=Res(f'{O}/spl/ny#blin.spl')
tmpl=r.heads[0]
hb0=bytearray(tmpl[0])
keepops=lambda e: eop(e) in (165,174,215,206)
base_eff=[bytearray(e) for e in tmpl[1] if keepops(e)]
r.base[0x1c:0x1e]=struct.pack('<H',1)            # wizard spell
struct.pack_into('<I',r.base,0x34,2)               # level 2
struct.pack_into('<I',r.base,0x18,0x400)           # flags as before
r.base[0x25]=6                                     # school: evocation (invoker)
struct.pack_into('<I',r.base,0x1e,0)               # no exclusion
r.base[0x27]=10                                    # secondary type: offensive damage
r.base[0x3a:0x42]=b'NY#BLINC'
r.heads=[]
for lvl,dice in [(1,4),(5,5),(6,6),(7,7),(8,8)]:
    hb=bytearray(hb0); hb[2]=2                    # location: spell
    struct.pack_into('<H',hb,0x10,lvl); struct.pack_into('<H',hb,0x12,0)   # level, casting time 0
    hb[0x0c]=4; struct.pack_into('<H',hb,0x0e,30)
    hb[4:12]=b'NY#BLINB'
    el=[bytearray(e) for e in base_eff]
    for e in el:
        if eop(e)==206: set_res(e,'NY#BLIN')
    el.append(mk_eff(12,tg=2,p2=0x10000,dn=dice,ds=4))                               # impact, no save
    el.append(mk_eff(12,tg=2,p2=0x10000,tm=4,du=6,dn=dice//2,ds=4,sv=2))           # the acid keeps eating: next round, save vs. Breath negates
    r.heads.append([hb,el])
r.save(f'{O}/spl/ny#blin.spl')
# --- assets from the repository
REPO='/home/claude/blackdragonmagic'
def cp(src,dst):
    os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy(src,dst)
cp(f'{REPO}/kits/black_dragon_disciple/bam/ny#bdwvh.bam',f'{O}/bam/ny#cwvh.bam')
for f in os.listdir(f'{REPO}/creatures/half_black_dragon/anim'): cp(f'{REPO}/creatures/half_black_dragon/anim/{f}',f'{O}/bam/{f.lower()}')
for f in os.listdir(f'{REPO}/creatures/half_black_dragon/snd'): cp(f'{REPO}/creatures/half_black_dragon/snd/{f}',f'{O}/wav/{f.lower()}')
cp(f'{REPO}/creatures/half_black_dragon/ini/half_black_dragon.ini',f'{O}/ini/half_black_dragon.ini')
baf=open(f'{REPO}/creatures/half_black_dragon/baf/ny#tancs.baf').read()
for old,new in pairs: baf=baf.replace(old,new)
os.makedirs(f'{O}/baf',exist_ok=True); open(f'{O}/baf/ny#cnyds.baf','w').write(baf)
print('done')
