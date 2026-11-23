#!/usr/bin/env python3
"""Radar Social: em que dia e horário os posts de um perfil costumam render mais.

Uso:
  python3 horarios.py posts.csv [--metrica views|likes|comentarios|engajamento]
                      [--fuso America/Sao_Paulo] [--min-posts 3]

Cada post é comparado com a mediana da própria conta e formato (igual ao fora_da_curva.py).
Depois o script olha a mediana desse "vezes a base" por dia da semana e por faixa de horário.
Acima de 1,0 = costuma render mais que o normal do perfil; abaixo = menos.

Precisa da coluna publicado_em com horário (o coletar.py já entrega). Fuso padrão: Brasília.
Outros fusos comuns: America/Manaus, America/Noronha, Europe/Lisbon.
Lembrete honesto: horário explica pouco perto de tema e gancho. Use como desempate.
"""
import argparse
import csv
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
FAIXAS = [(0, 6, "madrugada (0h-6h)"), (6, 9, "cedo (6h-9h)"), (9, 12, "manhã (9h-12h)"), (12, 14, "almoço (12h-14h)"),
          (14, 18, "tarde (14h-18h)"), (18, 21, "noite (18h-21h)"), (21, 24, "fim da noite (21h-0h)")]


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


def faixa_hora(h):
    return next(nome for ini, fim, nome in FAIXAS if ini <= h < fim)


def tabela(titulo, grupos, ordem, min_posts):
    print(f"\n## {titulo}\n\n| | Posts | Rende (mediana de vezes a base) | Leitura |\n|---|---:|---:|---|")
    for k in ordem:
        xs = grupos.get(k, [])
        if not xs:
            continue
        if len(xs) < min_posts:
            print(f"| {k} | {len(xs)} | - | poucos posts |")
            continue
        m = statistics.median(xs)
        leitura = "acima do normal" if m >= 1.2 else "abaixo do normal" if m <= 0.8 else "na média"
        print(f"| {k} | {len(xs)} | {m:.2f}x | {leitura} |".replace(".", ","))


def main():
    ap = argparse.ArgumentParser(description="Melhor dia e horário de um perfil, pelos próprios dados.")
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--metrica", default=None)
    ap.add_argument("--fuso", default="America/Sao_Paulo")
    ap.add_argument("--min-posts", type=int, default=3)
    a = ap.parse_args()

    linhas = []
    for arq in a.csv:
        with open(arq, encoding="utf-8-sig") as f:
            linhas += list(csv.DictReader(f))
    metrica = a.metrica or ("views" if any(num(l.get("views")) for l in linhas) else "engajamento")
    fuso = ZoneInfo(a.fuso)

    por_grupo = defaultdict(list)
    for l in linhas:
        v, quando = valor(l, metrica), (l.get("publicado_em") or "").strip()
        if v is None or len(quando) < 16:  # precisa de data E hora
            continue
        d = datetime.fromisoformat(quando.replace("Z", "+00:00"))
        if d.tzinfo is None:
            continue
        por_grupo[(l.get("conta", ""), l.get("formato", ""))].append((v, d.astimezone(fuso)))
    if not por_grupo:
        sys.exit("Sem posts com data e hora (coluna publicado_em). Colete com o coletar.py.")

    contas = sorted({c for c, _ in por_grupo})
    for conta in contas:
        dia, hora, total = defaultdict(list), defaultdict(list), 0
        for (c, fmt), itens in por_grupo.items():
            if c != conta:
                continue
            base = statistics.median(v for v, _ in itens)
            if base <= 0:
                continue
            for v, d in itens:
                dia[DIAS[d.weekday()]].append(v / base)
                hora[faixa_hora(d.hour)].append(v / base)
                total += 1
        print(f"# Quando posta melhor: {conta}\n\n{total} posts · métrica: {metrica} · fuso: {a.fuso}")
        tabela("Por dia da semana", dia, DIAS, a.min_posts)
        tabela("Por horário", hora, [n for _, _, n in FAIXAS], a.min_posts)
        print()


if __name__ == "__main__":
    main()
