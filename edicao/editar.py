#!/usr/bin/env python3
"""Editor automático nos estilos A, B, C e D (veja GUIA_DE_ESTILO.md).

Uso:
  python3 edicao/editar.py ENTRADA.mp4 SAIDA.mp4 --estilo a [--srt legenda.srt]
         [--destaques "negócio,pessoas"] [--sem-cortar-silencio] [--sem-legenda]

O que faz:
  1. Corta os silêncios (jump cuts), como em todos os vídeos de referência.
  2. Reenquadra: 9:16 (A, C, D) ou 4:5 (B). No C coloca tarjas pretas + cor teal.
  3. Legenda no estilo escolhido. Transcreve sozinho com faster-whisper
     (se instalado e com internet para baixar o modelo) ou usa um .srt seu
     (tempos do .srt referentes ao vídeo ORIGINAL, antes dos cortes).
  4. Normaliza o áudio (~ -14 LUFS) e exporta H.264/AAC 30 fps.
Precisa de: ffmpeg (com libass).
"""
import argparse, os, re, subprocess, sys, tempfile

W = 1080
H = {"a": 1920, "b": 1350, "c": 1920, "d": 1920}
FONTE = "Inter"


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, **kw)


def duracao(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", path], capture_output=True).stdout
    return float(out.strip())


# ---------------------------------------------------------------- silêncio
def trechos_falados(path, limiar="-35dB", minimo=0.35, folga=0.08):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                          f"silencedetect=n={limiar}:d={minimo}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = duracao(path)
    fim += [total] * (len(ini) - len(fim))
    keep, cur = [], 0.0
    for s, e in zip(ini, fim):
        a, b = cur, min(s + folga, total)
        if b - a > 0.05:
            keep.append((a, b))
        cur = max(e - folga, 0)
    if total - cur > 0.05:
        keep.append((cur, total))
    return keep or [(0, total)]


def remapear(t, keep):
    """Tempo do vídeo original -> tempo no vídeo cortado (None se cortado)."""
    acc = 0.0
    for a, b in keep:
        if a <= t <= b:
            return acc + (t - a)
        if t < a:
            return acc  # caiu num silêncio: gruda no próximo trecho
        acc += b - a
    return acc


# ---------------------------------------------------------------- palavras
def palavras_whisper(audio):
    from faster_whisper import WhisperModel
    m = WhisperModel(os.environ.get("WHISPER_MODELO", "small"), device="cpu",
                     compute_type="int8")
    segs, _ = m.transcribe(audio, language="pt", word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]


def palavras_srt(path, keep):
    txt = open(path, encoding="utf-8-sig").read()
    blocos = re.findall(r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)\s*\n(.+?)(?:\n\s*\n|\Z)",
                        txt, re.S)

    def seg(ts):
        h, m, s = ts.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    out = []
    for a, b, texto in blocos:
        ws = texto.split()
        a, b = seg(a), seg(b)
        passo = (b - a) / max(len(ws), 1)
        for i, w in enumerate(ws):
            out.append((w, a + i * passo, a + (i + 1) * passo))
    if keep:
        out = [(w, remapear(s, keep), remapear(e, keep)) for w, s, e in out]
    return out


def blocos(palavras, maximo):
    """Agrupa palavras em blocos, quebrando em pontuação ou pausa."""
    grupos, atual = [], []
    for i, p in enumerate(palavras):
        atual.append(p)
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        quebra = (len(atual) >= maximo or re.search(r"[.,!?;:]$", p[0])
                  or (prox and prox[1] - p[2] > 0.4))
        if quebra:
            grupos.append(atual)
            atual = []
    if atual:
        grupos.append(atual)
    return grupos


# ---------------------------------------------------------------- ASS
def t_ass(t):
    t = max(t, 0)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def limpar(w):
    return w.replace("{", "").replace("}", "").replace("\\", "")


def gerar_ass(palavras, estilo, destaques, altura):
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {altura}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: A,{FONTE},48,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,0,2,5,40,40,0,1
Style: Sticker,{FONTE},86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,0,5,40,40,0,1
Style: B,{FONTE} SemiBold,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,0,3,5,60,60,0,1
Style: C,{FONTE},46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H50000000,0,0,0,0,100,100,0,0,1,0,1,4,0,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    dest = {d.lower() for d in destaques}

    if estilo == "a":
        for g in blocos(palavras, 2):
            texto = " ".join(limpar(w) for w, _, _ in g).lower()
            fim = g[-1][2] + 0.05
            ev.append(f"Dialogue: 0,{t_ass(g[0][1])},{t_ass(fim)},A,,0,0,0,,"
                      f"{{\\pos({W//2},{int(altura*0.50)})}}{texto}")
            for w, s, e in g:  # palavras-chave viram sticker girado
                if re.sub(r"\W", "", w.lower()) in dest:
                    ang = 12 if len(ev) % 2 else -12
                    x = int(W * (0.28 if len(ev) % 2 else 0.72))
                    ev.append(f"Dialogue: 1,{t_ass(s)},{t_ass(s+1.6)},Sticker,,0,0,0,,"
                              f"{{\\pos({x},{int(altura*0.62)})\\frz{ang}\\fscx40\\fscy40"
                              f"\\t(0,120,\\fscx100\\fscy100)}}{limpar(w).strip('.,!?')}")

    elif estilo == "b":
        for g in blocos(palavras, 5):
            texto = " ".join(limpar(w) for w, _, _ in g)
            texto = texto[:1].lower() + texto[1:]
            ev.append(f"Dialogue: 0,{t_ass(g[0][1])},{t_ass(g[-1][2]+0.05)},B,,0,0,0,,"
                      f"{{\\pos({W//2},{int(altura*0.60)})}}{texto}")

    elif estilo == "c":
        def fmt(w, i):
            chave = re.sub(r"\W", "", w.lower())
            if chave in dest or len(chave) >= 9:
                return f"{{\\fn{FONTE} Bold\\fs78\\i0}}{limpar(w)}{{\\r}}"
            if i % 5 == 3 and len(chave) >= 4:
                return f"{{\\fs58\\i1}}{limpar(w)}{{\\r}}"
            return limpar(w)
        y = int(altura * 0.50)
        for g in blocos(palavras, 4):
            partes = [fmt(w, i) for i, (w, _, _) in enumerate(g)]
            for i, (w, s, e) in enumerate(g):  # revela palavra por palavra
                fim = g[i + 1][1] if i + 1 < len(g) else g[-1][2] + 0.1
                # quebra de linha antes da palavra-chave grande
                linha = ""
                for j, p in enumerate(partes[: i + 1]):
                    linha += ("\\N" if "Bold" in p and j > 0 else (" " if j else "")) + p
                ev.append(f"Dialogue: 0,{t_ass(s)},{t_ass(fim)},C,,0,0,0,,"
                          f"{{\\an4\\pos({int(W*0.50)},{y})}}{linha}")
    return cab + "\n".join(ev) + "\n"


# ---------------------------------------------------------------- vídeo
def filtro_video(estilo, altura):
    if estilo == "c":  # faixa cinema 1080x640 no meio + teal
        return (f"scale={W}:640:force_original_aspect_ratio=increase,crop={W}:640:0:(ih-640)*0.3,"
                "colorbalance=rs=-0.08:gs=0.02:bs=0.10:rm=-0.05:bm=0.05,"
                "eq=contrast=0.95:saturation=0.9,"
                f"pad={W}:{altura}:0:(oh-ih)/2:black")
    base = (f"scale={W}:{altura}:force_original_aspect_ratio=increase,"
            f"crop={W}:{altura}")
    return base + ",eq=contrast=1.04:saturation=1.05"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--estilo", required=True, choices="abcd")
    ap.add_argument("--srt")
    ap.add_argument("--destaques", default="", help="palavras-chave separadas por vírgula")
    ap.add_argument("--sem-cortar-silencio", action="store_true")
    ap.add_argument("--sem-legenda", action="store_true")
    ap.add_argument("--limiar", default="-35dB")
    a = ap.parse_args()

    altura = H[a.estilo]
    tmp = tempfile.mkdtemp(prefix="edicao_")
    keep = None if a.sem_cortar_silencio else trechos_falados(a.entrada, a.limiar)

    vf = filtro_video(a.estilo, altura)
    af = "loudnorm=I=-14:TP=-1.5:LRA=11"
    if keep:
        sel = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in keep)
        vf = f"select='{sel}',setpts=N/FRAME_RATE/TB,fps=30," + vf
        af = f"aselect='{sel}',asetpts=N/SR/TB," + af
        cortado = sum(e - s for s, e in keep)
        print(f"Silêncios cortados: {duracao(a.entrada):.1f}s -> {cortado:.1f}s ({len(keep)} trechos)")

    legenda = not a.sem_legenda and a.estilo != "d"
    if legenda or a.estilo == "d" and a.srt:
        palavras = []
        if a.srt:
            palavras = palavras_srt(a.srt, keep)
        else:
            base = os.path.join(tmp, "base.mp4")
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.entrada, "-vf", vf,
                 "-af", af, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                 "-c:a", "aac", "-b:a", "192k", base])
            try:
                palavras = palavras_whisper(base)
            except Exception as e:  # sem whisper/sem internet
                print(f"AVISO: transcrição automática indisponível ({type(e).__name__}). "
                      "Use --srt para legendar. Exportando sem legenda.")
            if not palavras:
                os.replace(base, a.saida)
                print("Pronto:", a.saida)
                return
            ass = os.path.join(tmp, "leg.ass")
            open(ass, "w", encoding="utf-8").write(
                gerar_ass(palavras, a.estilo, a.destaques.split(","), altura))
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", base, "-vf",
                 f"ass={ass}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", a.saida])
            print("Pronto:", a.saida)
            return
        ass = os.path.join(tmp, "leg.ass")
        open(ass, "w", encoding="utf-8").write(
            gerar_ass(palavras, a.estilo, a.destaques.split(","), altura))
        vf += f",ass={ass}"

    run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.entrada, "-vf", vf, "-af", af,
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.saida])
    print("Pronto:", a.saida)


if __name__ == "__main__":
    main()
