"""
Instagram Comment Bot - Aplicação Principal
Monitora comentários e envia respostas automáticas + DMs
"""

import os
import hmac
import hashlib
import logging
import random
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from instagram_api import InstagramAPI

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurações do Meta/Instagram
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'seu_token_de_verificacao')
APP_SECRET = os.getenv('APP_SECRET', '')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', '')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID', '')

# Inicializar API do Instagram
instagram = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

# =============================================================================
# CONFIGURAÇÃO DE RESPOSTAS AUTOMÁTICAS
# =============================================================================

# Respostas variadas para comentários (escolhe aleatoriamente)
COMMENT_REPLIES = [
    "Todos os itens foram enviados para sua DM! Verifique se você está seguindo a página pra receber tudo direitinho!🥰",
    "Todos os itens foram enviados para sua caixa de mensagem! Verifique se você está seguindo a página pra receber tudo direitinho!🥰",
    "Todos os itens foram enviados com sucesso!✅ Siga a página pra receber outros tipos de promoções!!"
]

# Posts que você quer monitorar (ID do post -> configuração)
MONITORED_POSTS = {
    # Post 1: Itens Milagrosos da Shopee
    "18076117025230421": {
        "comment_replies": COMMENT_REPLIES,
        "dm_message": """E aqui estão os links do vídeo "Itens Milagrosos da Shopee que ninguém te conta mas eu sim"

🔗 Aparelho de lifting https://s.shopee.com.br/12ORVX7p6
🔗 Bastão de argila https://s.shopee.com.br/8AO6Ho4AdC 
🔗 Creme de arroz https://s.shopee.com.br/8pdn4vZKLU 
🔗 Máscara de colágeno https://s.shopee.com.br/3LIqX3ww7q 

Caso não consiga CLICAR algum link, copie e cole no bloco de notas do seu celular ou WhatsApp que fica clicável ou acesse o destaque links Acessórios""",
        "enabled": True
    },
    
    # Post 2: Top 10 produtos da shopee - Faxina
    "18059820224230541": {
        "comment_replies": COMMENT_REPLIES,
        "dm_message": """Certo, aqui estão os links do vídeo "Top 10 produtos da shopee que vão salvar as malucas da faxina"

🔗 Tira pelos https://s.shopee.com.br/3AzWD7SD5l
🔗 Vassoura 2 em 1 https://s.shopee.com.br/4VUtnbV7rT 
🔗 Limpa Piso https://s.shopee.com.br/50RAOYssiK
🔗 Pano metálico https://s.shopee.com.br/2qMfoc93MJ
🔗 Spray mágico https://s.shopee.com.br/2B6z1Qjyre 
🔗 Rolo de microfibra https://s.shopee.com.br/9fCzxFPUOA
🔗 Limpa calçados https://s.shopee.com.br/5VNQzcw8rS 
🔗 Escovão elétrico https://s.shopee.com.br/70CEmQy1GR 

Caso não consiga CLICAR algum link, copie e cole no bloco de notas do seu celular ou WhatsApp que fica clicável ou acesse o destaque links Acessórios

Temos um grupo também no Whatsapp, onde postamos as melhores promoções todos os dias, caso queira entrar é só clicar no Link abaixo:
👉 https://chat.whatsapp.com/Kh0sSt3eLnwFbvokLmnrwZ""",
        "enabled": True
    }
}

# Resposta padrão para posts não configurados específicamente
DEFAULT_RESPONSE = {
    "comment_replies": None,
    "dm_message": None,
    "enabled": False
}


def get_post_config(post_id: str) -> dict:
    """Retorna a configuração para um post específico"""
    # Tenta encontrar pelo ID completo ou pelo shortcode
    if post_id in MONITORED_POSTS:
        return MONITORED_POSTS[post_id]
    
    # Procura pelo shortcode em qualquer parte do ID
    for shortcode, config in MONITORED_POSTS.items():
        if shortcode in post_id:
            return config
    
    return DEFAULT_RESPONSE


def get_random_reply(config: dict) -> str:
    """Retorna uma resposta aleatória da lista de respostas"""
    replies = config.get('comment_replies', [])
    if replies:
        return random.choice(replies)
    return None


# =============================================================================
# VERIFICAÇÃO DE ASSINATURA (SEGURANÇA)
# =============================================================================

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verifica se a requisição realmente veio do Meta/Instagram"""
    if not APP_SECRET:
        logger.warning("APP_SECRET não configurado - pulando verificação")
        return True
    
    expected_signature = hmac.new(
        APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)


# =============================================================================
# ROTAS DA APLICAÇÃO
# =============================================================================

@app.route('/', methods=['GET'])
def home():
    """Rota inicial - verifica se o servidor está rodando"""
    return jsonify({
        "status": "online",
        "message": "Instagram Bot está rodando! 🤖"
    })


@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """
    Verificação do Webhook (GET)
    O Meta envia uma requisição GET para verificar seu endpoint
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        logger.info("✅ Webhook verificado com sucesso!")
        return challenge, 200
    else:
        logger.warning("❌ Falha na verificação do webhook")
        return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Handler principal do Webhook (POST)
    Recebe notificações de comentários do Instagram
    """
    # Verificar assinatura
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not verify_signature(request.data, signature):
        logger.warning("❌ Assinatura inválida!")
        return 'Invalid signature', 403
    
    # Processar payload
    data = request.json
    logger.info(f"📩 Webhook recebido: {data}")
    
    try:
        process_webhook(data)
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
    
    # Sempre retornar 200 rapidamente para o Meta
    return 'OK', 200


def process_webhook(data: dict):
    """Processa os dados recebidos do webhook"""
    
    # Verificar se é do Instagram
    if data.get('object') != 'instagram':
        return
    
    # Iterar sobre as entradas
    for entry in data.get('entry', []):
        # Processar mudanças (comentários, etc.)
        for change in entry.get('changes', []):
            if change.get('field') == 'comments':
                handle_comment(change.get('value', {}))


def handle_comment(comment_data: dict):
    """
    Processa um novo comentário
    """
    comment_id = comment_data.get('id')
    post_id = comment_data.get('media', {}).get('id')
    user_id = comment_data.get('from', {}).get('id')
    username = comment_data.get('from', {}).get('username', 'usuário')
    comment_text = comment_data.get('text', '')
    
    logger.info(f"💬 Novo comentário de @{username}: {comment_text}")
    logger.info(f"📌 Post ID: {post_id}")
    
    # Verificar se devemos responder este post
    config = get_post_config(str(post_id))
    
    if not config.get('enabled'):
        logger.info(f"Post {post_id} não está configurado para respostas automáticas")
        return
    
    # Responder o comentário (se configurado) - com variação aleatória
    reply_text = get_random_reply(config)
    if reply_text:
        success = instagram.reply_to_comment(comment_id, reply_text)
        if success:
            logger.info(f"✅ Comentário respondido para @{username}: {reply_text[:50]}...")
        else:
            logger.error(f"❌ Falha ao responder comentário")
    
    # Enviar DM (se configurado)
    if config.get('dm_message'):
        dm_text = config['dm_message']
        
        success = instagram.send_private_reply(comment_id, dm_text)
        if success:
            logger.info(f"✅ DM enviada para @{username}")
        else:
            logger.error(f"❌ Falha ao enviar DM")


# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
