# Montagem do fluxo de edição

Fase atual: 2 (entrevista, decisão 4 em diante) · Atualizado em 2026-11-28

## Ambiente
- A pessoa só tem celular (sem computador). O fluxo roda em sessões do Claude Code na nuvem, abertas pelo app no celular.
- Container da nuvem: Linux · Python 3.13 · FFmpeg 6.1 · Node.js 22 · Git · sem GPU
- O container é descartado a cada sessão: tudo o que precisa durar fica neste repositório (Meu-Projeto) ou no Drive.
- Rede: o Google Drive (drive.google.com, drive.usercontent.google.com) está **bloqueado** pela política de rede do ambiente. É preciso liberar antes do primeiro vídeo de verdade.
- Instalado nesta montagem: nada ainda

## Decisões
- Revisão: vídeo pronto (caminho C, sem programa). Edita no InShot, que não importa projetos; a pessoa pode finalizar o MP4 no InShot.
- Tipo e formato: falando para a câmera + gravação de tela. Quase sempre vertical 9:16, às vezes horizontal 16:9. De 30 s a 3 min. Gravado no celular, "60 fps" (conferir a taxa real; celular costuma gravar com taxa variável).
- Vídeos curtos: sem trabalho por trecho.
- Entrada dos vídeos: Google Drive (link compartilhado). Saída: a definir (sugestão: Release do GitHub ou Drive).
- Pastas: ferramentas em `Meu-Projeto/edicao/`; skills em `Meu-Projeto/.claude/skills/`; projeto de cada vídeo: a definir
- Transcrição: <…>
- Notas faladas: <…>
- Animação: <…>
- Câmera: <…>
- Som: <…>
- Revisões: <…>
- Nomes: prefixo <…>; skill mestra /<…>

## Perfil
- (ainda não começado)

## Fluxo aprovado
(ainda não)

## Skills escritas
- [ ] regras comuns

## Próximo passo
Entrevista: decisão 3 (como o vídeo entra e sai) e depois a 4 (transcrição).
