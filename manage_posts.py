"""
Utilitário para gerenciar posts monitorados
Execute: python manage_posts.py
"""

import os
import json
from dotenv import load_dotenv
from instagram_api import InstagramAPI

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', '')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID', '')

# Arquivo para salvar configurações dos posts
CONFIG_FILE = 'monitored_posts.json'


def load_config() -> dict:
    """Carrega configurações salvas"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Salva configurações"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ Configurações salvas em {CONFIG_FILE}")


def list_posts():
    """Lista seus posts recentes do Instagram"""
    if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("❌ Configure ACCESS_TOKEN e INSTAGRAM_ACCOUNT_ID no arquivo .env")
        return
    
    api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)
    posts = api.get_media_list(limit=10)
    
    if not posts:
        print("❌ Não foi possível obter posts. Verifique seu token.")
        return
    
    print("\n📸 Seus posts recentes:\n")
    print("-" * 80)
    
    for i, post in enumerate(posts, 1):
        caption = post.get('caption', 'Sem legenda')
        # Truncar legenda se muito longa
        if len(caption) > 50:
            caption = caption[:50] + "..."
        
        print(f"{i}. ID: {post['id']}")
        print(f"   Tipo: {post.get('media_type', 'N/A')}")
        print(f"   Legenda: {caption}")
        print(f"   Link: {post.get('permalink', 'N/A')}")
        print("-" * 80)


def add_post():
    """Adiciona um post para monitoramento"""
    config = load_config()
    
    print("\n➕ Adicionar post para monitoramento\n")
    
    post_id = input("ID do post (use 'list' para ver seus posts): ").strip()
    
    if post_id.lower() == 'list':
        list_posts()
        post_id = input("\nAgora digite o ID do post: ").strip()
    
    if not post_id:
        print("❌ ID inválido")
        return
    
    print("\n📝 Configure as respostas automáticas:")
    print("(Deixe em branco para não enviar)")
    print("Dica: Use {username} para inserir o nome do usuário\n")
    
    comment_reply = input("Resposta ao comentário: ").strip() or None
    dm_message = input("Mensagem de DM: ").strip() or None
    
    config[post_id] = {
        "comment_reply": comment_reply,
        "dm_message": dm_message,
        "enabled": True
    }
    
    save_config(config)
    print(f"\n✅ Post {post_id} adicionado com sucesso!")


def remove_post():
    """Remove um post do monitoramento"""
    config = load_config()
    
    if not config:
        print("❌ Nenhum post configurado")
        return
    
    print("\n📋 Posts configurados:\n")
    for post_id, settings in config.items():
        status = "🟢 Ativo" if settings.get('enabled') else "🔴 Inativo"
        print(f"  - {post_id} ({status})")
    
    post_id = input("\nID do post para remover: ").strip()
    
    if post_id in config:
        del config[post_id]
        save_config(config)
        print(f"✅ Post {post_id} removido")
    else:
        print("❌ Post não encontrado")


def view_config():
    """Mostra configuração atual"""
    config = load_config()
    
    if not config:
        print("❌ Nenhum post configurado ainda")
        return
    
    print("\n📋 Configuração atual:\n")
    print(json.dumps(config, indent=2, ensure_ascii=False))


def generate_code():
    """Gera código Python para colar no app.py"""
    config = load_config()
    
    if not config:
        print("❌ Nenhum post configurado")
        return
    
    print("\n📝 Cole este código no seu app.py (substitua MONITORED_POSTS):\n")
    print("MONITORED_POSTS = {")
    
    for post_id, settings in config.items():
        print(f'    "{post_id}": {{')
        print(f'        "comment_reply": {repr(settings.get("comment_reply"))},')
        print(f'        "dm_message": {repr(settings.get("dm_message"))},')
        print(f'        "enabled": {settings.get("enabled", True)}')
        print('    },')
    
    print("}")


def test_connection():
    """Testa a conexão com a API"""
    if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("❌ Configure ACCESS_TOKEN e INSTAGRAM_ACCOUNT_ID no arquivo .env")
        return
    
    print("\n🔍 Testando conexão...\n")
    
    api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)
    
    # Testar info da conta
    info = api.get_account_info()
    if info:
        print(f"✅ Conectado como: @{info.get('username', 'N/A')}")
        print(f"   Nome: {info.get('name', 'N/A')}")
        print(f"   Seguidores: {info.get('followers_count', 'N/A')}")
        print(f"   Posts: {info.get('media_count', 'N/A')}")
    else:
        print("❌ Falha ao conectar. Verifique seu ACCESS_TOKEN.")
        return
    
    # Verificar permissões
    print("\n📋 Verificando permissões...")
    perms = api.verify_permissions()
    
    required_perms = [
        'instagram_basic',
        'instagram_manage_comments',
        'instagram_manage_messages',
        'pages_manage_metadata'
    ]
    
    for perm in required_perms:
        status = perms.get(perm, 'não encontrada')
        emoji = "✅" if status == 'granted' else "❌"
        print(f"   {emoji} {perm}: {status}")


def main():
    """Menu principal"""
    while True:
        print("\n" + "=" * 50)
        print("🤖 INSTAGRAM BOT - Gerenciador de Posts")
        print("=" * 50)
        print("\n1. Listar meus posts")
        print("2. Adicionar post para monitorar")
        print("3. Remover post")
        print("4. Ver configuração atual")
        print("5. Gerar código para app.py")
        print("6. Testar conexão com API")
        print("0. Sair\n")
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '1':
            list_posts()
        elif choice == '2':
            add_post()
        elif choice == '3':
            remove_post()
        elif choice == '4':
            view_config()
        elif choice == '5':
            generate_code()
        elif choice == '6':
            test_connection()
        elif choice == '0':
            print("\n👋 Até mais!")
            break
        else:
            print("❌ Opção inválida")


if __name__ == '__main__':
    main()
