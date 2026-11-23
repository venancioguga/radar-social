# Antes e depois: a mudança funcionou?

**Pergunta que responde:** depois que começamos a campanha, mudamos a linha editorial, contratamos a agência ou passamos a postar reels, o perfil melhorou?

## Passo a passo

1. Pergunte a data da mudança, se não veio no pedido.
2. Colete posts suficientes para cobrir o mesmo número de dias antes e depois.
3. `python3 scripts/antes_depois.py posts.csv --corte 2026-10-01 --dias 60`
   - Compara o mesmo número de dias de cada lado.
   - Mostra posts, posts por semana, mediana por post, total e a mistura de formatos.
4. Explique separando as duas coisas que mais confundem:
   - **Volume:** postou mais? O total sobe só por isso.
   - **Qualidade:** a mediana por post subiu? Esse é o sinal de que o conteúdo ficou melhor.
5. Rode também o `fora_da_curva.py` só no período depois para mostrar quais posts puxaram o resultado.

## Cuidados

- Posts com menos de 3 dias ainda estão crescendo; o script avisa. Se forem muitos, espere ou diga que é parcial.
- Sazonalidade: dezembro não se compara com outubro sem ressalva. Black Friday, férias e feriados mexem em tudo.
- Correlação não é causa. Se outra coisa mudou junto (anúncio pago, collab, notícia), diga.

## Modelo de entrega

```
## Antes x depois de <data>: @perfil
Resposta curta: melhorou / piorou / igual, em uma frase.
| | Antes | Depois | Variação |
O que puxou o resultado (posts com link)
Ressalvas
Próximo passo
```
