# Instruções de Instalação - TaskFlow com SQLite

Este documento fornece instruções detalhadas para instalar e executar o TaskFlow com banco de dados SQLite.

## Requisitos do Sistema

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

## Passo a Passo para Instalação

### 1. Extrair o Arquivo ZIP

```bash
unzip taskflow_database_sqlite.zip
cd taskflow_database
```

### 2. Configurar o Ambiente Virtual

```bash
cd taskflow_api
python -m venv venv
```

#### Ativação do Ambiente Virtual

**No Windows:**
```bash
venv\Scripts\activate
```

**No Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar o Servidor

```bash
python src/main.py
```

O servidor será iniciado na porta 5001 por padrão. Você verá uma mensagem como:
```
* Running on http://127.0.0.1:5001
```

### 5. Acessar a Aplicação

Abra seu navegador e acesse:
```
http://localhost:5001/taskflow
```

## Credenciais Padrão

A aplicação vem com um usuário padrão pré-configurado:

- **Usuário:** default
- **Senha:** default

## Solução de Problemas

### Porta em Uso

Se a porta 5001 já estiver em uso, você pode alterar a porta no arquivo `src/main.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)  # Altere para outra porta
```

### Banco de Dados

Se você encontrar problemas com o banco de dados, pode excluir o arquivo `src/database/taskflow.db` e reiniciar o servidor. Um novo banco de dados será criado automaticamente.

### Dependências

Se houver problemas com as dependências, tente:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## Próximos Passos

Após a instalação, você pode:

1. Criar novas tarefas
2. Organizar tarefas em categorias
3. Definir lembretes
4. Exportar tarefas para iCalendar
5. Personalizar o tema da aplicação

## Suporte

Para obter ajuda ou relatar problemas, entre em contato com o desenvolvedor.

---

© 2025 TaskFlow
