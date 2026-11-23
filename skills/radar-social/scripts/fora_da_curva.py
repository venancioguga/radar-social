#!/usr/bin/env python3
"""Radar Social: acha os posts que foram muito acima do normal do próprio perfil.

Uso:
  python3 fora_da_curva.py posts.csv [mais.csv ...] [--metrica views|likes|comentarios|engajamento]
                           [--min 1.5] [--top 15] [--idade-min 3] [--json]

Como funciona:
  1. Separa os posts por conta + rede + formato (short não compete com vídeo longo, reel não compete com carrossel).
  2. A "base" de cada grupo é a MEDIANA da métrica (não a média: um viral não distorce a régua).
  3. Cada post recebe "vezes a base" = métrica do post / base.
  4. Posts com menos de --idade-min dias ficam de fora da conta (ainda estão acumulando) e aparecem
     numa lista separada, para não enganar.

Faixas: 5x ou mais = explodiu · 2x a 5x = forte · 1,5x a 2x = acima do normal.
Confiança: 20+ posts = alta · 10 a 19 = média · menos de 10 = baixa.

Aceita CSV do coletar.py ou qualquer export com as colunas conta, url e a métrica
(plataforma, formato, titulo e publicado_em/data são opcionais).
"""
import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone


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


def quando(linha):
    v = (linha.get("publicado_em") or linha.get("data") or "").strip()
    if not v:
        return None
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        try:
            d = datetime.strptime(v[:10], "%d/%m/%Y")
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def valor(linha, metrica):
    if metrica == "engajamento":
        partes = [num(linha.get(k)) for k in ("likes", "comentarios", "compartilhamentos", "salvos")]
        partes = [p for p in partes if p is not None]
        return sum(partes) if partes else None
    return num(linha.get(metrica))


def br(n):
    """1234567 -> 1.234.567"""
    return f"{n:,.0f}".replace(",", ".")


def faixa(x):
    return "explodiu" if x >= 5 else "forte" if x >= 2 else "acima do normal" if x >= 1.5 else ""


def confianca(n):
    return "alta" if n >= 20 else "média" if n >= 10 else "baixa"


def main():
    ap = argparse.ArgumentParser(description="Posts fora da curva, comparando cada post com a mediana do próprio perfil.")
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--metrica", default=None, help="views, likes, comentarios ou engajamento (padrão: views se houver, senão engajamento)")
    ap.add_argument("--min", type=float, default=1.5, help="mínimo de vezes a base para entrar na lista")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--idade-min", type=float, default=3, help="dias mínimos de vida para entrar na conta")
    ap.add_argument("--json", action="store_true", help="saída em JSON em vez de markdown")
    a = ap.parse_args()

    linhas = []
    for arq in a.csv:
        with open(arq, encoding="utf-8-sig") as f:
            linhas += list(csv.DictReader(f))
    if not linhas:
        sys.exit("CSV vazio.")

    metrica = a.metrica or ("views" if any(num(l.get("views")) for l in linhas) else "engajamento")
    agora = datetime.now(timezone.utc)

    grupos, recentes = defaultdict(list), defaultdict(list)
    for l in linhas:
        v = valor(l, metrica)
        if v is None:
            continue
        chave = (l.get("conta", ""), l.get("plataforma", ""), l.get("formato", "") or "todos")
        d = quando(l)
        idade = (agora - d).total_seconds() / 86400 if d else None
        (recentes if idade is not None and idade < a.idade_min else grupos)[chave].append((v, l, d))

    if not grupos:
        sys.exit(f"Nenhuma linha com a métrica '{metrica}'. Tente --metrica likes ou engajamento.")

    resultado = []
    for chave in sorted(grupos):
        itens = grupos[chave]
        base = statistics.median(v for v, _, _ in itens)
        g = {"conta": chave[0], "plataforma": chave[1], "formato": chave[2], "amostra": len(itens),
             "base_mediana": base, "confianca": confianca(len(itens)), "metrica": metrica, "posts": [], "recentes": []}
        datas = [d for _, _, d in itens if d]
        if datas:
            g["periodo"] = f"{min(datas):%d/%m/%Y} a {max(datas):%d/%m/%Y}"
        if base > 0:
            tops = sorted(((v / base, v, l, d) for v, l, d in itens if v / base >= a.min), key=lambda t: t[0], reverse=True)
            for x, v, l, d in tops[:a.top]:
                g["posts"].append({"vezes_base": round(x, 1), "faixa": faixa(x), "valor": v, "titulo": l.get("titulo", ""),
                                   "url": l.get("url", ""), "data": f"{d:%d/%m/%Y}" if d else ""})
            novos = recentes.get(chave, [])
            g["recentes_total"] = len(novos)
            for v, l, d in sorted(novos, key=lambda t: t[0], reverse=True):
                if v / base >= a.min:  # sinal precoce: já passou da régua antes de completar a idade mínima
                    g["recentes"].append({"vezes_base_ate_agora": round(v / base, 1), "titulo": l.get("titulo", ""), "url": l.get("url", "")})
        resultado.append(g)

    if a.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return

    print(f"# Posts fora da curva (métrica: {metrica})\n")
    for g in resultado:
        print(f"## {g['conta']} · {g['plataforma']} · {g['formato']}")
        print(f"Amostra: {g['amostra']} posts{' (' + g['periodo'] + ')' if g.get('periodo') else ''} · "
              f"base (mediana): {br(g['base_mediana'])} · confiança: {g['confianca']}")
        if g["base_mediana"] <= 0:
            print("\nBase zero: não dá para comparar este grupo.\n")
            continue
        if not g["posts"]:
            print(f"\nNenhum post chegou a {a.min}x a base.\n")
        else:
            print("\n| # | Post | Data | " + metrica.capitalize() + " | Vezes a base | Faixa |")
            print("|---:|---|---|---:|---:|---|")
            for i, p in enumerate(g["posts"], 1):
                t = (p["titulo"] or "(sem título)").replace("|", "/").replace("\n", " ")[:90]
                print(f"| {i} | [{t}]({p['url']}) | {p['data']} | {br(p['valor'])} | {str(p['vezes_base']).replace('.', ',')}x | {p['faixa']} |")
            print()
        if g["recentes"]:
            print(f"Sinal precoce: {len(g['recentes'])} de {g['recentes_total']} posts com menos de {a.idade_min:g} dias "
                  "já passaram da régua (ainda acumulando, ficaram fora da base):")
            for r in g["recentes"]:
                print(f"- [{(r['titulo'] or '(sem título)')[:80]}]({r['url']}): {str(r['vezes_base_ate_agora']).replace('.', ',')}x a base até agora")
            print()


if __name__ == "__main__":
    main()
