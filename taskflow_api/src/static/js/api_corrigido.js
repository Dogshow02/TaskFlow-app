/**
 * TaskFlow API Client
 * Módulo para interagir com a API do TaskFlow
 */

const API = {
    // URL base da API
    baseUrl: '/api',
    
    // Usuário atual (padrão: usuário default)
    currentUser: {
        id: 1,
        username: 'default'
    },
    
    /**
     * Configurações do usuário
     */
    settings: {
        theme: 'light',
        notifications_enabled: true,
        default_priority: 'media'
    },
    
    /**
     * Inicializa o cliente da API
     */
    init: async function() {
        console.log('Inicializando API client...');
        
        try {
            // Carregar configurações do usuário
            await this.loadUserSettings();
            
            // Aplicar tema
            this.applyTheme();
            
            return true;
        } catch (error) {
            console.error('Erro ao inicializar API client:', error);
            return false;
        }
    },
    
    /**
     * Realiza uma requisição para a API
     * @param {string} endpoint - Endpoint da API
     * @param {string} method - Método HTTP (GET, POST, PUT, DELETE)
     * @param {object} data - Dados a serem enviados (opcional)
     * @returns {Promise} - Promise com a resposta da API
     */
    request: async function(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            
            if (!result.success && result.error) {
                throw new Error(result.error);
            }
            
            return result;
        } catch (error) {
            console.error(`Erro na requisição para ${url}:`, error);
            throw error;
        }
    },
    
    /**
     * Carrega as configurações do usuário
     */
    loadUserSettings: async function() {
        try {
            const result = await this.request(`/settings/${this.currentUser.id}`);
            this.settings = result.settings;
            return this.settings;
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
            // Usar configurações padrão em caso de erro
            this.settings = {
                theme: 'light',
                notifications_enabled: true,
                default_priority: 'media'
            };
            return this.settings;
        }
    },
    
    /**
     * Aplica o tema conforme configurações
     */
    applyTheme: function() {
        document.documentElement.setAttribute('data-theme', this.settings.theme);
        
        // Atualizar ícone do botão de tema
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = this.settings.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    },
    
    /**
     * Alterna o tema entre claro e escuro
     */
    toggleTheme: async function() {
        const newTheme = this.settings.theme === 'dark' ? 'light' : 'dark';
        
        try {
            await this.request(`/settings/${this.currentUser.id}`, 'PUT', {
                theme: newTheme
            });
            
            this.settings.theme = newTheme;
            this.applyTheme();
            
            return true;
        } catch (error) {
            console.error('Erro ao alternar tema:', error);
            return false;
        }
    },
    
    /**
     * Obtém todas as tarefas do usuário
     * @param {object} filters - Filtros opcionais (completed, priority, category_id)
     * @returns {Promise} - Promise com as tarefas
     */
    getTasks: async function(filters = {}) {
        let queryParams = `user_id=${this.currentUser.id}`;
        
        if (filters.completed !== undefined) {
            queryParams += `&completed=${filters.completed}`;
        }
        
        if (filters.priority) {
            queryParams += `&priority=${filters.priority}`;
        }
        
        if (filters.category_id) {
            queryParams += `&category_id=${filters.category_id}`;
        }
        
        try {
            const result = await this.request(`/tasks?${queryParams}`);
            return result.tasks || [];
        } catch (error) {
            console.error('Erro ao obter tarefas:', error);
            return [];
        }
    },
    
    /**
     * Adiciona uma nova tarefa
     * @param {object} taskData - Dados da tarefa
     * @returns {Promise} - Promise com a tarefa criada
     */
    addTask: async function(taskData) {
        // Adicionar ID do usuário atual
        taskData.user_id = this.currentUser.id;
        
        try {
            const result = await this.request('/tasks', 'POST', taskData);
            return result.task;
        } catch (error) {
            console.error('Erro ao adicionar tarefa:', error);
            throw error;
        }
    },
    
    /**
     * Atualiza uma tarefa existente
     * @param {number} taskId - ID da tarefa
     * @param {object} taskData - Dados atualizados da tarefa
     * @returns {Promise} - Promise com a tarefa atualizada
     */
    updateTask: async function(taskId, taskData) {
        try {
            const result = await this.request(`/tasks/${taskId}`, 'PUT', taskData);
            return result.task;
        } catch (error) {
            console.error(`Erro ao atualizar tarefa ${taskId}:`, error);
            throw error;
        }
    },
    
    /**
     * Alterna o status de conclusão de uma tarefa
     * @param {number} taskId - ID da tarefa
     * @returns {Promise} - Promise com a tarefa atualizada
     */
    toggleTask: async function(taskId) {
        try {
            const result = await this.request(`/tasks/toggle/${taskId}`, 'PATCH');
            return result.task;
        } catch (error) {
            console.error(`Erro ao alternar status da tarefa ${taskId}:`, error);
            throw error;
        }
    },
    
    /**
     * Exclui uma tarefa
     * @param {number} taskId - ID da tarefa
     * @returns {Promise} - Promise com o resultado da operação
     */
    deleteTask: async function(taskId) {
        try {
            const result = await this.request(`/tasks/${taskId}`, 'DELETE');
            return result;
        } catch (error) {
            console.error(`Erro ao excluir tarefa ${taskId}:`, error);
            throw error;
        }
    },
    
    /**
     * Obtém todas as categorias do usuário
     * @returns {Promise} - Promise com as categorias
     */
    getCategories: async function() {
        try {
            const result = await this.request(`/categories?user_id=${this.currentUser.id}`);
            return result.categories || [];
        } catch (error) {
            console.error('Erro ao obter categorias:', error);
            return [];
        }
    },
    
    /**
     * Adiciona uma nova categoria
     * @param {object} categoryData - Dados da categoria
     * @returns {Promise} - Promise com a categoria criada
     */
    addCategory: async function(categoryData) {
        // Adicionar ID do usuário atual
        categoryData.user_id = this.currentUser.id;
        
        try {
            const result = await this.request('/categories', 'POST', categoryData);
            return result.category;
        } catch (error) {
            console.error('Erro ao adicionar categoria:', error);
            throw error;
        }
    },
    
    /**
     * Atualiza uma categoria existente
     * @param {number} categoryId - ID da categoria
     * @param {object} categoryData - Dados atualizados da categoria
     * @returns {Promise} - Promise com a categoria atualizada
     */
    updateCategory: async function(categoryId, categoryData) {
        try {
            const result = await this.request(`/categories/${categoryId}`, 'PUT', categoryData);
            return result.category;
        } catch (error) {
            console.error(`Erro ao atualizar categoria ${categoryId}:`, error);
            throw error;
        }
    },
    
    /**
     * Exclui uma categoria
     * @param {number} categoryId - ID da categoria
     * @returns {Promise} - Promise com o resultado da operação
     */
    deleteCategory: async function(categoryId) {
        try {
            const result = await this.request(`/categories/${categoryId}`, 'DELETE');
            return result;
        } catch (error) {
            console.error(`Erro ao excluir categoria ${categoryId}:`, error);
            throw error;
        }
    },
    
    /**
     * Obtém estatísticas das tarefas
     * @returns {Promise} - Promise com as estatísticas
     */
    getStats: async function() {
        try {
            const result = await this.request(`/stats?user_id=${this.currentUser.id}`);
            return result.stats || {};
        } catch (error) {
            console.error('Erro ao obter estatísticas:', error);
            return {};
        }
    },
    
    /**
     * Exporta tarefas para formato iCalendar
     * @returns {Promise} - Promise com o arquivo iCalendar
     */
    exportToICalendar: async function() {
        try {
            // Obter tarefas com lembretes
            const tasks = await this.getTasks();
            const tasksWithReminders = tasks.filter(task => task.reminder_datetime);
            
            if (tasksWithReminders.length === 0) {
                throw new Error('Nenhuma tarefa com lembrete encontrada!');
            }
            
            // Gerar conteúdo iCalendar
            let icsContent = [
                'BEGIN:VCALENDAR',
                'VERSION:2.0',
                'PRODID:-//TaskFlow//TaskFlow//PT',
                'CALSCALE:GREGORIAN',
                'METHOD:PUBLISH'
            ];
            
            tasksWithReminders.forEach(task => {
                const startDate = new Date(task.reminder_datetime);
                const endDate = new Date(startDate.getTime() + 60 * 60 * 1000); // 1 hora depois
                
                icsContent.push(
                    'BEGIN:VEVENT',
                    `UID:${task.id}@taskflow.com`,
                    `DTSTART:${this.formatDateForICS(startDate)}`,
                    `DTEND:${this.formatDateForICS(endDate)}`,
                    `SUMMARY:${task.text}`,
                    `DESCRIPTION:Prioridade: ${task.priority}${task.category ? `\\nCategoria: ${task.category.name}` : ''}`,
                    `CREATED:${this.formatDateForICS(new Date(task.created_at))}`,
                    'STATUS:CONFIRMED',
                    'TRANSP:OPAQUE',
                    'END:VEVENT'
                );
            });
            
            icsContent.push('END:VCALENDAR');
            
            // Criar blob e download
            const blob = new Blob([icsContent.join('\r\n')], { type: 'text/calendar;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'taskflow_calendario.ics';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            return {
                success: true,
                message: `${tasksWithReminders.length} evento(s) exportado(s) para calendário!`
            };
        } catch (error) {
            console.error('Erro ao exportar para iCalendar:', error);
            throw error;
        }
    },
    
    /**
     * Formata data para o formato iCalendar
     * @param {Date} date - Data a ser formatada
     * @returns {string} - Data formatada
     */
    formatDateForICS: function(date) {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    }
};

// Exportar para uso global
window.TaskFlowAPI = API;
