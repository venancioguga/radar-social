#!/usr/bin/env python3
"""Radar Social: coleta posts e comentários de fontes oficiais e gratuitas e salva em CSV.

Uso:
  python3 coletar.py youtube-rss <@canal | URL | ID UC...>            (sem chave, 15 vídeos mais recentes)
  python3 coletar.py youtube <@canal | ID UC...> [--limite 200]       (precisa de YOUTUBE_API_KEY)
  python3 coletar.py youtube-comentarios <URL ou ID do vídeo> [--limite 500]
  python3 coletar.py instagram <usuario> [--limite 100]               (precisa de META_ACCESS_TOKEN e IG_BUSINESS_ID)

Todos aceitam --saida arquivo.csv (sem isso, imprime na tela).

CSV de posts:       plataforma,conta,publicado_em,titulo,url,views,likes,comentarios,formato
CSV de comentários: plataforma,fonte,publicado_em,curtidas,respostas,texto
publicado_em sai em UTC (ISO 8601). O horarios.py converte para o fuso que você escolher.
O nome de quem comentou nunca é salvo.

Só usa a biblioteca padrão do Python 3.9+.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

VERSAO = "0.1.0"
UA = f"radar-social/{VERSAO} (+https://github.com/venancioguga/radar-social)"
CAMPOS_POSTS = ["plataforma", "conta", "publicado_em", "titulo", "url", "views", "likes", "comentarios", "formato"]
CAMPOS_COMENTARIOS = ["plataforma", "fonte", "publicado_em", "curtidas", "respostas", "texto"]


def erro(msg):
    sys.exit(f"[radar-social] {msg}")


def baixar(url, tentativas=3):
    """GET com novas tentativas. Devolve o texto da resposta (também em erros 4xx, para ler a mensagem da API)."""
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            corpo = e.read().decode("utf-8", "replace")
            if e.code < 500:
                return corpo
            if i == tentativas - 1:
                erro(f"servidor respondeu {e.code} em {url.split('?')[0]}")
        except Exception as e:  # rede instável
            if i == tentativas - 1:
                erro(f"falha ao acessar {url.split('?')[0]}: {e}")
        time.sleep(2 * (i + 1))


def json_ou_erro(texto, origem):
    try:
        d = json.loads(texto)
    except ValueError:
        erro(f"{origem} devolveu algo que não é JSON")
    if isinstance(d, dict) and "error" in d:
        e = d["error"]
        msg = e.get("message", "erro") if isinstance(e, dict) else str(e)
        erro(f"{origem}: {msg}")
    return d


# ---------------------------------------------------------------- YouTube

ID_CANAL = re.compile(r"UC[\w-]{22}")


def duracao_seg(iso):
    """PT1H2M3S -> 3723"""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def youtube_chave():
    chave = os.environ.get("YOUTUBE_API_KEY")
    if not chave:
        erro("defina YOUTUBE_API_KEY (passo a passo em guias/chaves.md) ou use 'youtube-rss', que não precisa de chave.")
    return chave


def yt(recurso, **params):
    params["key"] = youtube_chave()
    return json_ou_erro(baixar(f"https://www.googleapis.com/youtube/v3/{recurso}?" + urllib.parse.urlencode(params)), "YouTube")


def canal_id_pela_pagina(alvo):
    if ID_CANAL.fullmatch(alvo):
        return alvo
    m = re.search(r"/channel/(UC[\w-]{22})", alvo)
    if m:
        return m.group(1)
    url = alvo if alvo.startswith("http") else "https://www.youtube.com/@" + alvo.lstrip("@")
    html = baixar(url)
    m = re.search(r'"(?:channelId|externalId)":"(UC[\w-]{22})"', html) or re.search(r"channel/(UC[\w-]{22})", html)
    if not m:
        erro("não achei o ID do canal. Passe a URL youtube.com/channel/UC...")
    return m.group(1)


def youtube_rss(alvo, limite):
    cid = canal_id_pela_pagina(alvo)
    raiz = ET.fromstring(baixar(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"))
    ns = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/"}
    conta = raiz.findtext("a:title", default=cid, namespaces=ns)
    linhas = []
    for e in raiz.findall("a:entry", ns):
        link = e.find("a:link", ns).get("href")
        st = e.find("m:group/m:community/m:statistics", ns)
        nota = e.find("m:group/m:community/m:starRating", ns)
        linhas.append({
            "plataforma": "youtube", "conta": conta,
            "publicado_em": e.findtext("a:published", namespaces=ns) or "",
            "titulo": e.findtext("a:title", namespaces=ns) or "", "url": link,
            "views": st.get("views") if st is not None else "",
            "likes": nota.get("count") if nota is not None else "",
            "comentarios": "", "formato": "short" if "/shorts/" in link else "video",
        })
    return linhas[:limite]


def youtube_api(alvo, limite):
    if ID_CANAL.fullmatch(alvo):
        filtro = {"id": alvo}
    else:
        m = re.search(r"/channel/(UC[\w-]{22})", alvo)
        filtro = {"id": m.group(1)} if m else {"forHandle": "@" + alvo.rstrip("/").split("/")[-1].lstrip("@")}
    itens = yt("channels", part="snippet,contentDetails", **filtro).get("items", [])
    if not itens:
        erro("canal não encontrado.")
    conta = itens[0]["snippet"]["title"]
    uploads = itens[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    ids, pagina = [], None
    while len(ids) < limite:
        extra = {"pageToken": pagina} if pagina else {}
        d = yt("playlistItems", part="contentDetails", playlistId=uploads, maxResults=50, **extra)
        ids += [i["contentDetails"]["videoId"] for i in d.get("items", [])]
        pagina = d.get("nextPageToken")
        if not pagina:
            break
    ids = ids[:limite]

    linhas = []
    for i in range(0, len(ids), 50):
        for v in yt("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).get("items", []):
            st = v.get("statistics", {})
            seg = duracao_seg(v["contentDetails"].get("duration"))
            linhas.append({
                "plataforma": "youtube", "conta": conta, "publicado_em": v["snippet"]["publishedAt"],
                "titulo": v["snippet"]["title"], "url": f"https://www.youtube.com/watch?v={v['id']}",
                "views": st.get("viewCount", ""), "likes": st.get("likeCount", ""),
                "comentarios": st.get("commentCount", ""),
                "formato": "short" if seg is not None and seg <= 180 else "video",
            })
    return linhas


def youtube_comentarios(alvo, limite):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|live/)([\w-]{11})", alvo)
    vid = m.group(1) if m else alvo
    fonte = f"https://www.youtube.com/watch?v={vid}"
    linhas, pagina = [], None
    while len(linhas) < limite:
        extra = {"pageToken": pagina} if pagina else {}
        d = yt("commentThreads", part="snippet,replies", videoId=vid, maxResults=100,
               order="relevance", textFormat="plainText", **extra)
        for t in d.get("items", []):
            topo = t["snippet"]["topLevelComment"]["snippet"]
            linhas.append({"plataforma": "youtube", "fonte": fonte, "publicado_em": topo["publishedAt"],
                           "curtidas": topo.get("likeCount", 0), "respostas": t["snippet"].get("totalReplyCount", 0),
                           "texto": topo["textDisplay"]})
            for r in t.get("replies", {}).get("comments", []):
                s = r["snippet"]
                linhas.append({"plataforma": "youtube", "fonte": fonte, "publicado_em": s["publishedAt"],
                               "curtidas": s.get("likeCount", 0), "respostas": "", "texto": s["textDisplay"]})
        pagina = d.get("nextPageToken")
        if not pagina:
            break
    return linhas[:limite]


# ---------------------------------------------------------------- Instagram (Graph API, business discovery)

def instagram(usuario, limite):
    token, minha_conta = os.environ.get("META_ACCESS_TOKEN"), os.environ.get("IG_BUSINESS_ID")
    if not token or not minha_conta:
        erro("defina META_ACCESS_TOKEN e IG_BUSINESS_ID (passo a passo em guias/chaves.md).")
    usuario = usuario.rstrip("/").split("/")[-1].lstrip("@")
    linhas, depois = [], ""
    while len(linhas) < limite:
        pag = f".after({depois})" if depois else ""
        campos = (f"business_discovery.username({usuario}){{followers_count,media{pag}.limit(50)"
                  "{timestamp,like_count,comments_count,media_type,media_product_type,permalink,caption}}")
        url = f"https://graph.facebook.com/v21.0/{minha_conta}?" + urllib.parse.urlencode({"fields": campos, "access_token": token})
        media = json_ou_erro(baixar(url), "Meta").get("business_discovery", {}).get("media", {})
        for m in media.get("data", []):
            if m.get("media_product_type") == "REELS":
                fmt = "reel"
            elif m.get("media_type") == "CAROUSEL_ALBUM":
                fmt = "carrossel"
            else:
                fmt = "post"
            linhas.append({
                "plataforma": "instagram", "conta": "@" + usuario, "publicado_em": m.get("timestamp", ""),
                "titulo": (m.get("caption") or "").strip().split("\n")[0][:140], "url": m.get("permalink", ""),
                "views": "", "likes": m.get("like_count", ""), "comentarios": m.get("comments_count", ""), "formato": fmt,
            })
        depois = media.get("paging", {}).get("cursors", {}).get("after")
        if not depois or not media.get("data"):
            break
    return linhas[:limite]


# ---------------------------------------------------------------- saída

def salvar(linhas, campos, saida):
    if not linhas:
        erro("nada coletado.")
    f = open(saida, "w", newline="", encoding="utf-8") if saida else sys.stdout
    w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
    w.writeheader()
    w.writerows(linhas)
    if saida:
        f.close()
        print(f"{len(linhas)} linhas salvas em {saida}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Coleta dados públicos para o Radar Social.")
    ap.add_argument("fonte", choices=["youtube-rss", "youtube", "youtube-comentarios", "instagram"])
    ap.add_argument("alvo", help="@canal, usuário, URL ou ID")
    ap.add_argument("--limite", type=int, default=100)
    ap.add_argument("--saida", help="arquivo .csv de saída")
    a = ap.parse_args()

    if a.fonte == "youtube-comentarios":
        salvar(youtube_comentarios(a.alvo, a.limite), CAMPOS_COMENTARIOS, a.saida)
        return
    coleta = {"youtube-rss": youtube_rss, "youtube": youtube_api, "instagram": instagram}[a.fonte]
    salvar(coleta(a.alvo, a.limite), CAMPOS_POSTS, a.saida)


if __name__ == "__main__":
    main()
