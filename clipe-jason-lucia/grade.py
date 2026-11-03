"""Gera a grade de sincronia do clipe a partir da análise da música.

Saídas: letra.srt (cada verso com timecode), marcadores.csv (batidas, compassos e seções
para importar como marcadores no Premiere/DaVinci) e imprime a tabela das seções.
Uso: python3 grade.py beats.json
"""
import csv, json, sys

beats = json.load(open(sys.argv[1]))["beats"]
BPM = 143.55
BEAT = 60 / BPM
BAR = 4 * BEAT
FIM = 186.92

def snap(t):
    return min(beats, key=lambda b: abs(b - t))

# (nome, início aproximado medido no áudio, nº de versos, letra cantada)
SECOES = [
    ("Intro", 0.19, 4), ("Verso 1", 13.5, 8), ("Refrão 1", 40.9, 4), ("Verso 2", 54.4, 8),
    ("Respiro (beat cai)", 80.4, 0), ("Refrão 2", 82.2, 4), ("Ponte", 95.6, 4), ("Verso 3", 108.9, 8),
    ("Refrão final", 135.5, 5), ("Outro (voz)", 164.6, 2), ("Final instrumental", 171.4, 0), ("Fade", 183.4, 0),
]
LETRA = open("letra.txt", encoding="utf-8").read().split("\n")
LETRA = [l.strip() for l in LETRA if l.strip() and not l.startswith("[")]

def tc(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"

def srt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"

linhas, li = [], 0
for i, (nome, ini, n) in enumerate(SECOES):
    start = snap(ini)
    fim = snap(SECOES[i + 1][1]) if i + 1 < len(SECOES) else FIM
    for k in range(n):
        a = start + k * 2 * BAR
        b = min(a + 2 * BAR, fim)
        if k == n - 1 and nome == "Refrão final":
            b = fim  # último verso segura até o outro
        linhas.append((a, b, LETRA[li], nome)); li += 1
    print(f"{tc(start):>8} – {tc(fim):>8}  {nome}  ({(fim - start) / BAR:.1f} compassos)")

with open("letra.srt", "w", encoding="utf-8") as f:
    for i, (a, b, txt, _) in enumerate(linhas, 1):
        f.write(f"{i}\n{srt(a)} --> {srt(b - 0.05)}\n{txt}\n\n")

with open("marcadores.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["tempo_s", "timecode", "tipo", "nome"])
    for nome, ini, _ in SECOES:
        w.writerow([f"{snap(ini):.3f}", tc(snap(ini)), "secao", nome])
    for i, b in enumerate(beats):
        w.writerow([f"{b:.3f}", tc(b), "compasso" if i % 4 == 0 else "batida", f"{i // 4 + 1}.{i % 4 + 1}"])
print(f"{len(linhas)} versos no SRT; {len(beats)} batidas")
