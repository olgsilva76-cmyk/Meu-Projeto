# Recriação do estilo do Vídeo 1 (motion design creme/preto e dourado)

Vídeo **original** que usa a mesma linguagem de edição do Vídeo 1 da [desmontagem](../desmontagem-edicoes/README.md). A marca ("Faísca"), o roteiro, os elementos visuais e a trilha foram todos criados do zero. Nada foi copiado do vídeo de referência.

- **Resultado:** `faisca_motion.mp4`, com 720×1280, 30 fps, 26 s e áudio em -14 LUFS.
- **Animação:** `animacao.html`. Cada cena é um bloco HTML/CSS, e a função `render(t)` desenha o quadro de cada instante.
- **Renderização:** `renderizar.js` abre a página no Chromium (Playwright), tira um print por quadro e envia tudo ao ffmpeg.
- **Trilha:** `trilha.py` faz uma síntese em Python/numpy com pad, baixo, bateria a 120 BPM, whoosh nos cortes, cliques e tiques de digitação.

## Roteiro / linha do tempo

| Tempo | Fundo | Cena |
|-------|-------|------|
| 0,0–2,4 s | claro | Barra de busca digitando "Seu vídeo merece mais"; o cursor clica no botão laranja |
| 2,4–4,0 s | claro | "Movimento" entra com desfoque de movimento e uma estrela orbitando |
| 4,0–6,0 s | escuro | "uma ideia **vira** imagem": palavra por palavra, com "vira" dourada e sublinhado se desenhando |
| 6,0–8,0 s | escuro | 3 esferas de vidro com lâmpadas + pílula "Ideias"; as esferas se juntam no centro |
| 8,0–10,4 s | escuro | Celular 3D girando com notificações de "Novo pedido" + pílula "Vendas"; sai em chicote |
| 10,4–12,2 s | escuro | "sem **complicar** nada" + esfera "?" atravessando |
| 12,2–14,6 s | escuro | "a gente chama isso de:" + logo "Faísca" com borda de LED arco-íris girando |
| 14,6–17,6 s | claro | Botão 3D "Roteiro Visual" → campo de prompt "quero um vídeo assim" + moedas caindo |
| 17,6–21,2 s | escuro | Portas se abrem, hub dourado ✦ com pílulas orbitando (Clareza, Ritmo, Retenção…) + balão de resultado |
| 21,2–26,0 s | escuro | CTA: @faisca.motion, abas 01 Ideia / 02 Motion / 03 Entrega, carrossel 3D com reflexo, botão "QUERO ESSE ESTILO" clicado |

Há um flash curto a cada corte, grão de filme e vinheta por cima de tudo.

## Como gerar de novo

```bash
cd recriacao-video1
node renderizar.js video_sem_audio.mp4      # ~780 quadros
python3 trilha.py trilha.wav
ffmpeg -i video_sem_audio.mp4 -i trilha.wav -c:v copy -c:a aac -b:a 192k \
  -af loudnorm=I=-14:TP=-1 -shortest faisca_motion.mp4
```

Para ver só alguns quadros: `node renderizar.js --preview 1.2 5 9.6` (salva `preview_*.png`).

## Como personalizar

- **Textos:** procure por "Seu vídeo merece mais", "Movimento", "Faísca", "@faisca.motion" e "QUERO ESSE ESTILO" no `animacao.html`.
- **Tempos:** o objeto `SC` define a janela de cada cena, e `CUTS` define os cortes (com os mesmos tempos na `trilha.py`).
- **Cores:** `#bgLight`, `#bgDark` e a classe `.gold`.
- **Narração:** grave a sua voz por cima e ajuste os tempos de `SC` para cada palavra-chave cair no corte.
