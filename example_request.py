"""Exemplo de como fazer requisições para a API."""
import requests
import json

# Configurações
API_URL = "http://localhost:8000"
API_KEY = ""  # Deixe vazio se autenticação estiver desabilitada

# Headers
headers = {
    "Content-Type": "application/json"
}

# Adiciona API key se configurada
if API_KEY:
    headers["X-API-Key"] = API_KEY


def print_label_example():
    """Exemplo de impressão de etiqueta de produto."""
    url = f"{API_URL}/print"
    
    data = {
        "label_type": "produto",
        "data": {
            "codigo": "12345",
            "descricao": "Produto XYZ - Descrição do Produto",
            "quantidade": 10,
            "preco": "29.90",
            "codigo_barras": "1234567890123"
        }
    }
    
    print("Enviando requisição de impressão...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ Resposta:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro na requisição: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Resposta: {e.response.text}")
        return None


def check_status():
    """Verifica o status da API."""
    url = f"{API_URL}/status"
    
    print("Verificando status da API...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ Status:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro: {e}")
        return None


def list_printers():
    """Lista impressoras disponíveis."""
    url = f"{API_URL}/printers"
    
    print("Listando impressoras...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ Impressoras:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro: {e}")
        return None


def view_queue():
    """Visualiza a fila de impressão."""
    url = f"{API_URL}/queue"
    
    print("Visualizando fila...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Fila ({len(result)} itens):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Exemplos de Uso da API de Impressão de Etiquetas")
    print("=" * 60)
    print()
    
    # Verifica status
    check_status()
    print()
    
    # Lista impressoras
    list_printers()
    print()
    
    # Visualiza fila
    view_queue()
    print()
    
    # Imprime etiqueta
    print_label_example()
    print()
    
    print("=" * 60)
    print("Exemplos concluídos!")
    print("=" * 60)

