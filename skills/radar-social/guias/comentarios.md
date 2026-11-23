# Comentários: o que o público pergunta, reclama, pede e quer comprar

**Pergunta que responde:** o que as pessoas estão dizendo de verdade, com as palavras delas, e o que fazer com isso (pauta, FAQ, anúncio, produto, atendimento).

## Passo a passo

1. **Escolha bem os posts.** Comentário bom vem de post que gerou conversa: rode antes o `fora_da_curva.py` com `--metrica comentarios` e pegue os 3 a 5 primeiros.
2. **Colete.**
   - YouTube: `python3 scripts/coletar.py youtube-comentarios <link> --limite 500 --saida c1.csv` (repita por vídeo).
   - Instagram, TikTok e outras: export, prints ou texto colado. Monte um CSV com as colunas `texto,curtidas,fonte`.
3. **Triagem:** `python3 scripts/comentarios.py c1.csv c2.csv --saida rotulados.csv`
   O script tira repetidos e spam de corrente, esconde @ de pessoas citadas e separa por intenção:

| Intenção | Exemplos que ele reconhece |
|---|---|
| quer comprar / preço | "quanto tá?", "passa o link", "faz entrega em BH?", "parcela?", "chama no direct" |
| pergunta | "?", "será que", "alguém sabe", "dá pra" |
| objeção | "caro", "não funciona", "é golpe", "duvido", "mas e se", "já tentei" |
| reclamação | "péssimo", "não chegou", "atrasou", "nunca mais", "reclame aqui" |
| pedido de conteúdo | "faz um vídeo sobre", "parte 2", "ensina", "traz mais" |
| confusão | "não entendi", "como assim", "explica" |
| elogio | "amei", "brabo", "salvou", "muito bom", ❤️ 🔥 👏 |
| humor | kkkk, rsrs, hahaha, 😂 |

   Também marca **possível ironia** ("amei kkkk", "parabéns pelo atraso", "ótimo, só que não"), que não conta como elogio.
4. **Leia de verdade.** A triagem é por regras e erra. Abra `rotulados.csv`, confira os mais curtidos de cada grupo e leia os "outros": costuma ter opinião e história que nenhuma regra pega.
5. **Agrupe em temas** dentro de cada intenção (ex.: em "objeção", o tema "preço" e o tema "não confio que funciona"). Para cada tema: quantos comentários, quantas curtidas somadas e a frase exata que melhor representa.
6. **Transforme em ação:**
   - pergunta repetida → post respondendo + item de FAQ;
   - objeção → argumento para anúncio e página de venda;
   - pedido de conteúdo → pauta pronta (a pessoa já pediu);
   - quer comprar → avise que existe demanda e onde ela aparece;
   - reclamação → encaminhe para atendimento, não para pauta.

## Cuidados

- Um comentário muito curtido não é a opinião de todos. Diga a frequência.
- Cite o texto exato, com gíria e erro de digitação, mas nunca o nome ou @ de quem escreveu.
- Comentário de concorrente, bot ou sorteio ("marca 3 amigos") não entra na leitura.

## Modelo de entrega

```
## O que o público diz: <perfil/post> (N comentários de X posts)
| Intenção | % | Tema principal | Frase exata |
Perguntas que viram post (5)
Objeções e como responder (3)
Pedidos de conteúdo (pautas prontas)
Sinais de compra
```
