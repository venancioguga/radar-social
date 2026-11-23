# Fora da curva: o que funcionou num perfil e por quê

**Pergunta que responde:** quais posts foram muito acima do normal deste perfil, o que eles têm em comum e o que eu posto a partir disso.

## Passo a passo

1. **Colete pelo menos 30 posts** (o ideal é 3 meses ou mais).
   - YouTube: `python3 scripts/coletar.py youtube @canal --limite 200 --saida posts.csv`
   - Instagram: `python3 scripts/coletar.py instagram usuario --limite 100 --saida posts.csv`
   - Outras redes: CSV com os números que a pessoa tiver.
2. **Rode a régua:** `python3 scripts/fora_da_curva.py posts.csv`
   - O script escolhe sozinho: views quando existe, senão engajamento (likes + comentários + compartilhamentos + salvos).
   - Instagram não entrega views de outras contas pela API oficial; use engajamento e diga isso.
   - Grupos separados por formato: short não compete com vídeo longo; reel, carrossel e post também ficam separados.
3. **Leia as faixas:** 5x ou mais = explodiu · 2x a 5x = forte · 1,5x a 2x = acima do normal.
4. **Olhe o "sinal precoce".** Posts com menos de 3 dias ficam fora da régua porque ainda estão crescendo. Se um deles já passou da régua, é o assunto quente do momento: vale citar à parte.
5. **Abra os 3 a 5 melhores** (título, legenda, thumbnail, primeiros segundos, comentários) e preencha para cada um:

| Ponto | Pergunta |
|---|---|
| Assunto | Do que fala, em uma frase? |
| Gancho | O que prende nos primeiros 3 segundos ou na primeira linha? |
| Gatilho | Novidade, curiosidade, medo, utilidade, polêmica, identificação, orgulho, humor? |
| Formato | Short/reel, tutorial, lista, notícia, bastidor, opinião, antes e depois? |
| Momento | Pegou uma onda (data, notícia, tendência)? Se sim, é repetível? |
| Público | O que os comentários mostram sobre quem se interessou? |

6. **Ache o padrão.** Um sucesso isolado é sorte; três com o mesmo ingrediente é padrão. Compare também com os posts que ficaram abaixo da régua: o que eles NÃO têm?
7. **Transforme em pauta.** Entregue 5 ideias concretas para a marca de quem pediu, cada uma com título ou gancho escrito, formato e qual padrão ela aproveita.

## Cuidados

- Base de 10 posts ou menos: diga "confiança baixa" e trate como pista, não como conclusão.
- Um vídeo que explodiu por um motivo externo (virou meme, foi impulsionado, entrou numa notícia) não é receita. Se houver sinal de anúncio pago, separe.
- Não copie o post do concorrente: extraia o ingrediente e aplique na voz da marca.

## Modelo de entrega

```
## Fora da curva: @perfil (rede, período)
Base: mediana de X por post, N posts, confiança alta/média/baixa.

| # | Post | Vezes o normal | Por que funcionou (uma linha) |

Padrões que se repetem
1. ...
O que não funciona
- ...
5 pautas para <marca>
1. "<gancho escrito>" (formato) · aproveita o padrão ...
```
