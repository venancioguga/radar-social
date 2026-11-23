# Horários: quando este perfil rende mais

**Pergunta que responde:** em que dia da semana e faixa de horário os posts deste perfil costumam ir melhor, pelos dados dele mesmo, e não por tabela genérica da internet.

## Passo a passo

1. Colete pelo menos 60 posts com data e hora (o `coletar.py` já entrega `publicado_em`).
2. `python3 scripts/horarios.py posts.csv` (fuso padrão: Brasília). Para outro fuso: `--fuso America/Manaus`, `--fuso Europe/Lisbon`.
3. Leia a coluna "Rende": 1,0x é o normal do perfil. 1,5x num dia quer dizer que, nesse dia, o post típico faz 50% a mais que o normal.
4. Ignore linhas marcadas "poucos posts".

## Como explicar

- Horário pesa pouco perto de assunto e gancho. Apresente como desempate: "se tiver dois posts prontos, guarde o melhor para domingo à noite".
- Dia com poucos posts e resultado alto pode ser acaso (um viral só). Diga quantos posts sustentam a conclusão.
- O perfil pode só nunca ter testado certos horários. Sugira um teste de 4 semanas antes de mudar a grade toda.
- Datas brasileiras mexem no resultado: feriado, Black Friday, Copa, Carnaval, BBB, horário de novela e de jogo de futebol.

## Modelo de entrega

```
## Quando postar: @perfil
Melhores dias: ... (Nx o normal, N posts)
Melhores horários: ...
Evitar: ...
Teste sugerido para as próximas 4 semanas: ...
```
