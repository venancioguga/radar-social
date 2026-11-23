# Chaves gratuitas: passo a passo

O Radar Social não usa serviço pago. Cada pessoa cria as próprias chaves, de graça, direto no Google e na Meta. As chaves ficam no seu computador, em variáveis de ambiente, e nunca vão para o código nem para a conversa.

## YouTube (5 minutos)

1. Entre em console.cloud.google.com com qualquer conta Google e crie um projeto (ex.: "radar-social").
2. Menu "APIs e serviços" > "Biblioteca" > procure **YouTube Data API v3** > Ativar.
3. "APIs e serviços" > "Credenciais" > "Criar credenciais" > "Chave de API".
4. Clique na chave criada > "Restrições de API" > marque só YouTube Data API v3 > Salvar.
5. No terminal (Mac/Linux), adicione ao arquivo `~/.zshrc` ou `~/.bashrc`:
   ```
   export YOUTUBE_API_KEY="cole-a-chave-aqui"
   ```
   No Windows (PowerShell): `setx YOUTUBE_API_KEY "cole-a-chave-aqui"`. Abra um terminal novo.

Cota grátis: 10 mil unidades por dia. Ler 200 vídeos de um canal gasta perto de 10 unidades, e cada 100 comentários gastam 1. Dá para centenas de canais por dia. Não precisa de cartão.

Sem chave nenhuma, `coletar.py youtube-rss @canal` já traz os 15 vídeos mais recentes.

## Instagram (15 minutos, uma vez)

A API oficial da Meta deixa ver posts, curtidas e comentários de qualquer conta **comercial ou de criador**, usando a sua própria conta profissional como porta de entrada. Não mostra views de outras contas nem contas pessoais.

Você precisa de: uma conta do Instagram profissional (comercial ou criador) ligada a uma Página do Facebook.

1. Em developers.facebook.com, "Meus apps" > "Criar app" > tipo "Empresa".
2. No app, adicione o produto **Instagram Graph API** (ou "API do Instagram com login do Facebook").
3. Abra o "Explorador da Graph API" (Ferramentas > Graph API Explorer), escolha o seu app e gere um token com as permissões `instagram_basic`, `pages_show_list` e `business_management`.
4. Ainda no explorador, rode `me/accounts?fields=instagram_business_account{id,username}` e copie o `id` da sua conta do Instagram.
5. Para o token não vencer em poucas horas: no Gerenciador de Negócios (business.facebook.com) > Configurações > Usuários do sistema, crie um usuário do sistema, dê acesso ao app e à página e gere o token por lá.
6. No terminal:
   ```
   export META_ACCESS_TOKEN="token"
   export IG_BUSINESS_ID="id-da-sua-conta-instagram"
   ```

Teste: `python3 scripts/coletar.py instagram nasa --limite 10`

## Biblioteca de Anúncios da Meta

Pela interface (facebook.com/ads/library) é livre e não precisa de nada. Pela API, a Meta pede uma confirmação de identidade única em facebook.com/ads/library/api. Até lá, o roteiro de concorrentes usa a interface.

## Segurança

- Restrinja cada chave ao serviço que ela usa.
- Não suba arquivo com chave para o GitHub. Se vazar, apague a chave no painel e crie outra.
- Não cole chave no chat com a IA. O script lê do ambiente.
