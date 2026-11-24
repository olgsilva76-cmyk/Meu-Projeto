# Instruções para o Claude neste projeto

Este projeto é para **editar vídeos curtos para Instagram/TikTok** no estilo das
referências que o usuário enviou.

Sempre que o usuário pedir uma edição de vídeo:
1. Leia `edicao/GUIA_DE_ESTILO.md` (estilos A, B, C, D com regras de roteiro,
   ritmo de cortes, legenda e cor).
2. Escolha o estilo pela tabela do guia (ou pergunte se não der para saber).
3. Use `edicao/editar.py` para o trabalho automático (cortar silêncios,
   reenquadrar, legendar, cor, áudio). Exemplo:
   `python3 edicao/editar.py bruto.mp4 final.mp4 --estilo a --destaques "biotina,vitamina"`
4. O que o script não faz sozinho (escolher B-roll, ordem das cenas, encenações)
   deve ser montado seguindo a "Estrutura" do estilo no guia; proponha o roteiro
   de cortes ao usuário antes se o material for longo.
5. Responda sempre em português.
