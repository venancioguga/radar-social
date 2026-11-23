# Concorrentes: onde eles ganham, onde ninguém está

**Pergunta que responde:** o que funciona para os concorrentes, o que eles anunciam e qual espaço está vazio para a minha marca.

## Passo a passo

1. **Defina 2 a 5 perfis** parecidos em proposta (não só em tamanho). Inclua o perfil de quem pediu.
2. **Colete todos para o mesmo CSV** (mesma rede, mesmo período):
   ```
   python3 scripts/coletar.py instagram marca_a --limite 100 --saida a.csv
   python3 scripts/coletar.py instagram marca_b --limite 100 --saida b.csv
   python3 scripts/fora_da_curva.py a.csv b.csv nossa.csv
   ```
   Cada conta tem a sua própria régua, então dá para comparar quem acerta mais vezes, mesmo com tamanhos diferentes.
3. **Monte o quadro comparativo**:

| | Marca A | Marca B | Nós |
|---|---|---|---|
| Posts por semana | | | |
| Formato principal | | | |
| % de posts acima de 2x a própria régua | | | |
| Assuntos dos posts fora da curva | | | |
| Tom (didático, divertido, institucional, polêmico) | | | |

4. **Anúncios.** Consulte a Biblioteca de Anúncios da Meta (facebook.com/ads/library, filtro Brasil) e a Central de Transparência de Anúncios do Google (adstransparency.google.com). Para cada anúncio ativo anote: promessa, oferta, prova (depoimento, número, antes e depois), chamada, formato e desde quando está no ar. Anúncio rodando há mais de 30 dias normalmente está dando retorno.
5. **Ache o espaço vazio:** assunto que gera conversa nos comentários dos concorrentes e que nenhum deles responde bem; formato que ninguém usa; pergunta que se repete sem resposta.

## Cuidados

- Comparar não é copiar. Entregue o ingrediente, não o post.
- Números de concorrente vêm só do que é público. Não estime faturamento ou verba de anúncio sem fonte.
- No Brasil, regras de setor (saúde, financeiro, bebida) limitam o que dá para anunciar; considere isso antes de sugerir copiar um ângulo.

## Modelo de entrega

```
## Concorrentes: <nicho> (<rede>, <período>)
Quadro comparativo
O que cada um faz melhor (1 linha por marca)
Anúncios ativos que chamam atenção (com link)
Espaços vazios
5 testes para a nossa marca
```
