import os,sys,json,urllib.request as U
E=os.environ['MAKEFUN_ENV_URL']
V={'P':100,'N':320,'B':330,'R':500,'Q':900,'K':20000}
N=[-21,-19,-12,-8,8,12,19,21]
K=[-11,-10,-9,-1,1,9,10,11]
R=[-10,10,-1,1]
B=[-11,-9,9,11]
CS={97:(96,98),93:(94,91),27:(26,28),23:(24,21)}
def post(p,b):
 with U.urlopen(U.Request(E+p,json.dumps(b).encode(),{'content-type':'application/json'})) as r:return json.load(r)
def u2s(s):return(8-int(s[1]))*10+ord(s[0])-76
def board(f):
 b=[' ']*120;r=c=0
 for ch in f.split()[0]:
  if ch=='/':r+=1;c=0
  elif ch.isdigit():
   for _ in range(int(ch)):b[21+r*10+c]='.';c+=1
  else:b[21+r*10+c]=ch;c+=1
 return b
def att(b,q,w):
 pw,rq,bq=('P','RQ','BQ') if w else ('p','rq','bq')
 if b[q+(9 if w else -9)]==pw or b[q+(11 if w else -11)]==pw:return 1
 for d in N:
  if b[q+d]==('N' if w else 'n'):return 1
 for d in K:
  if b[q+d]==('K' if w else 'k'):return 1
 for dirs,pcs in((R,rq),(B,bq)):
  for d in dirs:
   t=q+d
   while b[t]=='.':t+=d
   if b[t] in pcs:return 1
 return 0
def gen(b,w,caps=False):
 m=[];d=-10 if w else 10;opp=(lambda p:p.islower()) if w else (lambda p:p.isupper())
 for q in range(21,99):
  p=b[q]
  if p in' .'or(w!=p.isupper()):continue
  up=p.upper()
  if up=='P':
   if not caps:
    if b[q+d]=='.':
     if(w and q+d<=28)or(not w and q+d>=91):
      for pr in'qrbn':m.append((q,q+d,pr,0))
     else:
      m.append((q,q+d,'',0))
      if((w and 81<=q<=88)or(not w and 31<=q<=38))and b[q+2*d]=='.':m.append((q,q+2*d,'',0))
   for cd in(-1,1):
    t=q+d+cd
    if b[t] not in' .'and opp(b[t]):
     vic=V[b[t].upper()]
     if(w and t<=28)or(not w and t>=91):
      for pr in'qrbn':m.append((q,t,pr,10000+vic*10-100))
     else:m.append((q,t,'',10000+vic*10-100))
  elif up in'NK':
   for delta in(N if up=='N' else K):
    t=q+delta
    if b[t]!=' 'and opp(b[t]):m.append((q,t,'',10000+V[b[t].upper()]*10-V[up]))
    elif not caps and b[t]=='.':m.append((q,t,'',0))
  else:
   dirs=R if up=='R' else(B if up=='B' else K)
   for delta in dirs:
    t=q+delta
    while b[t]=='.':
     if not caps:m.append((q,t,'',0))
     t+=delta
    if b[t]!=' 'and opp(b[t]):m.append((q,t,'',10000+V[b[t].upper()]*10-V[up]))
 leg=[]
 m.sort(key=lambda x:x[3],reverse=True)
 for f,t,pr,sc in m:
  sf,st=b[f],b[t]
  b[t]=(pr.upper() if w else pr) if pr else sf
  b[f]='.'
  if not att(b,b.index('Kk'[not w]),not w):leg.append((f,t,pr,sc))
  b[f],b[t]=sf,st
 return leg
def ev(b):
 s=0
 for q in range(21,99):
  p=b[q]
  if p in' .':continue
  up=p.upper();r,c=(q-21)//10,(q-21)%10;bn=0
  if up=='P':
   bn=(6-r)*3 if p.isupper() else (r-1)*3
   if 2<=c<=5 and 3<=r<=4:bn+=10
  elif up in'NB':bn=(7-abs(2*c-7)-abs(2*r-7))*2
  elif up=='R' and((p.isupper() and r==1)or(p.islower() and r==6)):bn=20
  elif up=='K' and r in(0,7) and c in(1,2,6):bn=10
  s+=(V[up]+bn) if p.isupper() else -(V[up]+bn)
 return s
def ab(b,w,d,a,beta):
 if d<=0:
  sp=ev(b) if w else -ev(b)
  if sp>=beta:return beta
  if sp>a:a=sp
  if d<0:return a
 moves=gen(b,w,caps=(d<=0))
 if not moves:
  if d<=0:return a
  if att(b,b.index('Kk'[not w]),not w):return -90000-d
  return 0
 for f,t,pr,_ in moves:
  sf,st=b[f],b[t]
  b[t]=(pr.upper() if w else pr) if pr else sf
  b[f]='.'
  sc=-ab(b,not w,d-1,-beta,-a)
  b[f],b[t]=sf,st
  if sc>=beta:return beta
  if sc>a:a=sc
 return a
def choose(fen,legal):
 b=board(fen);w=fen.split()[1]=='w';best_m=legal[0];best_s=-1e9
 def rk(m):
  t=u2s(m[2:4])
  return (10000+V[b[t].upper()]*10-V[b[u2s(m[:2])].upper()]) if b[t] not in' .' else 0
 a,beta=-1000000,1000000
 for m in sorted(legal,key=rk,reverse=True):
  f,t=u2s(m[:2]),u2s(m[2:4]);pr=m[4:] if len(m)==5 else ''
  sf,st=b[f],b[t]
  b[t]=(pr.upper() if w else pr) if pr else sf
  b[f]='.'
  is_c=sf in'Kk' and abs(f-t)==2 and t in CS
  if is_c:r1,r2=CS[t];b[r1],b[r2]=b[r2],'.'
  sc=-ab(b,not w,3,-beta,-a)
  b[f],b[t]=sf,st
  if is_c:b[r2],b[r1]=b[r1],'.'
  if sc>best_s:best_s=sc;best_m=m
  if sc>a:a=sc
 return best_m
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':
  g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
