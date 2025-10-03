#!/usr/bin/env python3
"""
Script para testar operações CRUD no banco de dados TaskFlow
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

# URL base da API
BASE_URL = "http://localhost:5000/api"

def print_response(response, message=""):
    """Imprime resposta da API formatada"""
    print(f"\n{'=' * 50}")
    if message:
        print(f"{message}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print(f"{'=' * 50}\n")

def test_user_operations():
    """Testar operações CRUD de usuários"""
    print("\n\n>>> TESTANDO OPERAÇÕES DE USUÁRIOS <<<\n")
    
    # Criar usuário de teste
    print("Criando usuário de teste...")
    user_data = {
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "email": f"test_{int(datetime.now().timestamp())}@example.com",
        "password": "senha123"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print_response(response, "Criar usuário")
    
    if response.status_code == 201:
        user_id = response.json()["user"]["id"]
        
        # Obter usuário
        print("Obtendo usuário criado...")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print_response(response, "Obter usuário")
        
        # Atualizar usuário
        print("Atualizando usuário...")
        update_data = {
            "username": f"updated_{user_data['username']}"
        }
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        print_response(response, "Atualizar usuário")
        
        # Login
        print("Testando login...")
        login_data = {
            "username": update_data["username"],
            "password": user_data["password"]
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print_response(response, "Login")
        
        # Deletar usuário
        print("Deletando usuário...")
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        print_response(response, "Deletar usuário")
    
    return user_data

def test_category_operations(user_id=1):
    """Testar operações CRUD de categorias"""
    print("\n\n>>> TESTANDO OPERAÇÕES DE CATEGORIAS <<<\n")
    
    # Listar categorias
    print("Listando categorias...")
    response = requests.get(f"{BASE_URL}/categories?user_id={user_id}")
    print_response(response, "Listar categorias")
    
    # Criar categoria
    print("Criando categoria de teste...")
    category_data = {
        "name": f"Categoria Teste {int(datetime.now().timestamp())}",
        "color": "#ff5722",
        "user_id": user_id
    }
    
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    print_response(response, "Criar categoria")
    
    if response.status_code == 201:
        category_id = response.json()["category"]["id"]
        
        # Atualizar categoria
        print("Atualizando categoria...")
        update_data = {
            "name": f"Atualizada {category_data['name']}",
            "color": "#2196f3"
        }
        response = requests.put(f"{BASE_URL}/categories/{category_id}", json=update_data)
        print_response(response, "Atualizar categoria")
        
        # Listar categorias novamente
        print("Listando categorias atualizadas...")
        response = requests.get(f"{BASE_URL}/categories?user_id={user_id}")
        print_response(response, "Listar categorias atualizadas")
        
        return category_id
    
    return None

def test_task_operations(user_id=1, category_id=None):
    """Testar operações CRUD de tarefas"""
    print("\n\n>>> TESTANDO OPERAÇÕES DE TAREFAS <<<\n")
    
    # Listar tarefas
    print("Listando tarefas...")
    response = requests.get(f"{BASE_URL}/tasks?user_id={user_id}")
    print_response(response, "Listar tarefas")
    
    # Criar tarefa
    print("Criando tarefa de teste...")
    reminder_time = (datetime.now() + timedelta(days=1)).isoformat()
    task_data = {
        "text": f"Tarefa de teste {int(datetime.now().timestamp())}",
        "priority": "alta",
        "category_id": category_id,
        "reminder_datetime": reminder_time,
        "user_id": user_id
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=task_data)
    print_response(response, "Criar tarefa")
    
    if response.status_code == 201:
        task_id = response.json()["task"]["id"]
        
        # Obter tarefa
        print("Obtendo tarefa criada...")
        response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        print_response(response, "Obter tarefa")
        
        # Atualizar tarefa
        print("Atualizando tarefa...")
        update_data = {
            "text": f"Atualizada {task_data['text']}",
            "priority": "media"
        }
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data)
        print_response(response, "Atualizar tarefa")
        
        # Marcar como concluída
        print("Marcando tarefa como concluída...")
        response = requests.patch(f"{BASE_URL}/tasks/toggle/{task_id}")
        print_response(response, "Marcar como concluída")
        
        # Marcar como não concluída
        print("Marcando tarefa como não concluída...")
        response = requests.patch(f"{BASE_URL}/tasks/toggle/{task_id}")
        print_response(response, "Marcar como não concluída")
        
        # Obter estatísticas
        print("Obtendo estatísticas...")
        response = requests.get(f"{BASE_URL}/stats?user_id={user_id}")
        print_response(response, "Obter estatísticas")
        
        # Deletar tarefa
        print("Deletando tarefa...")
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
        print_response(response, "Deletar tarefa")
    
    return task_data

def test_settings_operations(user_id=1):
    """Testar operações de configurações do usuário"""
    print("\n\n>>> TESTANDO OPERAÇÕES DE CONFIGURAÇÕES <<<\n")
    
    # Obter configurações
    print("Obtendo configurações do usuário...")
    response = requests.get(f"{BASE_URL}/settings/{user_id}")
    print_response(response, "Obter configurações")
    
    # Atualizar configurações
    print("Atualizando configurações...")
    settings_data = {
        "theme": "dark",
        "notifications_enabled": True,
        "default_priority": "alta"
    }
    
    response = requests.put(f"{BASE_URL}/settings/{user_id}", json=settings_data)
    print_response(response, "Atualizar configurações")
    
    # Obter configurações atualizadas
    print("Obtendo configurações atualizadas...")
    response = requests.get(f"{BASE_URL}/settings/{user_id}")
    print_response(response, "Obter configurações atualizadas")
    
    # Restaurar configurações padrão
    print("Restaurando configurações padrão...")
    default_settings = {
        "theme": "light",
        "notifications_enabled": True,
        "default_priority": "media"
    }
    
    response = requests.put(f"{BASE_URL}/settings/{user_id}", json=default_settings)
    print_response(response, "Restaurar configurações padrão")

def main():
    """Função principal para executar testes"""
    print("\n" + "=" * 60)
    print("TESTE DE OPERAÇÕES CRUD - TASKFLOW API")
    print("=" * 60 + "\n")
    
    try:
        # Testar operações de usuário
        user_data = test_user_operations()
        
        # Testar operações com usuário padrão (id=1)
        category_id = test_category_operations()
        test_task_operations(category_id=category_id)
        test_settings_operations()
        
        print("\n" + "=" * 60)
        print("TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n\nERRO: Não foi possível conectar à API.")
        print("Certifique-se de que o servidor Flask está em execução na porta 5000.\n")
        print("Para iniciar o servidor, execute:")
        print("cd /home/ubuntu/taskflow_database/taskflow_api && source venv/bin/activate && python src/main.py\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERRO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
