# Radar Social

**Pesquisa de redes sociais com dados reais, em português, de graça.**

Uma skill para agentes de IA (Claude Code, Cursor, Codex, Gemini CLI e outros) que transforma "o que eu posto?" em resposta com número, link e pauta pronta.

[English](README.en.md)

## O que ele faz

| Pergunta | O que você recebe |
|---|---|
| O que bombou neste perfil? | Os posts que foram muito acima do normal **do próprio perfil**, por formato, com o porquê e 5 pautas |
| O que o público está dizendo? | Comentários separados em pergunta, objeção, reclamação, pedido de conteúdo, intenção de compra e elogio, entendendo gíria, "kkkk" e ironia |
| Como estou contra o concorrente? | Quadro comparativo justo (cada conta com a sua régua), anúncios ativos e espaços vazios |
| Que dia e horário postar? | Dia e faixa de horário que rendem mais **neste** perfil, no fuso do Brasil |
| A campanha funcionou? | Antes x depois separando volume (postou mais) de qualidade (cada post rendeu mais) |
| Preciso mandar para o cliente | Relatório em português claro, com fontes e limites |

## Por que é diferente

- **Grátis de verdade.** Usa as APIs oficiais e gratuitas do YouTube e da Meta, com chaves que você mesmo cria em minutos. Sem assinatura, sem crédito, sem intermediário.
- **Funciona sem chave nenhuma** para começar: feed público do YouTube ou qualquer planilha/CSV que você exportar de TikTok, Kwai, LinkedIn ou do seu painel.
- **Conta feita por código, não de cabeça.** Scripts em Python (sem instalar nada) calculam tudo. O resultado é sempre o mesmo e dá para conferir.
- **Feito para o Brasil.** Lê "12,5 mil" e "3.400", entende "quanto tá?", "passa o link", "faz parte 2", "amei kkkk" (ironia), usa fuso de Brasília e escreve relatório sem jargão.
- **Privacidade.** Nunca guarda nem mostra o nome de quem comentou.

## Instalação

Com o instalador de skills (Claude Code, Cursor, Codex e outros):

```bash
npx skills add venancioguga/radar-social
```

Como plugin do Claude Code:

```
/plugin marketplace add venancioguga/radar-social
/plugin install radar-social@radar-social
```

Manual: copie a pasta `skills/radar-social` para `~/.claude/skills/` (ou a pasta de skills do seu agente).

Requisito: Python 3.9 ou mais novo (já vem no Mac e na maioria dos Linux).

## Primeiro uso (sem chave)

Peça ao seu agente:

> Usa o radar social e me diz o que mais funcionou no canal @nomedocanal do YouTube.

Ou teste com os dados de exemplo:

```bash
cd skills/radar-social
python3 scripts/fora_da_curva.py ../../exemplos/posts-exemplo.csv
python3 scripts/comentarios.py ../../exemplos/comentarios-exemplo.csv
```

Para histórico completo do YouTube, comentários e Instagram, crie as chaves gratuitas: [passo a passo](skills/radar-social/guias/chaves.md).

## Fontes

| Fonte | O que dá | Custo |
|---|---|---|
| Feed público do YouTube | 15 vídeos mais recentes | grátis, sem chave |
| YouTube Data API | histórico completo e comentários | grátis (10 mil unidades/dia) |
| Instagram Graph API | posts, curtidas e comentários de contas comerciais e de criador | grátis |
| Seus exports e planilhas | qualquer rede | grátis |

O Radar Social só usa dados públicos, por APIs oficiais ou fornecidos por você. Não faz raspagem, não contorna login nem limite de plataforma.

## Como funciona a régua

Cada post é comparado com a **mediana** dos posts do mesmo perfil e do mesmo formato. Mediana, e não média, para que um único viral não distorça a régua. Um post com "4x" fez quatro vezes o resultado típico daquele perfil. Posts com menos de 3 dias ficam fora da régua (ainda estão crescendo), mas aparecem como "sinal precoce" quando já passaram dela.

## Contribua

Ideias, correções e novas fontes são bem-vindas: abra uma issue ou um pull request. Prioridade: fontes oficiais e gratuitas, e expressões brasileiras novas para a leitura de comentários (`scripts/comentarios.py`).

## Licença

MIT. Feito por [Guga Venancio](https://github.com/venancioguga). Um projeto [Guve](https://guve.io).
