import os, sys, json, urllib.request as U
E = os.environ.get('MAKEFUN_ENV_URL') or sys.exit(1)
V = {'P':100, 'N':320, 'B':330, 'R':500, 'Q':900, 'K':20000}
N = [-21, -19, -12, -8, 8, 12, 19, 21]
K = [-11, -10, -9, -1, 1, 9, 10, 11]
R = [-10, 10, -1, 1]
B = [-11, -9, 9, 11]
def post(p, b):
  req = U.Request(E + p, json.dumps(b).encode(), {'content-type':'application/json'})
  with U.urlopen(req) as res: return json.load(res)
def u2s(s): return 21 + (8 - int(s[1])) * 10 + (ord(s[0]) - 97)
def s2u(sq): return chr(97 + (sq - 21) % 10) + str(8 - (sq - 21) // 10)
def board(fen):
  b = [' '] * 120
  r = c = 0
  for ch in fen.split()[0]:
    if ch == '/': r += 1; c = 0
    elif ch.isdigit():
      for _ in range(int(ch)): b[21 + r*10 + c] = '.'; c += 1
    else: b[21 + r*10 + c] = ch; c += 1
  return b
def att(b, sq, w):
  pw, rq, bq = ('P', 'RQ', 'BQ') if w else ('p', 'rq', 'bq')
  if b[sq + (9 if w else -9)] == pw or b[sq + (11 if w else -11)] == pw: return 1
  kn, kk = ('N', 'K') if w else ('n', 'k')
  for d in N:
    if b[sq + d] == kn: return 1
  for d in K:
    if b[sq + d] == kk: return 1
  for d in R:
    t = sq + d
    while b[t] == '.': t += d
    if b[t] in rq: return 1
  for d in B:
    t = sq + d
    while b[t] == '.': t += d
    if b[t] in bq: return 1
  return 0
def gen(b, w):
  m = []
  d = -10 if w else 10
  opp = (lambda p: p.islower()) if w else (lambda p: p.isupper())
  for sq in range(21, 99):
    p = b[sq]
    if p in ' .' or (w != p.isupper()): continue
    up = p.upper()
    if up == 'P':
      if b[sq + d] == '.':
        if (w and sq + d <= 28) or (not w and sq + d >= 91):
          for pr in 'qrbn': m.append((sq, sq + d, pr))
        else:
          m.append((sq, sq + d, ''))
          if ((w and 81 <= sq <= 88) or (not w and 31 <= sq <= 38)) and b[sq + 2*d] == '.':
            m.append((sq, sq + 2*d, ''))
      for cd in (-1, 1):
        t = sq + d + cd
        if b[t] not in ' .' and opp(b[t]):
          if (w and t <= 28) or (not w and t >= 91):
            for pr in 'qrbn': m.append((sq, t, pr))
          else: m.append((sq, t, ''))
    elif up in 'NK':
      for delta in (N if up == 'N' else K):
        t = sq + delta
        if b[t] == '.' or (b[t] != ' ' and opp(b[t])): m.append((sq, t, ''))
    else:
      dirs = R if up == 'R' else (B if up == 'B' else K)
      for delta in dirs:
        t = sq + delta
        while b[t] == '.': m.append((sq, t, '')); t += delta
        if b[t] != ' ' and opp(b[t]): m.append((sq, t, ''))
  leg = []
  k = 'K' if w else 'k'
  for f, t, pr in m:
    sf, st = b[f], b[t]
    b[t] = pr.upper() if (w and pr) else (pr.lower() if pr else sf)
    b[f] = '.'
    if not att(b, b.index(k), not w): leg.append((f, t, pr))
    b[f], b[t] = sf, st
  return leg
def score(b):
  return sum(V[p] if p in V else -V[p.upper()] for p in b if p.upper() in V)
def ab(b, w, depth, alpha, beta):
  if depth == 0:
    s = score(b)
    return s if w else -s
  moves = gen(b, w)
  if not moves:
    k = 'K' if w else 'k'
    if att(b, b.index(k), not w): return -90000 - depth
    return 0
  for f, t, pr in moves:
    sf, st = b[f], b[t]
    b[t] = pr.upper() if (w and pr) else (pr.lower() if pr else sf)
    b[f] = '.'
    val = -ab(b, not w, depth - 1, -beta, -alpha)
    b[f], b[t] = sf, st
    if val >= beta: return beta
    if val > alpha: alpha = val
  return alpha
def choose(fen, legal):
  b = board(fen)
  w = fen.split()[1] == 'w'
  best_m, best_s = legal[0], -1e9
  alpha, beta = -1e9, 1e9
  for m in legal:
    f, t = u2s(m[:2]), u2s(m[2:4])
    pr = m[4:] if len(m) == 5 else ''
    sf, st = b[f], b[t]
    b[t] = pr.upper() if (w and pr) else (pr.lower() if pr else sf)
    b[f] = '.'
    val = -ab(b, not w, 2, -beta, -alpha)
    b[f], b[t] = sf, st
    if val > best_s: best_s, best_m = val, m
    if val > alpha: alpha = val
  return best_m
while 1:
  g = post('/game', {})
  if g['status'] == 'done': break
  while g['status'] == 'your_move':
    g = post('/move', {'game': g['game'], 'move': choose(g['fen'], g['legal_moves'])})