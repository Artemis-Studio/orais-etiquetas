"""Exemplo de requisição completa sem API key."""
import requests
import json

# Configurações - SEM API KEY (autenticação desabilitada)
API_URL = "http://localhost:8000"

# Headers (sem X-API-Key)
headers = {
    "Content-Type": "application/json"
}

def imprimir_etiqueta_completa():
    """Exemplo de impressão de etiqueta com TODOS os campos."""
    url = f"{API_URL}/print"
    
    # Dados completos da etiqueta
    data = {
        "label_type": "produto",
        "data": {
            "codigo": "1420",
            "descricao": "JG DENTE ENDO 21 AO 27 RADIO",
            "descricao2": "PACOS",
            "ref": "1420",
            "pedido": "10511",
            "codigo_barras": "7890000005098",
            "lote": "10111150126",
            "validade": "31/12/2025",
            "quantidade": "10",
            "preco": "29.90"
        },
        "printer_name": ""  # Deixe vazio para usar impressora padrão
    }
    
    print("=" * 60)
    print("Enviando requisição de impressão COMPLETA (sem API key)")
    print("=" * 60)
    print(f"\nURL: {url}")
    print(f"\nDados da requisição:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("\n" + "=" * 60)
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ SUCESSO! Resposta da API:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('success'):
            if result.get('queue_id'):
                print(f"\n📋 Requisição adicionada à fila: {result['queue_id']}")
            else:
                print("\n🖨️ Impressão realizada imediatamente!")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API")
        print(f"   Verifique se a API está rodando em {API_URL}")
        print("   Execute: python run_api.py")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO na requisição: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"\nResposta do servidor:")
            print(e.response.text)
        return None


def verificar_status():
    """Verifica o status da API."""
    url = f"{API_URL}/status"
    
    print("\n" + "=" * 60)
    print("Verificando status da API...")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ Status da API:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro ao verificar status: {e}")
        return None


if __name__ == "__main__":
    # Primeiro verifica o status
    verificar_status()
    
    print("\n")
    
    # Depois envia a requisição completa
    imprimir_etiqueta_completa()
    
    print("\n" + "=" * 60)
    print("Teste concluído!")
    print("=" * 60)
