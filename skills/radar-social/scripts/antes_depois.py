#!/usr/bin/env python3
"""Radar Social: compara o desempenho de um perfil antes e depois de uma data.

Uso:
  python3 antes_depois.py posts.csv --corte 2026-10-01 [--metrica views|likes|comentarios|engajamento]
                          [--fim 2026-11-30] [--dias 60]

Serve para responder "a campanha / a mudança de estratégia / o novo formato funcionou?".
Para cada conta mostra, antes e depois do corte: número de posts, posts por semana,
mediana da métrica, total e a variação. Também mostra a mistura de formatos.

--dias limita cada lado aos N dias mais próximos do corte (padrão 60), para comparar períodos parecidos.
Cuidado: posts recentes ainda estão acumulando. O script avisa quando o lado "depois" tem posts com menos de 3 dias.
"""
import argparse
import csv
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(" ", "")
    if not s:
        return None
    s = s.lower().replace("mil", "k")
    mult = 1
    if s.endswith("k"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1_000_000, s[:-1]
    # 1.234.567 (pt-BR) ou 1,234,567 (en) -> 1234567 ; 12,5 -> 12.5
    if (s.count(".") > 1 or (s.count(".") == 1 and s.count(",") == 1 and s.index(".") < s.index(","))
            or (s.count(".") == 1 and "," not in s and len(s.split(".")[1]) == 3 and mult == 1)):
        s = s.replace(".", "").replace(",", ".")
    elif s.count(",") > 1 or (s.count(",") == 1 and len(s.split(",")[1]) == 3 and mult == 1):
        s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        return float(s) * mult
    except ValueError:
        return None


def valor(l, metrica):
    if metrica == "engajamento":
        p = [num(l.get(k)) for k in ("likes", "comentarios", "compartilhamentos", "salvos")]
        p = [x for x in p if x is not None]
        return sum(p) if p else None
    return num(l.get(metrica))


def data(l):
    v = (l.get("publicado_em") or l.get("data") or "").strip()
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def br(n, casas=0):
    return f"{n:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def resumo(itens, dias):
    vals = [v for v, _, _ in itens]
    return {"posts": len(vals), "por_semana": len(vals) / (dias / 7) if dias else 0,
            "mediana": statistics.median(vals) if vals else 0, "total": sum(vals),
            "formatos": Counter(f or "?" for _, _, f in itens)}


def var(a, b):
    if a == 0:
        return "-"
    p = 100 * (b - a) / a
    return ("+" if p >= 0 else "") + br(p) + "%"


def main():
    ap = argparse.ArgumentParser(description="Antes x depois de uma data.")
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--corte", required=True, help="AAAA-MM-DD: primeiro dia do 'depois'")
    ap.add_argument("--fim", help="AAAA-MM-DD: último dia do 'depois' (padrão: hoje)")
    ap.add_argument("--dias", type=int, default=60)
    ap.add_argument("--metrica", default=None)
    a = ap.parse_args()

    corte = datetime.fromisoformat(a.corte).replace(tzinfo=timezone.utc)
    fim = datetime.fromisoformat(a.fim).replace(tzinfo=timezone.utc) + timedelta(days=1) if a.fim else datetime.now(timezone.utc)
    dias_depois = min(a.dias, max(1, (fim - corte).days))
    ini = corte - timedelta(days=dias_depois)
    fim_depois = corte + timedelta(days=dias_depois)

    linhas = []
    for arq in a.csv:
        with open(arq, encoding="utf-8-sig") as f:
            linhas += list(csv.DictReader(f))
    metrica = a.metrica or ("views" if any(num(l.get("views")) for l in linhas) else "engajamento")
    agora = datetime.now(timezone.utc)

    lados = defaultdict(lambda: {"antes": [], "depois": []})
    novos = Counter()
    for l in linhas:
        v, d = valor(l, metrica), data(l)
        if v is None or d is None or d < ini or d >= min(fim, fim_depois):
            continue
        lado = "antes" if d < corte else "depois"
        lados[l.get("conta", "")][lado].append((v, d, l.get("formato", "")))
        if lado == "depois" and (agora - d).days < 3:
            novos[l.get("conta", "")] += 1
    if not lados:
        sys.exit("Nenhum post no período. Confira --corte e a coluna publicado_em.")

    print(f"# Antes x depois de {corte:%d/%m/%Y}\n\nMétrica: {metrica} · {dias_depois} dias de cada lado "
          f"({ini:%d/%m/%Y} a {corte - timedelta(days=1):%d/%m/%Y} contra {corte:%d/%m/%Y} a {min(fim, fim_depois) - timedelta(days=1):%d/%m/%Y})")
    for conta, l in sorted(lados.items()):
        A, B = resumo(l["antes"], dias_depois), resumo(l["depois"], dias_depois)
        print(f"\n## {conta}\n\n| | Antes | Depois | Variação |\n|---|---:|---:|---:|")
        print(f"| Posts | {A['posts']} | {B['posts']} | {var(A['posts'], B['posts'])} |")
        print(f"| Posts por semana | {br(A['por_semana'], 1)} | {br(B['por_semana'], 1)} | {var(A['por_semana'], B['por_semana'])} |")
        print(f"| Mediana por post | {br(A['mediana'])} | {br(B['mediana'])} | {var(A['mediana'], B['mediana'])} |")
        print(f"| Total no período | {br(A['total'])} | {br(B['total'])} | {var(A['total'], B['total'])} |")
        fmts = sorted(set(A["formatos"]) | set(B["formatos"]))
        print("\nMistura de formatos: " + " · ".join(f"{f}: {A['formatos'][f]} → {B['formatos'][f]}" for f in fmts))
        if min(A["posts"], B["posts"]) < 5:
            print("Atenção: menos de 5 posts em um dos lados, conclusão fraca.")
        if novos[conta]:
            print(f"Atenção: {novos[conta]} post(s) do 'depois' têm menos de 3 dias e ainda estão crescendo.")


if __name__ == "__main__":
    main()
