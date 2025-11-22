"""
Instagram API - Módulo de integração com a Graph API do Meta
"""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://graph.facebook.com/v18.0"


class InstagramAPI:
    """
    Classe para interagir com a API do Instagram (via Meta Graph API)
    """
    
    def __init__(self, access_token: str, instagram_account_id: str):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: dict = None, 
        data: dict = None
    ) -> Optional[dict]:
        """Faz uma requisição para a API do Meta"""
        
        url = f"{BASE_URL}/{endpoint}"
        
        # Adicionar access_token aos parâmetros
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, params=params, json=data, timeout=30)
            else:
                raise ValueError(f"Método não suportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {endpoint}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Resposta: {e.response.text}")
            return None
    
    # =========================================================================
    # MÉTODOS DE COMENTÁRIOS
    # =========================================================================
    
    def reply_to_comment(self, comment_id: str, message: str) -> bool:
        """
        Responde a um comentário específico
        
        Args:
            comment_id: ID do comentário a ser respondido
            message: Texto da resposta
            
        Returns:
            True se sucesso, False se falhou
        """
        result = self._make_request(
            method='POST',
            endpoint=f"{comment_id}/replies",
            data={'message': message}
        )
        
        return result is not None and 'id' in result
    
    def send_private_reply(self, comment_id: str, message: str) -> bool:
        """
        Envia uma mensagem privada (DM) em resposta a um comentário
        Isso usa a feature "Private Replies" do Instagram
        
        Args:
            comment_id: ID do comentário
            message: Texto da DM
            
        Returns:
            True se sucesso, False se falhou
        """
        result = self._make_request(
            method='POST',
            endpoint=f"{self.instagram_account_id}/messages",
            data={
                'recipient': {'comment_id': comment_id},
                'message': {'text': message}
            }
        )
        
        return result is not None and 'message_id' in result
    
    def get_comment_details(self, comment_id: str) -> Optional[dict]:
        """
        Obtém detalhes de um comentário específico
        
        Args:
            comment_id: ID do comentário
            
        Returns:
            Dados do comentário ou None se falhou
        """
        return self._make_request(
            method='GET',
            endpoint=comment_id,
            params={'fields': 'id,text,username,timestamp,from'}
        )
    
    # =========================================================================
    # MÉTODOS DE MÍDIA/POSTS
    # =========================================================================
    
    def get_media_list(self, limit: int = 25) -> Optional[list]:
        """
        Lista as mídias (posts) da conta
        
        Args:
            limit: Número máximo de posts a retornar
            
        Returns:
            Lista de mídias ou None se falhou
        """
        result = self._make_request(
            method='GET',
            endpoint=f"{self.instagram_account_id}/media",
            params={
                'fields': 'id,caption,media_type,timestamp,permalink',
                'limit': limit
            }
        )
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def get_media_comments(self, media_id: str, limit: int = 50) -> Optional[list]:
        """
        Lista os comentários de um post específico
        
        Args:
            media_id: ID do post
            limit: Número máximo de comentários
            
        Returns:
            Lista de comentários ou None se falhou
        """
        result = self._make_request(
            method='GET',
            endpoint=f"{media_id}/comments",
            params={
                'fields': 'id,text,username,timestamp,from',
                'limit': limit
            }
        )
        
        if result and 'data' in result:
            return result['data']
        return None
    
    # =========================================================================
    # MÉTODOS DE CONTA
    # =========================================================================
    
    def get_account_info(self) -> Optional[dict]:
        """
        Obtém informações da conta do Instagram
        
        Returns:
            Dados da conta ou None se falhou
        """
        return self._make_request(
            method='GET',
            endpoint=self.instagram_account_id,
            params={'fields': 'id,username,name,biography,followers_count,follows_count,media_count'}
        )
    
    def verify_permissions(self) -> dict:
        """
        Verifica quais permissões o token possui
        
        Returns:
            Dicionário com status das permissões
        """
        result = self._make_request(
            method='GET',
            endpoint='me/permissions'
        )
        
        if result and 'data' in result:
            return {
                perm['permission']: perm['status'] 
                for perm in result['data']
            }
        return {}


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def format_mention(username: str) -> str:
    """Formata uma menção de usuário"""
    if username.startswith('@'):
        return username
    return f"@{username}"


def truncate_message(message: str, max_length: int = 1000) -> str:
    """Trunca uma mensagem se exceder o limite"""
    if len(message) <= max_length:
        return message
    return message[:max_length-3] + "..."
