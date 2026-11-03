"""Plano de edição: todos os tempos são do vídeo BRUTO (segundos).

O motor (scripts/editar.py) converte para a linha do tempo final.
Para ajustar a edição, mexa só aqui.
"""

# ------------------------------------------------------------------
# CLIPES (na ordem em que aparecem no vídeo final)
#   s, e      trecho do bruto
#   z         zoom base (1.0 = plano aberto; ~1.15 = "punch-in" de jump cut)
#   z2        zoom no fim do clipe (zoom lento entre z e z2)
#   speed     velocidade (4 = acelerado 4x, -6 = rebobinando)
#   enter     transição de entrada: "whip" (zoom com desfoque) | "flash"
#   hold      segundos congelando o último quadro (pausa cômica)
# ------------------------------------------------------------------
CLIPS = [
    # GANCHO: começa no número mais forte, depois "rebobina" para o início
    dict(s=29.45, e=32.42, z=1.18, z2=1.30),
    dict(s=29.60, e=32.40, speed=-7, tag="rewind"),

    dict(s=2.55, e=4.90, z=1.0, enter="flash"),             # Uma curiosidade sobre mim que...
    dict(s=5.40, e=7.15, z=1.14),                            # eu não cheguei a contar muito, né?
    dict(s=8.08, e=9.12, z=1.0),                             # pras pessoas,
    dict(s=9.65, e=12.98, z=1.0),                            # é que... Meu Deus, o que é isso, cara?
    dict(s=13.25, e=16.05, z=1.12, hold=0.55),               # Tá, pô, tô parecendo o Megamente. Enfim. (+ grilos)
    dict(s=17.35, e=21.37, z=1.0, enter="whip"),             # Eu já consegui alcançar muitos números...
    dict(s=22.03, e=22.66, z=1.15),                          # Tipo,
    dict(s=23.15, e=26.02, z=1.15, z2=1.22),                 # 10 anos de trajetória
    dict(s=26.50, e=29.08, z=1.0),                           # mas depois que eu me converti...
    dict(s=29.45, e=33.72, z=1.14),                          # Eu já alcancei mais de 600 mil pessoas com vídeo mundano.
    dict(s=33.70, e=38.10, z=1.0, z2=1.08),                  # Daí eu decidi seguir a minha vida com Deus...
    dict(s=39.28, e=40.36, z=1.14),                          # Porque
    dict(s=40.70, e=44.25, z=1.0),                           # não era o caminho, não era o propósito...
    dict(s=44.25, e=47.40, z=1.16),                          # Eu acho que eu tô colocando errado essa touca de cetim aqui.
    dict(s=47.40, e=58.70, speed=4, tag="fast"),             # (lutando com a touca: acelerado)
    dict(s=58.75, e=60.25, z=1.0, hold=0.25),                # Pronto, deixa assim.
    # corte: 61.5–66.3 repete "já alcancei X mil pessoas" com outro número
    dict(s=67.88, e=68.85, z=1.0, z2=1.18, enter="whip"),    # Só que tem um porém.
    dict(s=70.96, e=73.50, z=1.0),                           # Era um caminho muito diferente...
    dict(s=74.23, e=76.52, z=1.14),                          # Porque eu queria seguir minha vida artística,
    dict(s=77.41, e=82.14, z=1.0),                           # seguir minha vida normal, pessoal...
    dict(s=84.14, e=87.84, z=1.12, enter="whip"),            # Deus falou comigo quando eu estava no Canadá...
    dict(s=90.54, e=92.22, z=1.0),                           # usar os frutos,
    dict(s=92.64, e=95.40, z=1.0),                           # sabe, que habitam em mim. Então...
    dict(s=96.45, e=98.50, z=1.15),                          # como é que eu vou espalhar o evangelho?
    dict(s=100.53, e=101.34, z=1.28),                        # Por aqui.
    dict(s=103.58, e=105.60, z=1.0),                         # Eu posso falar pela internet
    dict(s=108.88, e=111.24, z=1.12),                        # sobre os frutos que ele me deu, sabe?
    # corte: 112.7–120.3 hesitação repetindo "Deus falou sobre a questão"
    dict(s=121.64, e=123.66, z=1.0),                         # E é muito importante falar
    dict(s=124.17, e=127.32, z=1.13),                        # sobre a questão de eu usar o que eu tenho.
    # corte: 127.7–131.0 desvio ("não lembro se... acho que tá falando sobre isso")
    dict(s=131.61, e=135.42, z=1.0, z2=1.16),                # Mas eu tenho que usar o que eu tenho para glorificar a Deus.
    dict(s=136.62, e=137.55, z=1.14, enter="whip"),          # E eu sei gravar vídeo,
    dict(s=138.44, e=141.66, z=1.0),                         # sabe? E eu tô me desenvolvendo com a câmera ainda,
    dict(s=145.28, e=147.80, z=1.12),                        # Foi uma decisão que eu tinha que tomar.
    # corte: 148.1–149.2 "E deixar..." (frase abandonada)
    dict(s=149.63, e=154.85, z=1.0),                         # Tipo, eu poderia crescer aquela conta...
    dict(s=154.81, e=157.18, z=1.14),                        # Os meus seguidores de uma conta antiga.
    dict(s=158.29, e=165.10, z=1.0, enter="whip"),           # mais de 200 mil views... alguma treta
    dict(s=165.07, e=171.34, z=1.14),                        # eu não tenho orgulho... quero deixar pra lá
    dict(s=171.32, e=174.40, z=1.0, z2=1.12),                # eu tenho vergonha, tenho vergonha.
    dict(s=174.70, e=176.90, z=1.0),                         # Foi bom, mas não é pra mim, tá ligado?
    dict(s=176.87, e=181.15, z=1.12),                        # Minha cabeça já não aguenta mais o tamanho dessa touca aqui.
    dict(s=181.13, e=187.12, z=1.0, enter="whip"),           # Então, olha, é melhor eu falar sobre Deus...
    dict(s=188.03, e=190.77, z=1.14),                        # Fazer uns conteúdos aqui...
    dict(s=191.44, e=194.62, z=1.0),                         # Mas eu espero que, com o tempo, vá dando certo.
    dict(s=195.61, e=200.55, z=1.0, hold=2.2, tag="end"),    # postar, postar, postar até postar... não postar mais.
]

# ------------------------------------------------------------------
# PALAVRAS EM DESTAQUE NA LEGENDA
#   cor: "y" amarelo | "g" verde | "r" vermelho/rosa ; impact=True = entra com impacto
# ------------------------------------------------------------------
DESTAQUES = {
    "curiosidade": ("y", True), "Megamente.": ("g", True), "cara?": ("r", True),
    "números": ("y", False), "10": ("y", True), "anos": ("y", False), "converti,": ("g", False),
    "600": ("y", True), "mil": ("y", False), "Deus,": ("g", False), "Deus.": ("g", True), "Deus": ("g", False),
    "propósito": ("y", False), "touca": ("r", True), "cetim": ("r", False),
    "porém.": ("r", True), "artística,": ("y", False), "Canadá": ("y", True), "frutos,": ("g", False),
    "frutos": ("g", False), "evangelho?": ("g", True), "internet": ("y", False), "glorificar": ("y", True),
    "câmera": ("y", False), "decisão": ("y", True), "diferente.": ("r", False), "200": ("y", True),
    "views": ("y", False), "treta": ("r", True), "orgulho,": ("r", False), "vergonha,": ("r", True),
    "vergonha.": ("r", True), "cabeça": ("y", False), "aleatório.": ("r", False), "certo.": ("g", False),
    "postar,": ("y", True), "postar": ("y", True), "mais.": ("r", True), "Pronto,": ("g", True),
}

# palavras que não viram legenda (hesitações)
SEM_LEGENDA = {"..."}

# ------------------------------------------------------------------
# EFEITOS (tempo no bruto). Tipos:
#   punch  (t, zoom, dur)          zoom rápido que segura por dur s (None = até o fim do clipe)
#   shake  (t, dur, força)
#   emoji  (t, "🙏", dur, lado)     lado: "d" direita / "e" esquerda da cabeça
#   big    (t, "TEXTO", "sub", dur) grafismo grande no topo
#   touca  (t,)                     +1 no contador "ajustes na touca"
#   sfx    (t, nome, ganho_dB)
# ------------------------------------------------------------------
EFEITOS = [
    # "+600 MIL" aparece no gancho e de novo na hora da fala completa
    ("sfx", 30.65, "ding", -8),

    # "Meu Deus, o que é isso, cara?" — reação ao se ver de touca
    ("punch", 10.24, 1.38, None), ("sfx", 10.22, "punch", -4),
    ("sfx", 11.92, "boing", -9),
    ("touca", 10.3),
    ("emoji", 14.41, "🧠", 1.3, "d"), ("punch", 14.41, 1.22, None), ("sfx", 14.40, "pop", -6),
    ("sfx", 16.0, "grilo", -14),

    ("touca", 20.3),
    ("big", 24.15, "10 ANOS", "de internet", 1.8), ("sfx", 24.13, "pop", -6),
    ("emoji", 27.3, "✨", 1.2, "e"),
    ("big", 30.65, "+600 MIL", "pessoas alcançadas", 1.7),
    ("emoji", 36.1, "🙏", 1.4, "d"),

    # a touca de novo
    ("touca", 43.6),
    ("punch", 45.05, 1.30, None), ("sfx", 45.0, "punch", -5),
    ("touca", 49.0), ("touca", 51.4), ("touca", 53.8), ("touca", 56.2),
    ("sfx", 58.75, "tchan", -10), ("emoji", 58.9, "✅", 1.2, "d"),

    ("sfx", 66.9, "riser", -12),
    ("shake", 68.59, 0.35, 10), ("sfx", 68.55, "punch", -6),

    ("emoji", 86.3, "🇨🇦", 1.6, "d"), ("sfx", 86.3, "pop", -8),
    ("emoji", 91.2, "✨", 1.3, "e"),
    ("emoji", 100.6, "📱", 1.0, "d"), ("sfx", 100.6, "pop", -8),
    ("sfx", 134.0, "ding", -12), ("emoji", 135.1, "🙏", 1.2, "d"),
    ("emoji", 141.1, "🎥", 1.3, "e"),
    ("sfx", 145.75, "pop", -10),

    ("big", 159.7, "+200 MIL", "views", 1.6), ("sfx", 159.68, "pop", -6),
    ("emoji", 162.9, "🍿", 1.6, "d"), ("sfx", 162.88, "boing", -14),
    ("emoji", 173.0, "🫣", 1.5, "d"), ("shake", 173.03, 0.5, 7),

    ("touca", 177.1),
    ("punch", 179.7, 1.34, None), ("sfx", 179.66, "punch", -4), ("sfx", 180.8, "boing", -10),
    ("emoji", 183.3, "🙏", 1.2, "d"),

    # final: cada "postar" é um zoom a mais
    ("punch", 196.77, 1.08, None), ("sfx", 196.77, "pop", -10),
    ("punch", 197.42, 1.16, None), ("sfx", 197.42, "pop", -9),
    ("punch", 197.92, 1.24, None), ("sfx", 197.92, "pop", -8),
    ("punch", 198.86, 1.32, None), ("sfx", 198.86, "pop", -7),
    ("sfx", 199.5, "scratch", -9), ("emoji", 199.7, "😅", 1.6, "d"),
]

# texto do cartão final (sobre o quadro congelado)
CARTAO_FINAL = ("Segue pra acompanhar", "🙏")
