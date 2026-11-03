# Desmontagem das 3 edições (referência para replicar)

Formato comum aos três: **vertical 720×1280 (9:16), 30 fps, áudio estéreo 44,1 kHz, volume final em ~-14 LUFS** (o padrão do Instagram/Reels). Nenhum dos três tem silêncio de mais de 0,3 s: a fala e a trilha não param nunca, e isso segura a retenção.

Os quadros de referência com a minutagem estão em [`referencias/`](referencias/).

| # | Arquivo | Duração | Estilo | Dificuldade |
|---|---------|---------|--------|-------------|
| 1 | `insta_post_1793728194945.mp4` | 35 s | Motion design 3D / anúncio de produto (EditClass) | Alta (After Effects/Blender) |
| 2 | `insta_post_1793726987538.MP4` | 85 s | UGC / review falado com muitos cortes | Baixa (CapCut) |
| 3 | `insta_post_1793728371639.mp4` | 52 s | Talking head cinematográfico em letterbox + legenda tipográfica | Média (CapCut/Premiere) |

---

## Vídeo 1: motion design "EditClass" (35 s)

Não tem filmagem de câmera até os 18 s. É tudo **motion graphics em 2,5D/3D** sincronizado com uma narração. A paleta é **creme/pêssego (claro) ↔ preto com dourado/âmbar (escuro)**, com glow, vidro fosco (glassmorphism) e desfoque de movimento forte.

### Linha do tempo

| Tempo | Cena | O que acontece | Técnica |
|-------|------|----------------|---------|
| 0:00–0:01,5 | **Barra de busca** | Fundo creme com gradiente suave. Aparece "Esse", o cursor clica, o texto "Esse é o estilo" é digitado numa pílula branca e um botão laranja com seta (↑) é clicado | Typewriter + cursor animado + pílula com sombra suave |
| 0:01,5–0:02,2 | **"Motion"** | A palavra entra grande, com motion blur e uma estrela dourada girando | Escala/posição com motion blur, partícula de estrela |
| 0:02,2 | **Corte: claro → escuro** | Transição para o fundo preto com ondas âmbar | Corte seco no beat (o primeiro grande corte da detecção de cenas) |
| 0:02,5–0:03,5 | "um formato **criado**" | A palavra-chave fica dourada e sublinhada, com uma estrela ⭐ | Destaque de palavra-chave por cor |
| 0:03,5–0:04,5 | **"Ideias"** | 3 esferas de vidro com lâmpadas douradas + uma pílula "Ideias" | Objetos 3D em vidro, pop-in escalonado |
| 0:05–0:05,5 | **Celular** | Um iPhone 3D gira mostrando notificações de "Venda Aprovada" + pílula "Vídeo" | Mockup 3D rotacionando, whip/blur |
| 0:06–0:07 | "**sem** precisar aparecer" | Palavra por palavra; um ícone de avatar com "?" passa na frente | Kinetic typography + objeto 3D atravessando |
| 0:07,5–0:09 | **Logo "EditClass"** | Pílula escura com borda de LEDs coloridos (efeito RGB) e o texto "chamamos isso de:" | Stroke animado + glow, zoom in |
| 0:09,5–0:10 | "**Copy** Visual" | Volta ao fundo claro; a palavra vira um botão 3D, com uma seta/cursor dourado | Transição de cor do fundo, texto → botão |
| 0:10,5–0:12 | **"eu quero um Motion"** | Campo de prompt escuro sendo digitado, com moedas ($, câmera, &) caindo em 3D | Typewriter + moedas 3D com física |
| 0:12–0:17 | **Hub "&"** | Botão circular dourado com "&" no centro, as pílulas Premium / Rapidez / Motion / EditClass / Retenção orbitam e saem; depois um balão de chat aparece | Giro de câmera 3D, painéis que se abrem como portas, órbita |
| 0:18–0:24 | **Pôster surreal** (filmagem) | Pessoa de moletom laranja num fundo bege; banana escrita "COMPREENSÃO", olho com "DESEJO", notas de dólar voando, nota "EXCELENTES" tapando os olhos; título manuscrito "O Objetivo não é enfeitar o vídeo" | Recorte (rotoscopia) + elementos 3D/colagem, parallax, câmera descendo |
| 0:24–0:28 | **Semáforo** | Céu azul com nuvens; o semáforo acende PRODUTO (vermelho) → SERVIÇO (amarelo) → IDEIA (verde), depois os três viram "&" | Objeto 3D com troca de textura/emissão |
| 0:28–0:31 | **"CENÁRIO PERFEITO"** | Câmera atravessa as nuvens e revela o pôster tipográfico, com um carro laranja e notas voando | Push-in através das nuvens (transição por máscara), tipografia condensada gigante |
| 0:31–0:35 | **CTA / vitrine** | Fundo escuro, abas "01 Avatar · 02 Motion · 03 EditClass", carrossel 3D de exemplos e botão dourado "QUERO ESSE ESTILO", com o cursor clicando | Carrossel 3D com reflexo no chão, botão de CTA |

### Receita para replicar

1. **Roteiro primeiro.** Grave a narração (≈ 2,5 palavras/s) e marque as palavras-chave: elas viram os objetos (Ideias → lâmpada, vendas → celular, rapidez → pílula…).
2. **Duas "salas" de cor.** Monte dois fundos: (a) creme `#F5E6D8` → pêssego `#F3C9A0` e (b) preto `#0B0805` → âmbar `#C98A2E`, com formas onduladas desfocadas. Alterne entre eles a cada mudança de ideia.
3. **Kit de componentes reutilizáveis:** pílula de vidro (retângulo arredondado + desfoque de fundo + borda 1 px clara + sombra), botão dourado, campo de prompt com cursor piscando, esfera de vidro. Quase todas as cenas são esses quatro elementos.
4. **Ritmo:** troque algo na tela a cada **0,5–1 s**. Use motion blur ligado em tudo e easing "ease out" forte (entrada rápida, assentamento suave).
5. **Texto:** uma sans geométrica (estilo SF Pro / Inter / Manrope) para a UI, uma condensada pesada (estilo Bebas/Anton) para os títulos de pôster e uma script/serifada itálica para o "O Objetivo…".
6. **3D:** o celular, as moedas, o semáforo e o carrossel saem de Blender/Cinema 4D, ou de templates de mockup 3D no After Effects (Element 3D). As versões 2D com Deep Glow + Motion Tile já chegam perto.
7. **Finalização:** glow (Deep Glow), leve grão, vinheta e o CTA nos últimos 3–4 s, sempre com o cursor clicando no botão.

Ferramentas: **After Effects** (+ Deep Glow, Element 3D ou Blender para os objetos), e Photoshop para a colagem do pôster.

---

## Vídeo 2: UGC / review de cuidados com o cabelo (85 s)

Estilo "conversa com a amiga". A base é **uma câmera fixa no sofá (A-roll)**, intercalada com **B-roll do dia a dia e do produto**. São 30 cortes detectados em 85 s, **um corte a cada ~2,8 s**.

### Estrutura

| Tempo | Bloco | Conteúdo |
|-------|-------|----------|
| 0:00–0:08 | **Gancho** | A-roll no sofá penteando o cabelo com um pente de madeira + B-roll mexendo no cabelo, já com legenda palavra por palavra |
| 0:08–0:20 | **Prova social** | Close do celular com comentários/DMs perguntando do cabelo (tela preta com os comentários), pessoa lendo o celular, mais A-roll |
| 0:20–0:30 | **Contexto/rotina** | B-roll: podcast (outra roupa e local), cozinha, pia, tomando suplemento |
| 0:30–0:46 | **Desenvolvimento** | A-roll longo falando ("por mais que…", "com os elogios…", "saber o segredo…", "nunca respondi…") |
| 0:46–0:50 | **Revelação** | Unboxing da caixa (luz estourada vindo da caixa = momento "mágico") |
| 0:50–0:72 | **Produto em uso** | Macro do sérum com conta-gotas, aplicação no couro cabeludo, frasco do creme Pantene, aplicação no espelho, cabelo brilhando em câmera lenta |
| 0:72–0:85 | **Fechamento + CTA** | A-roll com os stickers "**Biotina**" e "**Vitamina**" (texto branco com contorno preto, inclinado ±15°, que estala na tela), segura o produto e encerra |

### Receita para replicar (CapCut)

1. **Grave o A-roll inteiro de uma vez**, celular no tripé, luz da janela, enquadramento do joelho para cima, falando como num desabafo.
2. **Lista de B-roll:** mãos no cabelo, celular com os comentários (grave a tela ou filme o celular), cozinha/rotina, unboxing, macro do produto, aplicação e o cabelo "resultado" com o brilho em slow motion.
3. **Corte "jump cut"** tirando todas as respirações. Troque para o B-roll sempre que a fala citar algo visual (ex.: falou "comentário" → mostra o celular).
4. **Legenda automática** do CapCut: **uma palavra por vez**, fonte sans branca pequena (~5 % da largura), sem caixa, centralizada na altura do peito (≈ 60 % da tela). Discreta de propósito, para parecer orgânico.
5. **Stickers de palavra-chave** (Biotina/Vitamina): texto bold branco com contorno preto, rotacionado, animação "pop" (escala 0 → 110 % → 100 % em 0,2 s), um de cada lado do rosto.
6. **Cor:** quente e natural, sem LUT pesado. Só um pouco de calor e contraste.
7. **Áudio:** a voz é o protagonista, com uma trilha bem baixa por baixo (~-25 dB) e o volume normalizado em -14 LUFS.

---

## Vídeo 3: talking head cinematográfico (52 s)

É **um plano único**, sem nenhum corte detectado: a pessoa fala dentro do carro, à noite. A edição inteira está em **3 coisas: o letterbox, a cor e a legenda tipográfica**.

### Elementos

| Elemento | Detalhe medido |
|----------|----------------|
| **Letterbox** | O vídeo ocupa só uma faixa de **720×432 px centralizada (y = 424)**; o resto do 9:16 é preto puro. Proporção da faixa ≈ **1,67:1** (look de cinema dentro do Reels) |
| **Cor** | Teal & orange forte: a janela/fundo fica **ciano-esverdeado saturado**, os pretos são esmagados e a pele fica quente. Grão leve |
| **Legenda** | Branca, sans grotesca (estilo Helvetica Neue / SF Pro), colocada **sobre a janela à direita do rosto** (nunca em cima dele) |
| **Hierarquia tipográfica** | Cada frase tem 2–3 linhas com pesos diferentes: palavras de ligação em **Regular pequeno**, palavras emocionais em *Itálico leve*, palavra-chave em **Black/Bold grande** (ex.: "Se você *tem um* **negócio**", "Você tem um *emprego* **turbinado.**", "*a criatura* fica maior que o **Criador**") |
| **Animação do texto** | Entra palavra por palavra, sincronizada com a fala; a frase se acumula e depois é trocada inteira. Sem caixa de fundo, só uma sombra suave |
| **Áudio** | Voz contínua + trilha ambiente baixa |

### Linha do roteiro (lida nas legendas)

"Se você tem um negócio que depende de você, você não tem um negócio. Você tem um emprego turbinado, só não entendeu isso ainda. Para que você tenha um negócio de verdade, você precisa, no longo [prazo], ser substituível… se transformar… [no] que mais importante… formar pessoas e aprender a colocá-las… Só que, além disso, você vai formando… vai demitindo e vai promovendo… vai ficando… vá tirando aquilo que você… E a mágica acontece, em algum momento várias pessoas… E é nesse momento que a criatura fica maior que o Criador… um negócio de verdade… nos dias 29… teremos a primeira… onde os maiores… para ensinar… cada vez mais sólido."

Estrutura: **frase polêmica de gancho (0–5 s) → explicação → virada ("a criatura fica maior que o Criador") → CTA do evento (últimos ~10 s)**.

### Receita para replicar

1. Grave na horizontal (ou na vertical com espaço sobrando) à noite, dentro do carro, com a janela atrás e a luz do painel/rua batendo no rosto.
2. No CapCut/Premiere, crie a sequência 1080×1920, coloque o vídeo ocupando uma faixa de **~650 px de altura no centro** (equivalente a 432 px em 720p) e deixe o resto preto.
3. Cor: abaixe o contraste das sombras até o preto, empurre os meio-tons/realces frios para o **ciano (hue ~175°)**, proteja a pele (máscara HSL) e acrescente grão.
4. Legenda: **escreva a mão, frase por frase** (a legenda automática não faz a hierarquia). Use 3 estilos salvos como predefinição: `Regular 40px`, `Italic Light 44px`, `Black 64px`. Alinhe tudo dentro da área da janela.
5. Faça cada palavra entrar no exato momento em que é falada (fade + subida de 10 px em 3–4 frames).

### Atalho em ffmpeg (base de letterbox + cor)

```bash
# entrada: vídeo bruto vertical; saída: faixa cinematográfica + teal & orange
ffmpeg -i bruto.mp4 -vf "\
scale=720:-2,crop=720:432,\
eq=contrast=1.15:brightness=-0.03:saturation=1.2,\
colorbalance=rs=-0.08:gs=0.02:bs=0.10:rh=0.05:bh=-0.05,\
noise=alls=6:allf=t,\
pad=720:1280:0:424:black" \
-c:a aac -af loudnorm=I=-14 saida.mp4
```

As legendas tipográficas ficam melhores feitas no editor (CapCut/Premiere) por cima desse resultado.

---

## Resumo: o que os três têm em comum

1. **Gancho nos primeiros 2 s**: uma pergunta/afirmação na tela já no primeiro frame.
2. **Algo muda na tela a cada 0,5–3 s** (corte, palavra nova ou objeto novo).
3. **Legenda sempre presente**, com a palavra-chave destacada (cor no V1, sticker no V2, peso/tamanho no V3).
4. **Áudio sem buracos**, finalizado em -14 LUFS.
5. **CTA no fim** (botão "Quero esse estilo", produto na mão ou anúncio do evento).

> Observação: a transcrição exata do áudio não foi possível neste ambiente (o download do modelo de reconhecimento de fala foi bloqueado pela rede), então os textos acima foram lidos das legendas na tela. Trechos entre colchetes são inferidos.
