---
name: radar-social
description: Pesquisa de redes sociais com dados reais e em português do Brasil, usando só fontes oficiais e gratuitas. Descobre quais posts de um perfil foram muito acima do normal e por quê, lê comentários entendendo gíria e ironia (perguntas, objeções, intenção de compra, pedidos de conteúdo), compara concorrentes, mostra o melhor dia e horário de postar, mede antes e depois de uma campanha e entrega um relatório pronto para cliente. Use quando pedirem "o que bombou no perfil X", "posts que viralizaram", "o que o público está perguntando", "analisa os comentários", "compara com o concorrente", "melhor horário para postar", "a campanha funcionou?", "me dá pautas com base em dados", "relatório para o cliente".
license: MIT
---

# Radar Social

Pesquisa de redes sociais com número de verdade. Os scripts fazem a conta; você (o agente) explica o que ela quer dizer e transforma em pauta, gancho e decisão.

Pasta desta skill: os scripts ficam em `scripts/` e os roteiros detalhados em `guias/`, ao lado deste arquivo. Rode os scripts com `python3` (biblioteca padrão, nada para instalar).

## 1. Entenda o pedido e escolha o roteiro

| A pessoa quer saber | Roteiro |
|---|---|
| o que funcionou num perfil, de onde tirar pauta | `guias/fora-da-curva.md` |
| o que o público pergunta, reclama, pede, quer comprar | `guias/comentarios.md` |
| como estou contra um ou mais concorrentes, o que eles anunciam | `guias/concorrentes.md` |
| que dia e horário postar | `guias/horarios.md` |
| se uma campanha, mudança ou formato novo deu resultado | `guias/antes-depois.md` |
| um documento para mandar a cliente ou chefe | `guias/relatorio.md` (combina com qualquer um acima) |

Pedido vago ("analisa o @perfil")? Faça fora da curva + comentários dos 3 melhores posts. É o que mais rende em pouco tempo.

## 2. Pegue os dados (sempre a fonte gratuita primeiro)

| Fonte | Comando | Precisa de |
|---|---|---|
| YouTube, 15 vídeos mais recentes | `coletar.py youtube-rss @canal` | nada |
| YouTube, histórico completo | `coletar.py youtube @canal --limite 200` | `YOUTUBE_API_KEY` (grátis) |
| Comentários de um vídeo do YouTube | `coletar.py youtube-comentarios <link> --limite 500` | `YOUTUBE_API_KEY` |
| Instagram de contas comerciais e de criador | `coletar.py instagram usuario --limite 100` | `META_ACCESS_TOKEN` e `IG_BUSINESS_ID` (grátis) |
| Qualquer rede (TikTok, Kwai, LinkedIn, X) | CSV exportado, planilha, prints ou números colados pela pessoa | nada |

Sempre use `--saida arquivo.csv`. Se faltar a chave, não trave: comece pelo que dá (YouTube RSS ou dados colados) e mostre o passo a passo de `guias/chaves.md` para a próxima vez. Nunca peça para a pessoa colar a chave na conversa: ela deve ficar numa variável de ambiente.

Dados colados ou de print: monte um CSV com as colunas `plataforma,conta,publicado_em,titulo,url,views,likes,comentarios,formato` (pode deixar vazias as que não tiver) e use os mesmos scripts. Aceita número escrito como "12,5 mil", "1,2M" ou "3.400".

## 3. Calcule com os scripts, não de cabeça

- `fora_da_curva.py posts.csv`: régua de cada perfil e posts acima dela.
- `comentarios.py comentarios.csv --saida rotulados.csv`: triagem de intenção em pt-BR.
- `horarios.py posts.csv`: dia e faixa de horário.
- `antes_depois.py posts.csv --corte AAAA-MM-DD`: antes x depois.

Todos aceitam vários CSV de uma vez. Use os números exatamente como saem. Se o resultado parecer estranho, confira os dados antes de explicar.

## 4. Interprete e entregue

O número diz o quê; você explica o porquê e o que fazer. Para cada achado: o dado, a leitura, a ação. Feche sempre com uma lista curta de próximos passos (pautas, ganchos, testes) adaptados à marca de quem pediu.

## Regras que não mudam

1. **Compare cada perfil com ele mesmo.** Nunca ranqueie views brutos entre contas de tamanhos diferentes.
2. **Mostre o tamanho da amostra e a confiança.** Menos de 10 posts num grupo = conclusão fraca, e isso aparece no texto.
3. **Link de tudo.** Todo post, anúncio ou comentário citado leva link. Sem link, não cite.
4. **Nada inventado.** Não invente número, transcrição, comentário ou motivo. Se não deu para ver o vídeo, diga que a leitura é pelo título e pelos números.
5. **Privacidade.** Não exponha nome, foto ou @ de quem comentou. Cite o texto, não a pessoa.
6. **Fale como gente.** Português claro, sem jargão de analista. "Esse vídeo teve 10 vezes as views normais do canal" em vez de "lift de 10x sobre o baseline".
7. **Dados públicos e oficiais.** Use APIs oficiais e o que a pessoa fornecer. Não contorne login, bloqueio ou limite de plataforma.
