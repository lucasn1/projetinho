# 🤖 Instagram Comment Bot

Bot em Python para monitorar comentários no Instagram e enviar respostas automáticas + DMs.

## 📋 O que este bot faz

- ✅ Monitora comentários em posts específicos do seu Instagram
- ✅ Responde automaticamente aos comentários
- ✅ Envia DM para quem comentou
- ✅ Funciona 24/7 (quando hospedado em um servidor)

## 🔧 Pré-requisitos

1. **Conta Instagram Business ou Creator**
2. **Página do Facebook** vinculada à conta do Instagram
3. **Aplicativo no Meta for Developers**
4. **Servidor com HTTPS** (necessário para webhooks)

---

## 🚀 Passo a Passo de Configuração

### PASSO 1: Converter conta para Business/Creator

Se sua conta ainda é pessoal:

1. Vá em **Configurações** > **Conta** > **Mudar para conta profissional**
2. Escolha **Creator** ou **Business**
3. Siga as instruções

### PASSO 2: Criar Página no Facebook e vincular

1. Crie uma página no Facebook (se não tiver): [facebook.com/pages/create](https://facebook.com/pages/create)
2. No Instagram, vá em **Configurações** > **Conta** > **Compartilhamento em outros aplicativos** > **Facebook**
3. Vincule sua conta à página do Facebook

### PASSO 3: Criar aplicativo no Meta for Developers

1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Clique em **Meus Aplicativos** > **Criar Aplicativo**
3. Escolha **Outro** > **Avançar**
4. Escolha **Empresa** como tipo
5. Dê um nome ao app e crie

### PASSO 4: Configurar produtos do app

No painel do seu app:

1. Clique em **Adicionar Produto**
2. Adicione:
   - **Instagram** (Instagram Graph API)
   - **Webhooks**

### PASSO 5: Configurar permissões

Em **Permissões da API do Instagram**, solicite:

- `instagram_basic` - Acesso básico à conta
- `instagram_manage_comments` - Gerenciar comentários
- `instagram_manage_messages` - Enviar mensagens
- `pages_manage_metadata` - Gerenciar páginas
- `pages_read_engagement` - Ler engajamento

> ⚠️ Algumas permissões requerem **verificação do app** para uso em produção

### PASSO 6: Gerar Access Token

1. Vá em **Ferramentas** > **Graph API Explorer**
2. Selecione seu aplicativo
3. Clique em **Gerar Token de Acesso**
4. Selecione sua página do Facebook
5. Conceda todas as permissões necessárias
6. Copie o token gerado

> 💡 Para um token de longa duração, use a ferramenta de Tokens de Acesso ou a API

### PASSO 7: Obter Instagram Account ID

No Graph API Explorer, faça esta requisição:

```
GET /me/accounts
```

Isso retorna suas páginas. Depois, para cada página:

```
GET /{page-id}?fields=instagram_business_account
```

O `instagram_business_account.id` é seu **INSTAGRAM_ACCOUNT_ID**.

### PASSO 8: Configurar o projeto

```bash
# Clonar/baixar o projeto
cd instagram-bot

# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### PASSO 9: Configurar Webhook no Meta

1. Deploy seu app em um servidor com HTTPS (veja opções abaixo)
2. No Meta for Developers, vá em **Webhooks**
3. Clique em **Adicionar Assinatura** para **Instagram**
4. Configure:
   - **URL de retorno**: `https://seu-servidor.com/webhook`
   - **Token de verificação**: O mesmo que você colocou no `.env` (VERIFY_TOKEN)
5. Assine os campos:
   - `comments` - Para receber notificações de comentários

---

## 🖥️ Opções de Hospedagem

### Opção 1: Railway (Recomendado para iniciantes)

1. Crie conta em [railway.app](https://railway.app)
2. Conecte seu GitHub
3. Crie novo projeto e importe o repositório
4. Adicione as variáveis de ambiente
5. Railway gera URL HTTPS automaticamente

### Opção 2: Render

1. Crie conta em [render.com](https://render.com)
2. Crie um novo **Web Service**
3. Conecte ao repositório
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Adicione variáveis de ambiente

### Opção 3: VPS (DigitalOcean, Vultr, etc.)

```bash
# No servidor
git clone seu-repo
cd instagram-bot
pip install -r requirements.txt

# Usar nginx + certbot para HTTPS
# Rodar com gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Opção 4: Ngrok (Apenas para testes)

```bash
# Terminal 1: Rodar o app
python app.py

# Terminal 2: Expor com ngrok
ngrok http 5000
```

Use a URL HTTPS do ngrok para configurar o webhook.

---

## 📝 Configurando Posts para Monitorar

### Opção 1: Usar o gerenciador

```bash
python manage_posts.py
```

Menu interativo para:
- Listar seus posts
- Adicionar posts para monitorar
- Configurar mensagens de resposta e DM
- Testar conexão

### Opção 2: Editar diretamente no código

No arquivo `app.py`, edite o dicionário `MONITORED_POSTS`:

```python
MONITORED_POSTS = {
    "17895695668004550": {  # ID do post
        "comment_reply": "Obrigado pelo comentário, {username}! 🙏",
        "dm_message": "Oi {username}! Vi que você comentou. Aqui está o link: https://seulink.com",
        "enabled": True
    },
    "17895695668004551": {
        "comment_reply": "Valeu! 💪",
        "dm_message": None,  # Não envia DM
        "enabled": True
    }
}
```

---

## 🧪 Testando

### Testar conexão com a API

```bash
python manage_posts.py
# Escolha opção 6: Testar conexão
```

### Testar webhook localmente

```bash
# Iniciar servidor
python app.py

# Em outro terminal, simular webhook
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [{
      "changes": [{
        "field": "comments",
        "value": {
          "id": "123",
          "media": {"id": "456"},
          "from": {"id": "789", "username": "teste"},
          "text": "Comentário de teste"
        }
      }]
    }]
  }'
```

---

## ⚠️ Limitações e Avisos

1. **Rate Limits**: A API tem limites de requisições. Não abuse.

2. **Permissões**: Algumas funcionalidades requerem aprovação da Meta para uso em produção.

3. **DMs**: Você só pode enviar DM como "resposta privada" a um comentário, não mensagens frias.

4. **Contas**: Funciona apenas para contas Business/Creator vinculadas a uma página do Facebook.

5. **Tokens**: Access Tokens expiram. Para produção, implemente refresh automático ou use tokens de longa duração.

---

## 📁 Estrutura do Projeto

```
instagram-bot/
├── app.py              # Aplicação principal (Flask)
├── instagram_api.py    # Módulo de integração com a API
├── manage_posts.py     # Utilitário para gerenciar posts
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de configuração
├── .env                # Suas configurações (não commitar!)
└── README.md           # Este arquivo
```

---

## 🆘 Problemas Comuns

### "Webhook não verifica"
- Verifique se o VERIFY_TOKEN é o mesmo no .env e no Meta
- Confirme que a URL termina em `/webhook`
- Certifique-se de que é HTTPS

### "Token inválido"
- Tokens expiram! Gere um novo no Graph API Explorer
- Verifique se tem todas as permissões necessárias

### "Não recebo notificações de comentário"
- Confirme que assinou o campo `comments` no webhook
- Verifique se o app está rodando e acessível
- Teste com `curl` para ver se o endpoint responde

### "DM não envia"
- Verifique a permissão `instagram_manage_messages`
- A API só permite DM como resposta a comentário
- O usuário não pode ter bloqueado mensagens

---

## 📚 Recursos Úteis

- [Documentação Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Webhooks do Instagram](https://developers.facebook.com/docs/instagram-api/webhooks)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer)
- [Guia de Permissões](https://developers.facebook.com/docs/permissions)

---

## 📄 Licença

MIT License - Use como quiser!
