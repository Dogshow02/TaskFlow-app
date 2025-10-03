 TaskFlow com SQLite

TaskFlow é um gerenciador de tarefas completo com banco de dados SQLite, backend Flask e frontend responsivo. Esta versão aprimorada do TaskFlow oferece persistência de dados, múltiplos usuários, categorias personalizáveis e muito mais.

## Características

- **Banco de dados SQLite** para persistência de dados
- **API RESTful** com Flask para operações CRUD
- **Frontend responsivo** adaptado para desktop, tablet e celular
- **Autenticação de usuários** para ambiente multi-usuário
- **Categorias personalizáveis** com cores
- **Lembretes e notificações** para tarefas
- **Exportação para iCalendar** para integração com calendários
- **Tema claro/escuro** personalizável
- **Estatísticas** de tarefas e produtividade

## Estrutura do Banco de Dados

O banco de dados SQLite possui as seguintes tabelas:

- **users**: Armazena informações dos usuários
- **tasks**: Armazena as tarefas com seus detalhes
- **categories**: Armazena categorias personalizáveis
- **user_settings**: Armazena configurações do usuário
- **activity_logs**: Registra atividades para auditoria

## Requisitos

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-CORS
- Navegador moderno (Chrome, Firefox, Safari, Edge)

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/taskflow-sqlite.git
   cd taskflow-sqlite
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   cd taskflow_api
   pip install -r requirements.txt
   ```

4. Inicie o servidor:
   ```
   python src/main.py
   ```

5. Acesse a aplicação:
   ```
   http://localhost:5001/taskflow
   ```

## Estrutura do Projeto

```
taskflow_database/
├── taskflow_api/
│   ├── venv/                  # Ambiente virtual Python
│   ├── requirements.txt       # Dependências do projeto
│   ├── test_crud.py           # Script para testar operações CRUD
│   └── src/
│       ├── main.py            # Ponto de entrada da aplicação
│       ├── database/          # Arquivos de banco de dados
│       │   └── taskflow.db    # Banco de dados SQLite
│       ├── models/            # Modelos de dados
│       │   ├── user.py        # Modelo de usuário
│       │   └── task.py        # Modelos de tarefas e categorias
│       ├── routes/            # Rotas da API
│       │   ├── user.py        # Rotas de usuário
│       │   ├── task.py        # Rotas de tarefas
│       │   └── frontend.py    # Rotas para servir o frontend
│       └── static/            # Arquivos estáticos
│           ├── css/           # Estilos CSS
│           │   └── styles.css # Estilos da aplicação
│           ├── js/            # Scripts JavaScript
│           │   ├── api.js     # Cliente da API
│           │   └── script.js  # Lógica da aplicação
│           └── taskflow/      # Frontend da aplicação
│               └── index.html # Página principal
└── database_schema.sql        # Esquema do banco de dados
```

### Tarefas

- `GET /api/tasks` - Listar tarefas (com filtros opcionais)
- `POST /api/tasks` - Criar nova tarefa
- `GET /api/tasks/<id>` - Obter tarefa específica
- `PUT /api/tasks/<id>` - Atualizar tarefa
- `DELETE /api/tasks/<id>` - Excluir tarefa
- `PATCH /api/tasks/toggle/<id>` - Alternar status de conclusão

### Categorias

- `GET /api/categories` - Listar categorias
- `POST /api/categories` - Criar nova categoria
- `PUT /api/categories/<id>` - Atualizar categoria
- `DELETE /api/categories/<id>` - Excluir categoria

### Estatísticas

- `GET /api/stats` - Obter estatísticas das tarefas

## Uso

1. **Registro/Login**: Crie uma conta ou use o usuário padrão (username: default, senha: default)
2. **Adicionar Tarefas**: Preencha o formulário e clique em "Adicionar"
3. **Gerenciar Tarefas**: Marque como concluídas, edite ou exclua tarefas
4. **Filtrar Tarefas**: Use os botões de filtro ou o seletor de categorias
5. **Exportar**: Clique em "Exportar" e selecione o formato desejado (iCalendar)
6. **Alternar Tema**: Clique no ícone de lua/sol para alternar entre tema claro e escuro

## Desenvolvimento

Para desenvolver novas funcionalidades:

1. Crie novos modelos em `src/models/` se necessário
2. Adicione rotas em `src/routes/` para novos endpoints
3. Atualize o cliente da API em `src/static/js/api.js`
4. Implemente a interface do usuário em `src/static/js/script.js`


## Autor

Desenvolvido por Douglas Teixeira de Freitas

---

© 2025 TaskFlow
