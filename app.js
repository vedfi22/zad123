// Загрузка задач из localStorage
let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

// DOM-элементы
const taskForm = document.getElementById('task-form');
const taskInput = document.getElementById('task-input');
const taskList = document.getElementById('task-list');

// Добавление задачи
taskForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = taskInput.value.trim();
  if (text) {
    tasks.push({ text, completed: false });
    saveTasks();
    renderTasks();
    taskInput.value = '';
  }
});

// Рендер задач
function renderTasks() {
  taskList.innerHTML = '';
  tasks.forEach((task, index) => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span class="${task.completed ? 'completed' : ''}">${task.text}</span>
      <button class="delete-btn" data-id="${index}">×</button>
    `;
    li.querySelector('span').addEventListener('click', () => toggleTask(index));
    li.querySelector('.delete-btn').addEventListener('click', () => deleteTask(index));
    taskList.appendChild(li);
  });
}

// Сохранение задач
function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

// Инициализация
renderTasks();