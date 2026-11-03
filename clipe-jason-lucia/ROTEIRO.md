# Videoclipe "Jason e Lúcia": VAMORLI Music

Roteiro de direção e edição, sincronizado com a música real (`Gta6JasoneLucia.m4a`).

**Arquivos desta pasta**

| Arquivo | Para que serve |
|---------|----------------|
| `ROTEIRO.md` | Este documento: ficha técnica, roteiro por timecode, planos, transições, prompts e passo a passo |
| `letra.srt` | Os 47 versos com timecode exato. Importe no editor como guia da tipografia animada |
| `marcadores.csv` | As 12 seções + as 433 batidas e compassos, para usar como marcadores de corte |
| `grade.py` / `beats.json` / `letra.txt` | Geram o SRT e os marcadores de novo, se a letra ou os tempos mudarem |
| `frames.json` | Links da folha de personagem, das 13 imagens-chave e dos 13 clipes animados (Wan 3.0, 5 s, 480p) gerados na OpenArt (projeto "Clipe Jason e Lúcia - VAMORLI") |
| `animatic.py` | Monta o animatic com os 13 clipes animados no tempo da música (em câmera lenta quando o plano é mais longo que 5 s), cortes no compasso, flash nos refrões, letra e título. Rode no seu computador: `python3 animatic.py musica.m4a animatic.mp4` (use `--sem-video` para só as imagens) |

---

## 0. Antes de começar: personagens e direitos

Jason e Lucia são personagens da Rockstar Games. Para o clipe não levar reivindicação de direitos (Content ID) e para as ferramentas de IA não bloquearem os prompts:

- **Os nomes ficam na música e na letra animada**, porque fazem parte da sua obra.
- **O visual do casal é original:** rostos, roupas e tatuagens próprios, definidos na seção 2. Não use prints, trailers, logos ou capas do jogo, nem peça nos prompts "GTA", "Rockstar", "Vice City" ou o rosto dos personagens oficiais.
- **A cidade dos prompts é uma "cidade costeira tropical neon fictícia, inspirada na Miami dos anos 80".** É o mesmo clima, mas sem marca registrada.

Assim o clipe fica com cara de "homenagem/fan music", que é o padrão dos canais de música geek, e o material visual é 100% seu.

---

## 1. Ficha técnica da música (medida no áudio)

- **Duração:** 3:06,9
- **Andamento:** 143,5 BPM. Batida de trap em meio-tempo: a caixa cai a cada 2 tempos, então o pulso "sentido" é de ~72 BPM.
- **Grade:** batida = 0,418 s · compasso = 1,672 s · **cada verso da letra = 2 compassos = 3,344 s**.
- **Cortes:**
  - versos agitados cortam em batida ou em meio compasso (0,42–0,84 s);
  - refrões alternam corte na batida com planos de 1 compasso em câmera lenta;
  - ponte e outro usam planos de 2–4 compassos (3,3–6,7 s).

| Seção | Timecode | Compassos | Energia (medida) | Função no clipe |
|-------|----------|-----------|------------------|-----------------|
| Intro | 0:00,2 – 0:13,7 | 8 | Baixa; 808 isolado em 0:06 e 0:12 | Apresentar a cidade e os dois separados |
| Verso 1 | 0:13,7 – 0:40,7 | 16 | Sobe; hi-hats + 808 grave | O encontro e o primeiro golpe |
| Refrão 1 | 0:40,7 – 0:54,5 | 8 | Alta; grave forte | Primeira explosão visual, fuga |
| Verso 2 | 0:54,5 – 1:20,6 | 16 | Alta, mais escura | Passado dela, intimidade, briga |
| Respiro | 1:20,6 – 1:22,3 | 1 | **O beat cai (silêncio)** | Corte seco para o preto, tensão |
| Refrão 2 | 1:22,3 – 1:35,6 | 8 | Alta | Reconciliação em ação |
| Ponte | 1:35,6 – 1:48,8 | 8 | Média; piano e reverb | Cena lenta e emocional |
| Verso 3 | 1:48,8 – 2:15,4 | 16 | Crescente, rolos de hi-hat + riser | Perseguição final, tensão máxima |
| Refrão final | 2:15,4 – 2:44,6 | 17 | **A mais alta** | Clímax épico |
| Outro (voz) | 2:44,6 – 2:51,5 | 4 | Cai | Os dois olhando a cidade ao amanhecer |
| Final instrumental | 2:51,5 – 3:03,5 | 7 | **Pico de grave** | Montagem de memória + título |
| Fade | 3:03,5 – 3:06,9 | 2 | Some | Preto + logo do canal |

---

## 2. Bíblia visual

### Formato
- **Edição em 3840×2160 (4K UHD), 23,976 fps, com faixas pretas para 2,35:1** (área de imagem 3840×1634). É o melhor para o YouTube, que exibe 16:9 sem cortar.
- Se quiser 2,35:1 "nativo", exporte 3840×1634.
- Para o **Shorts/Reels de divulgação**, use 1080×1920 com o refrão (0:40,7–0:54,5) e reenquadre no centro.

### Personagens (design original)
- **"Jason"** (fim dos 20 anos): cabelo preto raspado nas laterais, bigode fino, cicatriz pequena no supercílio esquerdo, tatuagem de palmeira e relâmpago no antebraço direito. Usa regata branca, camisa de botão turquesa-pastel aberta, corrente prata fina e relógio dourado.
- **"Lucia"** (fim dos 20 anos): tranças longas descoloridas (platinadas), delineado gráfico rosa, piercing de argola no septo e tatuagem de rosa com faca no ombro. Usa corta-vento rosa-neon cortado, top preto, calça cargo e tênis branco. No flashback da prisão, usa macacão laranja.

### Paleta e color grading

| Uso | Cor |
|-----|-----|
| Neon rosa | `#FF2E88` |
| Neon ciano | `#19E3FF` |
| Laranja do pôr do sol | `#FF8A3D` |
| Roxo do céu | `#5B2A86` |
| Sombra azul-petróleo | `#0B2533` |

- **Grading Miami:** sombras puxadas para azul-petróleo, pele e realces para laranja-pêssego, neon saturado, contraste alto e preto profundo.
- **Por seção:**
  - Intro e ponte mais dessaturadas (60%) e frias.
  - Refrões com saturação total e *halation* (brilho vermelho em volta das luzes).
  - Verso 2 mais escuro, com luz de sódio (laranja) e sombras duras.
  - O outro vai ficando dourado com o nascer do sol.
- **Textura:** grão 35 mm sutil (tamanho 0,6, intensidade 15%), lens flare anamórfico horizontal ciano nas luzes, partículas (poeira e fumaça) contra luz.

### Linguagem de câmera
- **Abertos de drone:** a cidade e a costa.
- **Teleobjetiva 85–135 mm:** close dos olhos, com profundidade de campo rasa.
- **Câmera na mão:** nas brigas e nos golpes.
- **Travelling lateral:** carro em movimento.
- **Dolly-in lento:** nos momentos emocionais.

---

## 3. Roteiro plano a plano (com timecode)

**Legenda:** **P** = plano · **T** = transição para o próximo · **SFX** = som por baixo da música · **TXT** = tipografia animada.

### INTRO: 0:00,2 – 0:13,7 · "Neon no asfalto…"
Ritmo lento: 4 planos de 1 verso cada, com cortes nas frases.

| # | Tempo | Plano | Câmera / efeito | Transição | SFX |
|---|-------|-------|-----------------|-----------|-----|
| 1 | 0:00,0–0:03,5 | Drone sobre o oceano no pôr do sol, a cidade neon surge no horizonte | Drone avançando devagar, flare do sol | Fade do preto (0,5 s) | Ondas, gaivotas, chiado de vinil da música |
| 2 | 0:03,5–0:06,9 | Asfalto molhado refletindo neon rosa e ciano; um tênis branco pisa numa poça | Close baixo, câmera lenta 50% | **Corte no 808 (0:06,0)** com flash branco de 2 quadros | Passo na poça, carro passando ao longe |
| 3 | 0:06,9–0:10,2 | Split-screen vertical: Jason num posto de gasolina, Lucia no ponto de ônibus. Os dois olham para lados opostos | Duas metades em dolly-in espelhado | Desliza a divisória | Zumbido de lâmpada neon, mosquitos |
| 4 | 0:10,2–0:13,7 | Plano geral da avenida da praia ao anoitecer, letreiros acendendo em sequência no ritmo | Travelling lateral, partículas | **Whip pan** para a direita, entrando no Verso 1 | Motor V8 acelerando sob o 808 de 0:12 |

**TXT:** na abertura, sobre o plano 1, o título "JASON & LÚCIA" aparece em fonte fina espaçada, desfocando de dentro para fora. Some em 0:03.

### VERSO 1: 0:13,7 – 0:40,7 · O encontro e o primeiro golpe
Corte a cada 2 batidas (0,84 s) nas ações e a cada verso (3,34 s) nos olhares.

| # | Tempo | Verso | Plano | Câmera / efeito | Transição |
|---|-------|-------|-------|-----------------|-----------|
| 5 | 0:13,7 | "Saí do nada…" | Jason corre por um beco à noite, a câmera corre junto | Câmera na mão, desfoque de movimento | Corte na batida |
| 6 | 0:15,4 | | Pés correndo, poça explodindo | Câmera lenta 40%, rampa de volta a 100% | Corte |
| 7 | 0:17,0 | "…me ver perder" | Placa neon de cassino piscando "PERCA TUDO" (texto inventado, sem marca) | Rack focus da placa para o rosto de Jason | Corte |
| 8 | 0:20,4 | "Sol da Flórida queima…" | Sol a pino distorcendo o ar sobre a estrada, um conversível passa | Teleobjetiva com distorção de calor | Corte |
| 9 | 0:23,7 | "Minha única regra…" | Jason ajusta o relógio dourado. Close no rosto, olhar firme | Dolly-in lento | **Match cut** do relógio para a roda do carro |
| 10 | 0:27,1 | "Jacaré no pântano…" | Olho de jacaré emergindo na água à noite | Macro, reflexo de neon | Corte na batida |
| 11 | 0:28,7 | "…tubarão no cais" | Homens de terno no cais à noite (os "tubarões") | Contraluz, fumaça | Corte |
| 12 | 0:30,4 | "Quem confia em demasia…" | Uma mão entrega uma bolsa de dinheiro, outra mão esconde uma faca | Plano detalhe, sombras duras | **Glitch** de 4 quadros |
| 13 | 0:33,7 | "Mas ela me olhou…" | **Primeiro olhar:** Lucia na outra ponta de um bar neon, ela abaixa os óculos | Câmera lenta 50%, profundidade rasa, neon rosa | Corte |
| 14 | 0:35,4 | | Contraplano de Jason, o mundo em volta desfoca | Zoom lento (dolly zoom sutil) | Corte |
| 15 | 0:37,1 | "Dois contra o mundo…" | Os dois saem de uma loja de conveniência com máscaras de carnaval, sacolas na mão, sirene ao fundo | Câmera na mão, flare | **Flash branco + zoom-in rápido** no 1º tempo do refrão (0:40,7) |

**SFX:** passos, porta de loja, alarme baixinho, jacaré (sibilo), barulho de cais. A sirene entra em 0:38 e sobe junto com o riser.

### REFRÃO 1: 0:40,7 – 0:54,5 · Explosão visual
Os dois primeiros versos têm cortes rápidos (na batida). Nos dois últimos, um plano em câmera lenta por compasso.

| # | Tempo | Verso | Plano | Efeito |
|---|-------|-------|-------|--------|
| 16 | 0:40,7 | "Jason e Lucia…" | Os dois de costas caminhando em direção à câmera, carro explodindo atrás | **Speed ramp:** 100% → 25% no impacto → 100% |
| 17 | 0:42,4 | "…Vice City acesa" | Drone sobre a cidade toda acesa, a câmera passa entre prédios | Hyperlapse |
| 18 | 0:44,0 | "Sirene na nossa cola…" | Conversível fugindo, três viaturas atrás. 4 cortes na batida: roda, retrovisor, Lucia rindo, viatura derrapando | Corte na batida (0,42 s) |
| 19 | 0:45,7 | "…mas o amor é a defesa" | Ela segura a mão dele no câmbio | Câmera lenta 30%, flare ciano |
| 20 | 0:47,4 | "Neon no rosto…" | Close dos dois rostos banhados de neon rosa/ciano alternando (pisca no 808) | Luz piscando no ritmo |
| 21 | 0:49,0 | "…o grave faz a cidade tremer" | Os prédios "tremem": camera shake + distorção de onda a cada 808 | Shake sincronizado com o grave |
| 22 | 0:50,7 | "Se for pra cair, cai junto…" | Os dois pulam de um píer para a lancha em movimento | Câmera lenta 20%, partículas de água |
| 23 | 0:52,4 | "…foi o que prometi pra você" | Lancha cortando o mar escuro rumo às ilhas, rastro de espuma iluminado | Drone recuando; **corte seco** para o escuro do Verso 2 |

**TXT:** sobre os planos 16–23, ver a seção 4.

### VERSO 2: 0:54,5 – 1:20,6 · O passado dela, intimidade, briga
Fica mais escuro. A voz feminina conduz. Cortes por verso, com micro-cortes nas ações.

| # | Tempo | Verso | Plano | Câmera / efeito | Transição |
|---|-------|-------|-------|-----------------|-----------|
| 24 | 0:54,5 | "Saí da cela…" | **Flashback:** Lucia de macacão laranja atravessa o portão da prisão, sol estourado | Sobre-exposição, grão mais forte, 4:3 dentro do 2,35 | Corte |
| 25 | 0:57,8 | "Laranja no corpo…" | Ela arranca o crachá da prisão e joga fora, sorri | Câmera lenta 60% | **Match cut** do laranja do macacão para o laranja do pôr do sol |
| 26 | 1:01,1 | "Meu pai me ensinou…" | Memória: uma mão masculina mais velha entrega moedas para a mão de uma menina | Foto antiga em movimento, vinheta | Corte |
| 27 | 1:04,5 | "Cada plano que eu faço…" | Lucia desenha um plano numa mesa: mapa, fotos, barbante vermelho | Plano zenital, luz de luminária | Corte |
| 28 | 1:07,8 | "Os Keys de madrugada…" | Lancha sem luz entre ilhotas de mangue, lua alta | Drone baixo, céu azul-petróleo | Corte |
| 29 | 1:11,2 | "Passado me persegue…" | Ela pula um muro, a câmera fica para trás e uma lanterna da polícia varre o muro vazio | Câmera na mão | Corte |
| 30 | 1:14,5 | "Não quero ser rainha…" | **Intimidade:** os dois num quarto de motel, luz neon pela persiana, ela encosta a testa na dele | Câmera lenta suave, luz listrada | Corte |
| 31 | 1:16,2 | | **Briga:** ele vê uma mensagem no celular dela e levanta. Ela grita (sem som, só a música) e ele bate a porta | Câmera na mão nervosa, corte na batida | Corte |
| 32 | 1:17,9 | "…quem não luta não vive" | Ela sozinha no espelho do banheiro, rímel escorrendo, olhar decidido | Reflexo, neon rosa piscando | **Corte para o preto absoluto** em 1:20,6 |

**SFX:** portão de ferro, gaivotas e sol (flashback), lápis no papel, motor de lancha abafado, cão latindo, porta batendo em 1:17,4 **exatamente na batida**.

### RESPIRO: 1:20,6 – 1:22,3 · O beat cai
| # | Tempo | Plano | Efeito |
|---|-------|-------|--------|
| 33 | 1:20,6–1:22,3 | **Tela preta.** Só o som de um isqueiro acendendo e a chama iluminando o rosto de Jason no carro, sozinho, esperando | Silêncio da música + isqueiro e respiração. Em 1:22,3 a chama "explode" em flash laranja e entra o refrão |

### REFRÃO 2: 1:22,3 – 1:35,6 · Reconciliação em ação
| # | Tempo | Verso | Plano | Efeito |
|---|-------|-------|-------|--------|
| 34 | 1:22,3 | "Jason e Lucia…" | Ela abre a porta do carro dele e senta. Os dois se olham e ele sorri | Speed ramp no "Jason" |
| 35 | 1:24,0 | "…Vice City acesa" | Carro arrancando, pneus fumando, neon refletindo no capô | Câmera baixa colada no carro |
| 36 | 1:25,6 | "Sirene na nossa cola…" | **Helicóptero da polícia** com holofote varrendo a avenida; o carro corta pelo estacionamento | Câmera na mão no helicóptero, o holofote estoura a imagem |
| 37 | 1:27,3 | "…o amor é a defesa" | Ela atira pela janela (só o clarão, sem violência gráfica) enquanto ele dirige | Câmera lenta 30%, cartuchos dourados no ar |
| 38 | 1:29,0 | "Neon no rosto…" | Túnel de neon: as luzes passam pelos rostos | Streak de luz, desfoque radial |
| 39 | 1:30,6 | "…cidade tremer" | O carro salta uma rampa de ponte levadiça | Câmera lenta 15%, tempo "congela" no ar por 4 quadros |
| 40 | 1:32,3 | "Se for pra cair…" | Os dois rindo dentro do carro em queda | Câmera lenta |
| 41 | 1:34,0 | "…prometi pra você" | O carro aterrissa e foge. A câmera sobe para o céu, onde o pôr do sol vira noite | Drone subindo; **transição de luz:** o céu clareia em branco suave para a ponte |

### PONTE: 1:35,6 – 1:48,8 · Cena emocional e lenta
Planos longos, de 1 verso cada (3,3 s). Saturação 60%. Sem cortes na batida.

| # | Tempo | Verso | Plano | Câmera / efeito |
|---|-------|-------|-------|-----------------|
| 42 | 1:35,6 | "Bonnie e Clyde de Leonida…" | Telhado de prédio, de madrugada. Os dois sentados lado a lado, o carro lá embaixo | Plano geral fixo, silhuetas contra a cidade |
| 43 | 1:38,9 | "Cada golpe é uma prova…" | Ela tira um anel improvisado (porca de parafuso) e coloca no dedo dele | Close das mãos, profundidade rasa, câmera lenta 50% |
| 44 | 1:42,3 | "Se o mundo desabar…" | As mãos entrelaçadas, a câmera gira 180° em volta | Órbita lenta, flare suave |
| 45 | 1:45,6 | "…a gente escolhe o chão" | Os dois deitam no telhado olhando o céu. Plano zenital subindo | Drone subindo; no fim, **riser + zoom-in rápido** no rosto dela (os olhos se abrem) em 1:48,8 |

**SFX:** quase nada, só vento e uma sirene muito distante, abafada. **Deixe a música respirar.**

### VERSO 3: 1:48,8 – 2:15,4 · Perseguição final, tensão máxima
O ritmo mais rápido do clipe: corte a cada batida nos rolos de hi-hat e glitch nas viradas.

| # | Tempo | Verso | Plano | Efeito |
|---|-------|-------|-------|--------|
| 46 | 1:48,8 | "Palmeiras no vidro…" | Reflexo de palmeiras correndo no para-brisa; velocímetro em 120 | POV do motorista, desfoque de velocidade |
| 47 | 1:52,2 | "O rádio toca triste…" | O rádio do carro com luz verde; ela aumenta o volume e sorri | Close, depois corte para o contraplano |
| 48 | 1:55,5 | "Dinheiro, sangue e glória…" | Três planos de 1 batida: maço de dinheiro voando, gota de sangue no asfalto, um troféu na vitrine estilhaçando | **Corte na batida + glitch** entre cada um |
| 49 | 1:58,9 | "Vice City cobra caro…" | Bloqueio policial à frente: dezenas de luzes vermelhas e azuis | Teleobjetiva comprimindo as viaturas |
| 50 | 2:02,2 | "Se a lei bater na porta…" | Eles invadem um armazém pela frente e saem pelos fundos, onde a lancha espera | Câmera na mão, plano-sequência rápido |
| 51 | 2:05,6 | "Eu e você, Lucia…" | Lancha saltando ondas à noite, ele no leme e ela de pé apontando o caminho | Câmera lenta 40% no salto |
| 52 | 2:08,9 | "Nenhum rei, nenhum trono…" | Estrada longa sobre o mar (pontes entre ilhas), o carro sozinho ao amanhecer azul | Drone frontal recuando |
| 53 | 2:12,2 | "O nosso amor é crime…" | **Build-up:** cortes cada vez mais rápidos (1 batida → ½ → ¼) com os momentos do clipe até agora; o riser sobe | **Glitch + flash** no último quadro, explodindo no refrão final em 2:15,4 |

**SFX:** pneus cantando, motor no corte da marcha, hélice do helicóptero passando de L para R, vidro quebrando (plano 48), sirenes em coro no plano 49. Abaixe tudo em 2:14,5 para o silêncio de meio segundo antes do impacto.

### REFRÃO FINAL: 2:15,4 – 2:44,6 · O clímax épico
É a parte mais forte da música, então combine as melhores imagens com a tipografia mais forte.

| # | Tempo | Verso | Plano | Efeito |
|---|-------|-------|-------|--------|
| 54 | 2:15,4 | "Jason e Lucia…" | Os dois saem de dentro da fumaça caminhando em câmera lenta, a cidade explodindo em fogos atrás | Speed ramp 100% → 20%, flare gigante |
| 55 | 2:17,1 | "…Vice City acesa" | Drone 360° em volta do arranha-céu mais alto, com a cidade inteira acesa | Hyperlapse em órbita |
| 56 | 2:18,8 | "Sirene na nossa cola…" | Montagem na batida: helicóptero, lancha, carro e viaturas, 8 cortes de 0,42 s | Corte na batida + shake no grave |
| 57 | 2:22,1 | "Neon no rosto…" | Os dois rostos frente a frente, neon trocando de cor a cada batida | Luz sincronizada |
| 58 | 2:25,5 | "Se for pra cair, cai junto…" | **Momento-símbolo:** carro em fuga voando para fora de um viaduto rumo ao mar; os dois de mãos dadas | Câmera lenta extrema 10%, partículas, som abafado |
| 59 | 2:28,8 | "…prometi pra você" | O carro afunda em luz. Corte para os dois emergindo juntos na água iluminada por neon | Transição pela água (bolhas = máscara) |
| 60 | 2:32,1 | "Se for pra cair, cai junto… Vice City, Jason e Lucia" | Montagem de **match cuts** dos dois em todas as fases (prisão, bar, motel, telhado, lancha) sempre na mesma posição de quadro | Match cut a cada compasso (1,67 s) |
| 61 | 2:38,8 | (ad-libs) | Plano aéreo da costa, a lancha minúscula partindo rumo ao horizonte | Drone subindo bem alto; a música começa a cair em 2:44,6 |

### OUTRO (voz): 2:44,6 – 2:51,5 · "Luzes apagando…"
| # | Tempo | Verso | Plano | Efeito |
|---|-------|-------|-------|--------|
| 62 | 2:44,6 | "Luzes apagando, o sol vai nascer" | Os dois sentados no capô do carro, num mirante, olhando a cidade. O neon vai apagando prédio por prédio | Plano fixo de costas; o céu passa de roxo a dourado |
| 63 | 2:47,9 | "Dois nomes na história…" | Close lateral dos dois: ela encosta a cabeça no ombro dele | Dolly-in lento, sol nascendo atrás (flare quente) |

### FINAL INSTRUMENTAL: 2:51,5 – 3:03,5 · Título
| # | Tempo | Plano | Efeito |
|---|-------|-------|--------|
| 64 | 2:51,5 | O sol nasce por completo e a imagem estoura em branco quente | Flash suave no pico do 808 |
| 65 | 2:52,3 | **Título final** sobre fundo de céu: "JASON & LÚCIA", com "VAMORLI MUSIC" abaixo | Letras entram uma a uma na batida e pulsam no grave |
| 66 | 2:56,0 | Por trás do título, uma "galeria de memórias" em polaroids caindo (cada uma é um frame do clipe), uma por batida | Parallax 2,5D |

### FADE: 3:03,5 – 3:06,9
| # | Tempo | Plano | Efeito |
|---|-------|-------|--------|
| 67 | 3:03,5 | Fade para o preto. Fica só o logo do canal e "inscreva-se" discreto | Fade de 2 compassos acompanhando o áudio |

---

## 4. Tipografia animada (refrões)

**Fontes:**
- Títulos condensados e pesados: **Anton** ou **Bebas Neue** (gratuitas).
- Palavras-chave em script neon: **Monoton** ou **Neonderthaw** (gratuitas no Google Fonts).

**Regras:**
- Uma linha por vez, sempre na área de imagem (dentro das faixas pretas).
- Glow (brilho) rosa ou ciano e leve aberração cromática.
- A palavra-chave entra no 808 e o resto entra antes dela.

| Verso do refrão | Animação |
|-----------------|----------|
| "Jason e Lucia" | Os dois nomes vêm de lados opostos e se encontram no centro no 808; o "e" vira um coração neon que pisca uma vez |
| "Vice City acesa" | Letras acendem uma por uma como letreiro neon com falha (flicker), a última "estoura" num flash |
| "Sirene na nossa cola" | Texto alternando vermelho/azul a cada batida, como luz de viatura |
| "mas o amor é a defesa" | "amor" em script neon rosa, desenhado como traço de luz (write-on) |
| "Neon no rosto" | Texto refletido como num capô molhado (reflexo embaixo) |
| "o grave faz a cidade tremer" | Cada 808 dá shake e distorção de onda só no texto; "TREMER" com letras deslocadas |
| "Se for pra cair, cai junto" | As palavras caem de cima com gravidade e quicam no chão no tempo forte |
| "foi o que prometi pra você" | Write-on lento, fica 1 compasso a mais e se desfaz em partículas |

**Fora dos refrões:** legenda discreta (Bebas Neue, branca, 70% de opacidade, com sombra), no rodapé da área de imagem. Use `letra.srt` como base.

---

## 5. Prompts de imagem e vídeo (por cena)

Os prompts estão em inglês, porque as ferramentas entendem melhor. Use sempre os blocos **[ESTILO]** e **[CASAL]** junto com o prompt de cada cena.

**[ESTILO]**
```
cinematic film still, anamorphic 2.39:1, shot on ARRI Alexa with Cooke anamorphic lenses, 1980s Miami neo-noir mood, neon pink (#FF2E88) and cyan (#19E3FF) lights, sunset orange, teal shadows, high contrast, halation around lights, horizontal anamorphic lens flare, shallow depth of field, volumetric haze, subtle 35mm film grain, fictional tropical coastal city
```

**[CASAL]** (gere primeiro uma folha de personagem e use como referência em todas as cenas)
```
original characters: a man in his late 20s with black hair shaved on the sides, thin mustache, small scar on left eyebrow, palm-tree-and-lightning tattoo on right forearm, white tank top under an open pastel turquoise short-sleeve shirt, thin silver chain, gold watch;
a woman in her late 20s with long platinum-blonde box braids, graphic pink eyeliner, septum ring, rose-and-dagger tattoo on shoulder, cropped neon pink windbreaker, black crop top, cargo pants, white sneakers
```

**Folha de personagem (gerar primeiro):**
```
character reference sheet, front, side and back views, full body and close-up faces, of [CASAL], neutral gray background, consistent design, cinematic lighting
```

| Cena | Prompt (adicione [ESTILO] e, quando houver personagens, [CASAL]) |
|------|---------------------------------------------------------------|
| 1 · Abertura | `aerial drone shot over a calm ocean at golden hour, a neon-lit art-deco coastal skyline glowing on the horizon, palm trees, purple and orange sky, slow push forward` |
| 2 · Asfalto | `extreme low angle close-up of wet asphalt reflecting pink and cyan neon signs, a white sneaker stepping into a puddle in slow motion, splash droplets frozen` |
| 3 · Separados | `split screen: the man alone at a neon gas station at night looking left; the woman alone at a bus stop under a flickering streetlight looking right, mirrored composition` |
| 5 · Fuga no beco | `handheld tracking shot of the man running through a narrow alley at night, steam vents, neon signs, motion blur, tense` |
| 10–11 · Pântano/cais | `macro shot of an alligator eye emerging from dark swamp water reflecting neon` / `silhouetted men in suits on a foggy dock at night, backlit by harbor lights` |
| 13 · O olhar | `the woman at the far end of a neon-lit cocktail bar slowly lowering her sunglasses, locking eyes with the camera, pink rim light, slow motion, 85mm` |
| 15 · Primeiro golpe | `the couple running out of a convenience store wearing carnival masks, holding bags, red and blue police lights flaring in the background, handheld` |
| 16 · Explosão | `the couple walking toward camera in slow motion, a car exploding behind them, sparks and smoke, epic hero shot, dramatic backlight` |
| 18 · Perseguição | `a 1980s style red convertible speeding down a palm-lined beach boulevard at night, police cars chasing, sirens glowing, motion blur, low tracking shot` |
| 22 · Píer → lancha | `the couple jumping from a wooden pier onto a speeding speedboat at night, water spray frozen in mid-air, neon city behind, slow motion` |
| 24 · Prisão | `flashback, the woman in an orange prison jumpsuit walking out through a chain-link prison gate into blinding Florida sunlight, overexposed, nostalgic 4:3 framing, heavy grain` |
| 27 · Plano | `top-down shot of a table covered with a city map, photos and red string, a hand drawing a route with a marker, desk lamp light, noir` |
| 28 · Keys | `a dark speedboat without lights gliding between mangrove islets under a bright moon, teal night sky, low drone shot` |
| 30 · Motel | `intimate moment in a cheap motel room, neon light through window blinds casting stripes, the couple resting foreheads together, soft and warm` |
| 32 · Espelho | `the woman alone in a bathroom mirror, smeared mascara, determined look, flickering pink neon, reflection composition` |
| 33 · Isqueiro | `pitch black, a lighter flame illuminating the man's face inside a car, waiting alone, chiaroscuro` |
| 36 · Helicóptero | `police helicopter searchlight sweeping a neon avenue at night, a car cutting through a parking lot, aerial handheld, lens flare from the searchlight` |
| 39 · Salto | `a car jumping over an opening drawbridge at night in slow motion, city lights below, sparks, epic wide shot` |
| 42 · Telhado | `two silhouettes sitting side by side on a rooftop at dawn, a neon city stretching to the sea, calm and melancholic, wide static shot` |
| 43 · Anel | `close-up of a woman's hand sliding a hex-nut ring onto a man's finger, shallow depth of field, soft rooftop dawn light` |
| 46 · POV estrada | `driver POV through a windshield, palm tree reflections streaking across the glass, speedometer at 120, motion blur, night highway` |
| 49 · Bloqueio | `telephoto shot of a police roadblock with dozens of red and blue lights compressed together, heat haze, night` |
| 51 · Lancha | `speedboat leaping over a wave at night, the man at the helm, the woman standing and pointing ahead, spray in slow motion, neon skyline` |
| 52 · Ponte sobre o mar | `a lone car on a long bridge over turquoise sea connecting tropical islands, blue dawn, drone pulling back` |
| 54 · Clímax | `the couple emerging from thick smoke in slow motion, fireworks exploding over the neon city behind them, giant anamorphic flare, epic` |
| 58 · Voo do carro | `a car flying off a highway overpass toward the ocean at night, the couple holding hands inside, extreme slow motion, particles, surreal and epic` |
| 59 · Água | `underwater shot of the couple surfacing together in water lit by neon from above, bubbles, dreamy` |
| 62 · Amanhecer | `the couple sitting on the hood of a car at a scenic overlook, seen from behind, watching the neon city switch off as the sun rises, purple turning to gold` |
| 65 · Título | `empty dawn sky over the sea with soft golden clouds, space for title text, cinematic, calm` |

**Prompts de movimento (para imagem → vídeo):** acrescente no fim:
- planos de ação: `handheld camera, fast motion, 24fps`;
- planos emocionais: `slow dolly in, gentle movement`;
- planos aéreos: `smooth drone orbit`.

Gere clipes de **5 s**. Na edição, aproveite de 0,8 a 3,3 s de cada um, conforme o roteiro.

---

## 6. Sound design (por baixo da música)

| Momento | Som | Volume em relação à música |
|---------|-----|---------------------------|
| Intro | Ondas, gaivotas, neon zumbindo, carro ao longe | -18 dB |
| Verso 1 | Passos, alarme de loja, sirene crescente no fim | -16 dB |
| Refrões | Motor V8, pneus, sirene, helicóptero passando L→R, explosão no 1º tempo | -12 dB, **abaixe ainda mais na voz** |
| Verso 2 | Portão de ferro, lápis, porta batendo na batida | -16 dB |
| Respiro (1:20,6) | Isqueiro + respiração | Em primeiro plano, a música está em silêncio |
| Ponte | Vento, sirene muito distante | -24 dB |
| Verso 3 | Pneus, vidro, sirenes em coro, whoosh nos glitches | -14 dB |
| Outro | Pássaros do amanhecer, cidade "desligando" | -20 dB |

**Mixagem:**
- **Grave:** reforce a faixa de 40–60 Hz no refrão com um EQ leve (+2 dB) e use corte lateral (sidechain) dos efeitos pelo kick e pelo 808, para não embolar.
- **Voz da música:** não pode ser coberta. Abaixe os efeitos automaticamente (ducking) nos trechos cantados.
- **Loudness final:** -14 LUFS integrado, pico real de -1 dBTP (padrão do YouTube).

**Fontes de SFX legais:** Freesound.org (filtrar por CC0), Pixabay Sound Effects, Epidemic Sound ou Artlist (com assinatura).

---

## 7. Ferramentas e passo a passo de edição

### Ferramentas sugeridas

| Etapa | Ferramenta |
|-------|------------|
| Personagens e frames-chave | Midjourney v7 (com `--cref` ou referência de personagem), Flux, Ideogram, ou OpenArt (já conectada a esta conta) |
| Imagem → vídeo | Kling 2.x, Runway Gen-4, Google Veo 3, Luma Ray 2 |
| Upscale para 4K e interpolação | Topaz Video AI (Proteus/Artemis para upscale, Apollo/Chronos para câmera lenta) |
| Edição e cor | **DaVinci Resolve** (gratuito) ou Premiere Pro |
| Tipografia animada | After Effects (+ Saber/Deep Glow) ou o próprio Fusion do Resolve |
| Efeitos de luz | Flares (Video Copilot Optical Flares / Resolve "Lens Flare"), overlays de partículas e fumaça em modo Screen |
| Som | Fairlight (Resolve) ou Audition |

### Passo a passo

1. **Montar o projeto:** linha do tempo 3840×2160 a 23,976 fps. Coloque a música na faixa A1 e importe `marcadores.csv` como marcadores (no Resolve: Timeline → Import → Timeline Markers from EDL/CSV, ou cole os tempos das seções).
2. **Animatic primeiro:** gere as imagens fixas de todas as 67 cenas e monte no tempo certo, com zoom digital simples. Assim você valida o ritmo **antes** de gastar créditos com vídeo.
3. **Personagens consistentes:** gere a folha de personagem, escolha os melhores rostos e use-os como referência em todas as gerações. Gere 3–4 variações por cena e escolha a melhor.
4. **Imagem → vídeo:** anime só as cenas aprovadas no animatic e troque cada imagem fixa pelo vídeo correspondente.
5. **Corte fino na batida:** com o snapping ligado aos marcadores, ajuste cada corte para cair exatamente na batida. Nos refrões, corte 1–2 quadros **antes** do kick para o impacto parecer mais forte.
6. **Speed ramps:** use Retime Curve (Resolve) ou Time Remapping (Premiere). Rampa de 100% → 20–25% no impacto, segura de 0,5–1 s e volta a 100% no próximo tempo forte. Para câmera lenta suave, interpole os quadros no Topaz antes.
7. **Transições:**
   - **Whip pan:** desfoque direcional de 4–6 quadros nos dois lados do corte, mais um whoosh.
   - **Glitch:** 3–4 quadros de RGB split e deslocamento de blocos.
   - **Flash:** 2 quadros brancos com o brilho caindo.
   - **Match cut:** alinhe o objeto no mesmo ponto do quadro.
8. **Cor:**
   - **Nó 1:** balanço e exposição.
   - **Nó 2:** look Miami (sombras no teal, realces no laranja, saturação seletiva de rosa e ciano).
   - **Nó 3:** halation e glow.
   - **Nó 4:** grão.
   - **Por último:** as faixas pretas 2,35:1 (Output Blanking 2.35).
9. **Tipografia:** anime os refrões seguindo a tabela da seção 4 e as legendas dos versos a partir de `letra.srt`.
10. **Som:** coloque os efeitos de som da seção 6, faça a mixagem com ducking e normalize para -14 LUFS.
11. **Exportar:**
    - **YouTube:** H.264/H.265 3840×2160, 23,976 fps, 50–80 Mbps, áudio AAC 320 kbps.
    - **Shorts/Reels:** versão 1080×1920 do refrão (0:40,7–0:54,5).
12. **Thumbnail:** use o frame da cena 54 (os dois saindo da fumaça) com "JASON & LÚCIA" em Anton, contorno neon.
