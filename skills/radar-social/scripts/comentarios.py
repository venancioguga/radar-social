#!/usr/bin/env python3
"""Radar Social: primeira leitura de comentários em português do Brasil.

Uso:
  python3 comentarios.py comentarios.csv [mais.csv ...] [--exemplos 5] [--saida rotulados.csv] [--json]

Lê um CSV com a coluna "texto" (e, se houver, "curtidas" e "fonte") e:
  - separa por intenção: pergunta, quer comprar / preço, objeção, reclamação, pedido de conteúdo,
    confusão, elogio, humor (um comentário pode ter mais de uma);
  - marca possível ironia ("amei kkkkk", "ótimo, só que não", "parabéns pelo atraso");
  - entende escrita de internet: vc, pq, q, tb, mds, pfv, kkkk, rsrs, sqn, "quanto tá", "passa o link";
  - lista os termos e expressões que mais se repetem;
  - mostra os comentários mais curtidos de cada grupo, com o texto exato.

É uma triagem por regras, rápida e auditável. A leitura final (temas, tom, o que fazer)
é do agente ou de quem está analisando: use --saida para revisar linha a linha.
Nenhum nome de quem comentou é usado ou exibido.
"""
import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def normalizar(t):
    t = sem_acento(t.lower())
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"@\w+", " ", t)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)  # "muuuuito" -> "muuito", "kkkkkk" -> "kk"
    trocas = {r"\bvc[s]?\b": "voce", r"\bpq\b": "porque", r"\bq\b": "que", r"\btb[m]?\b": "tambem",
              r"\bmds\b": "meu deus", r"\bpfv\b|\bpf\b|\bplmds\b": "por favor", r"\bn\b": "nao",
              r"\bblz\b": "beleza", r"\bmt[o]?\b": "muito", r"\bcmg\b": "comigo", r"\bctz\b": "certeza",
              r"\bvdd\b": "verdade", r"\bqnd[o]?\b": "quando", r"\bqto\b|\bqnt[o]?\b": "quanto", r"\bta\b": "esta",
              r"\bdps\b": "depois", r"\bhj\b": "hoje", r"\bobg\b|\bobgd[a]?\b": "obrigado", r"\bslk\b": "nossa"}
    for padrao, troca in trocas.items():
        t = re.sub(padrao, troca, t)
    return re.sub(r"\s+", " ", t).strip()


# Cada intenção: lista de padrões (regex sobre o texto normalizado, sem acento).
INTENCOES = {
    "quer comprar / preço": [
        r"\bquanto (custa|e|sai|fica|esta|cobra)", r"\bvalor\b", r"\bpreco", r"\bonde (compr|acho|encontr|vend)",
        r"\b(passa|manda|tem|cade) (o )?link", r"\blink\b.*\?", r"\bquero (um|uma|o|a|comprar|esse|essa)\b",
        r"\bvende[ms]?\b", r"\bparcel", r"\bfrete\b", r"\bentrega(m)? (em|no|na|pra)\b", r"\bpix\b", r"\bcupom\b",
        r"\bchama (no|na) (dm|direct|privado|inbox)", r"\bme (chama|manda) (no|na|o)\b", r"\bcomo (faco|faz) (pra|para) (comprar|pedir|agendar|contratar)",
        r"\bagend", r"\borcamento\b",
    ],
    "pergunta": [
        r"\?", r"\b(sera que|tem como|da pra|alguem (sabe|ja|tem|conhece|explica)|(queria|gostaria de) saber|me explica|minha duvida|uma duvida)\b",
    ],
    "objeção": [
        r"\bcaro\b|\bcarissimo\b|\bsalgado\b", r"\bnao (funciona|vale|compensa|confio|acredito)", r"\bgolpe\b|\bfake\b|\bmentira\b|\benganacao\b",
        r"\bduvido\b", r"\bmas e (se|o|a|quem)\b", r"\bnao e (bem|tudo) (assim|isso)", r"\bja tentei\b", r"\bnao serve\b",
        r"\bpropaganda (enganosa)?\b", r"\bpatrocinad", r"\bjabá\b|\bjaba\b", r"\bnao tenho (dinheiro|tempo)\b",
    ],
    "reclamação": [
        r"\bpessim|\bhorrivel|\bridicul|\b(que|um|uma|isso e|esse|essa|e um) lixo\b|\blixo de\b|\bvergonha\b", r"\bnao (chegou|recebi|funcionou|responde|atende)",
        r"\batraso\b|\batrasou\b|\b(chegou|veio|entregaram|entrega) atrasad", r"\bnunca mais\b", r"\bdecepcion", r"\bdescaso\b", r"\bprocon\b|\breclame aqui\b",
        r"\bcancel", r"\breembolso\b|\bdevolu", r"\bestorno\b", r"\bpiorou\b",
    ],
    "pedido de conteúdo": [
        r"\bfaz (um|uma|o|a|mais|sobre|video|post)\b", r"\bfala sobre\b", r"\btraz (mais|um|uma|o|a)\b", r"\bensina\b",
        r"\bparte 2\b|\bpt 2\b|\bcontinua(cao)?\b", r"\bmais (videos?|conteudos?|posts?) (assim|sobre|como)",
        r"\b(podia|poderia|deveria) (fazer|falar|mostrar|trazer)", r"\btutorial\b", r"\bpasso a passo\b",
    ],
    "confusão": [
        r"\bnao entendi\b", r"\bcomo assim\b", r"\bexplica\b", r"\bfiquei (confus|perdid|sem entender)", r"\bboiei\b",
        r"\bque\?+$", r"\bhein\b", r"\bnao ficou claro\b",
    ],
    "elogio": [
        r"\bameii?\b|\bamo\b|\bapaixon", r"\bperfeit|\bincrive|\bsensacional|\bmaravilh|\blind[oa]\b|\bfod[ae]\b|\bbrabo\b|\bbraba\b",
        r"\btop\b|\bshow\b|\bmassa\b|\bmuito bom\b|\bmuito boa\b|\bexcelente\b|\bespetacular\b", r"\bparabens\b",
        r"\bobrigad|\bajudou\b|\bsalvou\b|\bmelhor (video|conteudo|canal|perfil|post)", r"\bconteudo (top|incrivel|bom)",
        "[❤\U0001F60D\U0001F970\U0001F44F\U0001F525\U0001F64C\U0001F499\U0001F49C\U0001F5A4✨]",
    ],
    "humor": [r"\bkk\b|\bkkk", r"\brsrs\b|\brs\b", r"\bhaha|\bhuehue|\bkakak", "[\U0001F602\U0001F923\U0001F606\U0001F605]", r"\bmorri\b|\bchorando\b"],
}
INTENCOES_RE = {k: [re.compile(p) for p in v] for k, v in INTENCOES.items()}

IRONIA = [re.compile(p) for p in (
    r"\b(so que nao|sqn)\b",
    r"\b(otimo|parabens|adorei|amei|maravilha|lindo|show)\b[^.!?]*\b(kk|rs)\b",
    r"\b(parabens|obrigado) (pelo|pela|por) (atraso|descaso|nada|falta|pessimo|golpe)",
    r"\bclaro que (sim|nao)\b.*\b(kk|rs)\b",
    r"\bque (otimo|lindo|maravilha)\b.*\b(ne|neh)\b",
)]

PARADAS = set(sem_acento("""a o e é de da do das dos que em um uma uns umas pra para por com sem no na nos nas ao aos à às
se eu tu ele ela nos nós vos eles elas me te lhe mim ti meu minha seu sua isso isto esse essa este esta aquilo
mais muito muita muitos muitas mas ou nem já ja tá ta tô to ser foi era sou são vai vou tem ter tinha
também tambem só so não nao sim como quando onde porque voce voces vcs gente aqui ali lá la então entao
bem até ate ainda sobre todo toda todos todas cada qual quais quem kk rs nossa meu deus""").split())


def termos(texto_norm):
    palavras = [p for p in re.findall(r"[a-z0-9]+", texto_norm) if len(p) > 2 and p not in PARADAS]
    pares = [f"{a} {b}" for a, b in zip(palavras, palavras[1:])]
    return palavras, pares


def classificar(texto):
    t = normalizar(texto)
    rotulos = [k for k, padroes in INTENCOES_RE.items() if any(p.search(t) for p in padroes)]
    # pergunta de preço já está em "quer comprar"; não contar duas vezes como dúvida genérica
    if "quer comprar / preço" in rotulos and "pergunta" in rotulos:
        rotulos.remove("pergunta")
    ironia = any(p.search(t) for p in IRONIA)
    if ironia and "elogio" in rotulos:
        rotulos.remove("elogio")
    return rotulos or ["outros"], ironia, t


def inteiro(v):
    try:
        return int(float(str(v).replace(".", "").replace(",", "") or 0))
    except ValueError:
        return 0


def main():
    ap = argparse.ArgumentParser(description="Triagem de comentários em pt-BR.")
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--exemplos", type=int, default=5, help="comentários de exemplo por grupo")
    ap.add_argument("--saida", help="salva um CSV com os rótulos de cada comentário para revisão")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    linhas = []
    for arq in a.csv:
        with open(arq, encoding="utf-8-sig") as f:
            linhas += list(csv.DictReader(f))
    vistos, limpos = set(), []
    for l in linhas:
        texto = re.sub(r"[\u200b-\u200f\ufeff]", "", l.get("texto") or l.get("comentario") or l.get("text") or "").strip()
        texto = re.sub(r"@[\w.\-]+", "@pessoa", texto)  # não expor quem foi citado
        chave = normalizar(texto)
        if len(chave) < 2 or chave in vistos:  # vazio ou duplicado (spam, corrente)
            continue
        vistos.add(chave)
        limpos.append(dict(l, texto=texto))
    if not limpos:
        sys.exit("Nenhum comentário com texto. O CSV precisa da coluna 'texto'.")

    grupos, ironicos = defaultdict(list), []
    cont_termos, cont_pares = Counter(), Counter()
    for l in limpos:
        rotulos, ironia, norm = classificar(l["texto"])
        l["intencoes"], l["ironia"] = "; ".join(rotulos), "sim" if ironia else ""
        for r in rotulos:
            grupos[r].append(l)
        if ironia:
            ironicos.append(l)
        palavras, pares = termos(norm)
        cont_termos.update(set(palavras))
        cont_pares.update(set(pares))

    total = len(limpos)
    ordem = sorted(grupos, key=lambda k: (k == "outros", -len(grupos[k])))
    curt = lambda l: inteiro(l.get("curtidas"))

    if a.saida:
        campos = list(limpos[0].keys())
        with open(a.saida, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
            w.writeheader()
            w.writerows(sorted(limpos, key=curt, reverse=True))
        print(f"{total} comentários rotulados em {a.saida}", file=sys.stderr)

    if a.json:
        print(json.dumps({
            "total": total, "descartados_vazios_ou_duplicados": len(linhas) - total,
            "intencoes": {k: {"qtd": len(grupos[k]), "pct": round(100 * len(grupos[k]) / total, 1),
                              "exemplos": [{"texto": l["texto"], "curtidas": curt(l), "fonte": l.get("fonte", "")}
                                           for l in sorted(grupos[k], key=curt, reverse=True)[:a.exemplos]]} for k in ordem},
            "possivel_ironia": [l["texto"] for l in ironicos[:a.exemplos]],
            "termos": cont_termos.most_common(20), "expressoes": [p for p in cont_pares.most_common(20) if p[1] > 1],
        }, ensure_ascii=False, indent=2))
        return

    print(f"# Comentários: triagem\n\n{total} comentários únicos ({len(linhas) - total} vazios ou repetidos descartados).\n")
    print("| Intenção | Qtd | % |\n|---|---:|---:|")
    for k in ordem:
        print(f"| {k} | {len(grupos[k])} | {100 * len(grupos[k]) / total:.0f}% |".replace(".", ","))
    if ironicos:
        print(f"\nPossível ironia: {len(ironicos)} (conferir antes de contar como elogio).")
    for k in ordem:
        if k == "outros":
            continue
        print(f"\n## {k} ({len(grupos[k])})")
        for l in sorted(grupos[k], key=curt, reverse=True)[:a.exemplos]:
            t = l["texto"].replace("\n", " ")[:220]
            print(f"- \"{t}\" ({curt(l)} curtidas)")
    if ironicos:
        print("\n## possível ironia")
        for l in ironicos[:a.exemplos]:
            print(f"- \"{l['texto'][:220]}\"")
    pares = [p for p in cont_pares.most_common(15) if p[1] > 1]
    print("\n## O que mais se repete")
    print("Palavras: " + ", ".join(f"{p} ({n})" for p, n in cont_termos.most_common(15)))
    if pares:
        print("Expressões: " + ", ".join(f"\"{p}\" ({n})" for p, n in pares))


if __name__ == "__main__":
    main()
