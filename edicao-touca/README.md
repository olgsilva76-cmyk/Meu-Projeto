# Edição: "Uma curiosidade sobre mim" (a touca de cetim)

O bruto `insta_post_1793733245487.mp4` tem 3min21. Ele virou `edicao_final.mp4`, com **2min15**, em 720×1280 (a resolução original), 30 fps, H.264 e áudio AAC em **-14 LUFS**, que é o padrão do Reels/TikTok/Shorts.

## A ideia da edição

O conteúdo é um desabafo sério (carreira na internet → conversão → nova fase do perfil). Mas existe um personagem acidental no vídeo: **a touca de cetim**, que ele ajusta o tempo todo e comenta ("Meu Deus, o que é isso, cara?", "tô parecendo o Megamente", "minha cabeça não aguenta o tamanho dessa touca"). A edição usa isso como **piada recorrente** e preserva a mensagem séria.

- O trecho em que ele luta com a touca (11 s) fica **acelerado 4x**, com a voz em tom agudo e baixa, e termina em **"Pronto, deixa assim."** com um "tchan".

## Estilo (seguindo o vídeo de referência)

- **Legendas:** Ronzino Bold (Collletttivo, licença SIL OFL, ver `fontes/OFL-Ronzino.txt`), **toda branca**, pequena, com contorno fino. Mostra de 1 a 3 palavras por vez, **sem animação**: o trecho fica fixo e troca direto para o próximo trecho falado. Fica no meio-baixo da tela, dentro da área segura.
- **"Várias câmeras":** em cada trecho, o plano alterna entre aberto e **close no rosto** nas trocas de frase (a cada ~1,5 s). O rosto é rastreado quadro a quadro, então o close acompanha o movimento.
- **Câmera viva:** cada enquadramento vai se aproximando devagar, sem nunca ficar parado.
- **Humor:** zooms rápidos nas reações, "boing", grilos na pausa, tremida, trecho acelerado com voz fininha e um "postar" em zoom crescente no final.
- **Sem** títulos grandes, emojis, contador ou cartão final.

## Estrutura

| Saída | O que acontece |
|-------|----------------|
| 0:00–0:03 | **Gancho:** "Eu já alcancei mais de 600 mil pessoas" |
| 0:03 | Efeito de **rebobinar** (scratch) e volta para o começo |
| 0:03–0:15 | "Uma curiosidade sobre mim…" → reação à touca com **zoom rápido**, "boing", zoom em "Megamente", pausa cômica com grilos |
| 0:15–0:34 | 10 anos de internet, conversão, +600 mil, vida com Deus |
| 0:35–0:46 | "Tô colocando errado essa touca de cetim" → zoom → **acelerado 4x** → "Pronto, deixa assim" |
| 0:46–1:12 | "Só que tem um porém" (riser + tremida), vida artística, Canadá, os frutos, "por aqui" |
| 1:12–1:35 | Usar o que tem para glorificar a Deus, câmera, a decisão |
| 1:35–1:52 | +200 mil views, a treta, vergonha (tremida) |
| 1:52–2:10 | "Minha cabeça já não aguenta mais o tamanho dessa touca" (zoom + boing), novo foco do perfil |
| 2:10–2:17 | "postar, postar, postar…": **cada "postar" dá um zoom a mais**, scratch e fim |

## O que foi cortado (e por quê)

- **Silêncios e respirações:** removidos em todo o vídeo (jump cuts alternando plano aberto e fechado).
- **0:00–0:02,5:** ruído antes da primeira fala.
- **1:01–1:06:** "já consegui atingir mais de 100 mil pessoas" repetia a ideia dos 600 mil com outro número.
- **1:52–2:00:** hesitação repetindo "Deus falou sobre a questão… da questão do…".
- **2:07–2:11:** desvio ("não lembro se… acho que tá falando sobre isso").
- **2:28:** "E deixar…", uma frase abandonada.
- Os finais "Então…" que não levavam a nada.

Nenhuma fala foi inventada ou reordenada fora do gancho. O gancho repete a frase dos 600 mil, que aparece de novo no lugar original.

## Música e efeitos

Tudo foi **sintetizado do zero** por `scripts/sons.py`, sem direitos de terceiros:
- **Música:** groove lo-fi/funk leve a 100 BPM, que abaixa automaticamente quando ele fala (sidechain) e quase some nas pausas cômicas.
- **Efeitos:** whoosh, pop, ding, boing, punch, scratch, grilos, "tchan" e riser.

A voz passa por passa-altas, redução de ruído, compressor e um leve brilho em 3,2 kHz.

## ⚠️ Confira estas legendas

A transcrição foi feita por reconhecimento automático (Whisper) e revisada pelo contexto. Estes trechos estavam pouco claros no áudio, então vale você ouvir e corrigir em `transcricao_revisada.json`:

| Bruto | Legenda usada | Dúvida |
|-------|---------------|--------|
| 0:13 | "Tá, pô, tô parecendo o Megamente." | o reconhecimento ouviu "mega-a-mente" |
| 0:46 | "essa touca de cetim aqui" | ouviu "esse toco de sentimento" |
| 2:17 | "E eu sei gravar vídeo," | ouviu "Eu se grava a vídeo" |
| 2:35 | "Os meus seguidores de uma conta antiga." | ouviu "O tio é meu seguidor…" |
| 2:39 | "mais de 200 mil views" | ouviu "200 mil vídeos" |
| 2:43 | "alguma treta que eu acabei presenciando" | ouviu "prestando" |
| 3:00 | "o tamanho dessa touca aqui" | ouviu "castaba/castauga" |

## Como refazer / ajustar

```bash
# 1) sons (música + efeitos)
python3 scripts/sons.py sons 200
# 2) transcrição (precisa do modelo sherpa-onnx-whisper-small)
python3 scripts/transcrever.py BRUTO.mp4 MODELO transcricao.json
# 3) depois de revisar transcricao_revisada.json, alinha as palavras
python3 scripts/alinhar.py BRUTO.mp4 transcricao_revisada.json palavras.json
# 4) edição completa
python3 scripts/editar.py BRUTO.mp4 palavras.json sons edicao_final.mp4
#    só alguns quadros para conferir:   --quadros 9.2,40,117
#    mapa bruto → final:                --mapa
```

- **Cortes, zooms e efeitos:** `plano.py` (todos os tempos são do vídeo bruto).
- **Fonte, tamanho e posição da legenda:** `scripts/editar.py` (`FONT_BLACK`, `caption_sprite`, `CAPTION_Y`).
- **Intensidade do close:** `REFRAME_CLOSE` em `scripts/editar.py`.

Dependências: `ffmpeg`, Python com `numpy`, `scipy`, `pillow`, `opencv-python-headless<5` e `sherpa-onnx`.
