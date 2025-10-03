// TaskFlow - Gerenciador de Tarefas Aprimorado com API
// Esta é a classe principal que gerencia todas as funcionalidades das tarefas.
class TaskManager {
    constructor() {
        this.currentFilter = 'todas';
        this.currentCategoryFilter = '';
        this.editingTaskId = null;
        this.notificationCheckInterval = null;
        this.initializeApp();
    }

    async initializeApp() {
        // Inicializar API
        await TaskFlowAPI.init();
        
        this.bindEvents();
        await this.renderTasks();
        await this.updateStats();
        await this.updateCategoryFilter();
        this.requestNotificationPermission();
        this.startNotificationCheck();
    }

    bindEvents() {
        // Eventos existentes
        document.getElementById('addTaskBtn').addEventListener('click', () => this.addTask());
        document.getElementById('taskInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addTask();
        });

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.setFilter(e.target.dataset.filter));
        });

        document.getElementById('clearCompletedBtn').addEventListener('click', () => this.clearCompleted());
        document.getElementById('closeModalBtn').addEventListener('click', () => this.closeEditModal());
        document.getElementById('cancelEditBtn').addEventListener('click', () => this.closeEditModal());
        document.getElementById('saveEditBtn').addEventListener('click', () => this.saveEdit());
        document.getElementById('editModal').addEventListener('click', (e) => {
            if (e.target.id === 'editModal') this.closeEditModal();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeEditModal();
        });

        // Novos eventos
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
        document.getElementById('exportBtn').addEventListener('click', () => this.toggleExportMenu());
        document.getElementById('exportICS').addEventListener('click', () => this.exportData('ics'));
        document.getElementById('categoryFilter').addEventListener('change', (e) => this.setCategoryFilter(e.target.value));

        // Fechar menu de exportação ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.export-dropdown')) {
                document.getElementById('exportMenu').classList.remove('show');
            }
        });
    }

    async addTask() {
        const input = document.getElementById('taskInput');
        const priority = document.getElementById('prioritySelect').value;
        const category = document.getElementById('categoryInput').value.trim();
        const reminder = document.getElementById('reminderInput').value;
        const text = input.value.trim();
        
        if (!text) return this.showToast('Por favor, digite uma tarefa', 'error');
        
        // CORREÇÃO ROBUSTA: Remover completamente a validação de data futura no frontend
        // Isso permite que o usuário adicione tarefas com lembretes para qualquer momento

        try {
            // Verificar se a categoria existe ou criar nova
            let categoryId = null;
            if (category) {
                const categories = await TaskFlowAPI.getCategories();
                const existingCategory = categories.find(c => c.name.toLowerCase() === category.toLowerCase());
                
                if (existingCategory) {
                    categoryId = existingCategory.id;
                } else {
                    // Criar nova categoria
                    const newCategory = await TaskFlowAPI.addCategory({
                        name: category,
                        color: this.getRandomColor()
                    });
                    categoryId = newCategory.id;
                }
            }
            
            // Criar tarefa via API
            const taskData = {
                text,
                priority,
                category_id: categoryId,
                reminder_datetime: reminder || null
            };
            
            await TaskFlowAPI.addTask(taskData);
            
            // Limpar formulário
            input.value = '';
            document.getElementById('prioritySelect').value = 'media';
            document.getElementById('categoryInput').value = '';
            document.getElementById('reminderInput').value = '';
            
            // Atualizar interface
            await this.renderTasks();
            await this.updateStats();
            await this.updateCategoryFilter();
            
            this.showToast('Tarefa adicionada com sucesso!');
        } catch (error) {
            this.showToast(`Erro ao adicionar tarefa: ${error.message}`, 'error');
        }
    }

    async toggleTask(id) {
        try {
            await TaskFlowAPI.toggleTask(id);
            
            // Atualizar interface
            await this.renderTasks();
            await this.updateStats();
            
            const task = (await TaskFlowAPI.getTasks()).find(t => t.id === id);
            this.showToast(task.completed ? 'Tarefa concluída!' : 'Tarefa reaberta!');
        } catch (error) {
            this.showToast(`Erro ao alternar status da tarefa: ${error.message}`, 'error');
        }
    }

    async deleteTask(id) {
        if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
            try {
                await TaskFlowAPI.deleteTask(id);
                
                // Atualizar interface
                await this.renderTasks();
                await this.updateStats();
                await this.updateCategoryFilter();
                
                this.showToast('Tarefa excluída!');
            } catch (error) {
                this.showToast(`Erro ao excluir tarefa: ${error.message}`, 'error');
            }
        }
    }

    async editTask(id) {
        try {
            const tasks = await TaskFlowAPI.getTasks();
            const task = tasks.find(t => t.id === id);
            
            if (task) {
                this.editingTaskId = id;
                document.getElementById('editTaskInput').value = task.text;
                document.getElementById('editPrioritySelect').value = task.priority;
                document.getElementById('editCategoryInput').value = task.category ? task.category.name : '';
                document.getElementById('editReminderInput').value = task.reminder_datetime ? task.reminder_datetime.slice(0, 16) : '';
                document.getElementById('editModal').classList.add('active');
            }
        } catch (error) {
            this.showToast(`Erro ao editar tarefa: ${error.message}`, 'error');
        }
    }

    async saveEdit() {
        const text = document.getElementById('editTaskInput').value.trim();
        const priority = document.getElementById('editPrioritySelect').value;
        const category = document.getElementById('editCategoryInput').value.trim();
        const reminder = document.getElementById('editReminderInput').value;
        
        if (!text) return this.showToast('Por favor, digite uma tarefa', 'error');
        
        // CORREÇÃO ROBUSTA: Remover completamente a validação de data futura no frontend
        // Isso permite que o usuário adicione tarefas com lembretes para qualquer momento

        try {
            // Verificar se a categoria existe ou criar nova
            let categoryId = null;
            if (category) {
                const categories = await TaskFlowAPI.getCategories();
                const existingCategory = categories.find(c => c.name.toLowerCase() === category.toLowerCase());
                
                if (existingCategory) {
                    categoryId = existingCategory.id;
                } else {
                    // Criar nova categoria
                    const newCategory = await TaskFlowAPI.addCategory({
                        name: category,
                        color: this.getRandomColor()
                    });
                    categoryId = newCategory.id;
                }
            }
            
            // Atualizar tarefa via API
            const taskData = {
                text,
                priority,
                category_id: categoryId,
                reminder_datetime: reminder || null
            };
            
            await TaskFlowAPI.updateTask(this.editingTaskId, taskData);
            
            // Atualizar interface
            this.closeEditModal();
            await this.renderTasks();
            await this.updateStats();
            await this.updateCategoryFilter();
            
            this.showToast('Tarefa atualizada!');
        } catch (error) {
            this.showToast(`Erro ao atualizar tarefa: ${error.message}`, 'error');
        }
    }

    closeEditModal() {
        document.getElementById('editModal').classList.remove('active');
        this.editingTaskId = null;
    }

    setFilter(filter) {
        this.currentFilter = filter;
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        this.renderTasks();
    }

    setCategoryFilter(category) {
        this.currentCategoryFilter = category;
        this.renderTasks();
    }

    async getFilteredTasks() {
        try {
            const filters = {};
            
            // Filtro por status
            switch (this.currentFilter) {
                case 'pendentes': 
                    filters.completed = false;
                    break;
                case 'concluidas': 
                    filters.completed = true;
                    break;
                case 'alta': 
                    filters.priority = 'alta';
                    break;
            }
            
            // Filtro por categoria
            if (this.currentCategoryFilter) {
                filters.category_id = parseInt(this.currentCategoryFilter);
            }
            
            return await TaskFlowAPI.getTasks(filters);
        } catch (error) {
            console.error('Erro ao filtrar tarefas:', error);
            return [];
        }
    }

    async clearCompleted() {
        if (confirm('Tem certeza que deseja limpar as tarefas concluídas?')) {
            try {
                const tasks = await TaskFlowAPI.getTasks({ completed: true });
                
                // Excluir cada tarefa concluída
                for (const task of tasks) {
                    await TaskFlowAPI.deleteTask(task.id);
                }
                
                // Atualizar interface
                await this.renderTasks();
                await this.updateStats();
                await this.updateCategoryFilter();
                
                this.showToast('Tarefas concluídas removidas!');
            } catch (error) {
                this.showToast(`Erro ao limpar tarefas concluídas: ${error.message}`, 'error');
            }
        }
    }

    async renderTasks() {
        const container = document.getElementById('tasksContainer');
        const filteredTasks = await this.getFilteredTasks();
        container.innerHTML = '';

        if (filteredTasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clipboard-list"></i>
                    <h3>Nenhuma tarefa encontrada</h3>
                    <p>Adicione sua primeira tarefa para começar a organizar seu dia!</p>
                </div>`;
            return;
        }

        filteredTasks.forEach(task => {
            const temp = document.createElement('div');
            temp.innerHTML = this.createTaskHTML(task);
            const taskElement = temp.firstElementChild;
            container.appendChild(taskElement);

            taskElement.querySelector('.task-checkbox').addEventListener('click', () => {
                this.toggleTask(task.id);
            });

            taskElement.querySelector('.edit-btn').addEventListener('click', () => {
                this.editTask(task.id);
            });

            taskElement.querySelector('.delete-btn').addEventListener('click', () => {
                this.deleteTask(task.id);
            });
        });
    }

    createTaskHTML(task) {
        const reminderHTML = task.reminder_datetime ? this.createReminderHTML(task.reminder_datetime) : '';
        const categoryHTML = task.category ? `<span class="task-category" style="background-color: ${task.category.color}">${this.escapeHtml(task.category.name)}</span>` : '';
        
        return `
        <div class="task-item ${task.completed ? 'completed' : ''}" data-task-id="${task.id}">
            <div class="task-checkbox ${task.completed ? 'checked' : ''}">
                ${task.completed ? '<i class="fas fa-check"></i>' : ''}
            </div>
            <div class="task-content">
                <div class="task-text">${this.escapeHtml(task.text)}</div>
                <div class="task-meta">
                    ${categoryHTML}
                    <span class="priority-badge priority-${task.priority}">${task.priority}</span>
                    ${reminderHTML}
                </div>
            </div>
            <div class="task-actions">
                <button class="action-btn edit-btn"><i class="fas fa-edit"></i></button>
                <button class="action-btn delete-btn"><i class="fas fa-trash"></i></button>
            </div>
        </div>`;
    }

    createReminderHTML(reminderDatetime) {
        const reminderDate = new Date(reminderDatetime);
        const now = new Date();
        const isOverdue = reminderDate < now;
        const dateStr = reminderDate.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <span class="task-reminder ${isOverdue ? 'overdue' : ''}">
                <i class="fas fa-bell"></i>
                ${dateStr}
            </span>
        `;
    }

    escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async updateStats() {
        try {
            const stats = await TaskFlowAPI.getStats();
            
            document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
            document.getElementById('completedTasks').textContent = stats.completed_tasks || 0;
            document.getElementById('pendingTasks').textContent = stats.pending_tasks || 0;
        } catch (error) {
            console.error('Erro ao atualizar estatísticas:', error);
        }
    }

    async updateCategoryFilter() {
        try {
            const categoryFilter = document.getElementById('categoryFilter');
            const categories = await TaskFlowAPI.getCategories();
            
            // Manter a opção "Todas as categorias"
            categoryFilter.innerHTML = '<option value="">Todas as categorias</option>';
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categoryFilter.appendChild(option);
            });
            
            // Restaurar seleção atual
            categoryFilter.value = this.currentCategoryFilter;
        } catch (error) {
            console.error('Erro ao atualizar filtro de categorias:', error);
        }
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        toastMessage.textContent = message;
        
        // Alterar cor baseada no tipo
        if (type === 'error') {
            toast.style.background = '#ff6b6b';
        } else {
            toast.style.background = '#4caf50';
        }
        
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    // Funcionalidades de tema
    async toggleTheme() {
        try {
            await TaskFlowAPI.toggleTheme();
            
            const newTheme = TaskFlowAPI.settings.theme;
            this.showToast(`Tema ${newTheme === 'dark' ? 'escuro' : 'claro'} ativado!`);
        } catch (error) {
            this.showToast(`Erro ao alternar tema: ${error.message}`, 'error');
        }
    }

    toggleExportMenu() {
        document.getElementById('exportMenu').classList.toggle('show');
    }

    exportData(format) {
        document.getElementById('exportMenu').classList.remove('show');
        
        if (format === 'ics') {
            this.exportICS();
        }
    }

    async exportICS() {
        try {
            const result = await TaskFlowAPI.exportToICalendar();
            this.showToast(result.message);
        } catch (error) {
            this.showToast(`Erro ao exportar para iCalendar: ${error.message}`, 'error');
        }
    }

    // Funcionalidades de notificação
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showToast('Notificações ativadas!');
                }
            });
        }
    }

    startNotificationCheck() {
        // Verificar notificações a cada minuto
        this.notificationCheckInterval = setInterval(() => {
            this.checkReminders();
        }, 60000);
        
        // Verificar imediatamente
        this.checkReminders();
    }

    async checkReminders() {
        const now = new Date();
        const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60000);
        
        try {
            const tasks = await TaskFlowAPI.getTasks({ completed: false });
            
            tasks.forEach(task => {
                if (task.reminder_datetime && !task.completed && !task.notified) {
                    const reminderDate = new Date(task.reminder_datetime);
                    
                    // Notificar se o lembrete está entre agora e 5 minutos
                    if (reminderDate >= now && reminderDate <= fiveMinutesFromNow) {
                        this.showNotification(task);
                        
                        // Marcar como notificado
                        TaskFlowAPI.updateTask(task.id, { notified: true });
                    }
                }
            });
        } catch (error) {
            console.error('Erro ao verificar lembretes:', error);
        }
    }

    showNotification(task) {
        const notification = new Notification('TaskFlow - Lembrete', {
            body: `${task.text}${task.category ? ` (${task.category.name})` : ''}`,
            icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23667eea"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>',
            tag: task.id,
            requireInteraction: true
        });

        notification.onclick = () => {
            window.focus();
            notification.close();
        };

        // Auto-fechar após 10 segundos
        setTimeout(() => notification.close(), 10000);
    }
    
    // Utilitários
    getRandomColor() {
        const colors = [
            '#667eea', '#764ba2', '#6B8E23', '#2196F3', '#FF9800', 
            '#9C27B0', '#673AB7', '#3F51B5', '#009688', '#4CAF50'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }
}

// Inicializar a aplicação quando o DOM estiver carregado
window.addEventListener('DOMContentLoaded', () => new TaskManager());
