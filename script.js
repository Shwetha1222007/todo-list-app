// ===================================
// TASKMASTER PRO - JAVASCRIPT
// Professional Task Management System
// ===================================

// Global State Management
let currentView = 'all';
let currentFilter = 'all';
let notificationCheckInterval = null;
let alarmAudio = null;

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize alarm audio
    initializeAlarmAudio();

    // Load tasks from localStorage
    loadTasks();

    // Update UI states
    updateEmptyState();
    updateTaskCounts();
    updateProductivityRate();

    // Start live clock
    startLiveClock();

    // Check notification permission
    checkNotificationPermission();

    // Start notification checker
    startNotificationChecker();

    // Setup event listeners
    setupEventListeners();

    // Set minimum datetime to current time
    setMinDateTime();
}

/**
 * Start the live digital clock
 */
function startLiveClock() {
    function updateClock() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
        const dateStr = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const liveTimeEl = document.getElementById('liveTime');
        const liveDateEl = document.getElementById('liveDate');

        if (liveTimeEl) liveTimeEl.textContent = timeStr;
        if (liveDateEl) liveDateEl.textContent = dateStr;
    }

    updateClock();
    setInterval(updateClock, 1000);
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const view = this.dataset.view;
            switchView(view);
        });
    });

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            filterTasks();
        });
    });

    // Minimize input card
    const minimizeBtn = document.getElementById('minimizeInput');
    if (minimizeBtn) {
        minimizeBtn.addEventListener('click', function () {
            const inputBody = document.querySelector('.input-body');
            inputBody.style.display = inputBody.style.display === 'none' ? 'block' : 'none';
            this.querySelector('svg').style.transform =
                inputBody.style.display === 'none' ? 'rotate(180deg)' : 'rotate(0deg)';
        });
    }
}

/**
 * Set minimum datetime to current time
 */
function setMinDateTime() {
    const datetimeInput = document.getElementById('taskDateTime');
    if (datetimeInput) {
        const now = new Date();
        // Set min to 1 minute ago to be slightly more flexible with "now" selection
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset() - 1);
        datetimeInput.min = now.toISOString().slice(0, 16);
    }
}

/**
 * Switch between different views
 */
function switchView(view) {
    currentView = view;

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === view) {
            item.classList.add('active');
        }
    });

    // Update page title
    const titles = {
        'all': 'All Tasks',
        'today': 'Today\'s Tasks',
        'upcoming': 'Upcoming Tasks',
        'completed': 'Completed Tasks'
    };

    const subtitles = {
        'all': 'Manage your tasks efficiently',
        'today': 'Focus on what matters today',
        'upcoming': 'Plan ahead for success',
        'completed': 'Review your achievements'
    };

    document.getElementById('pageTitle').textContent = titles[view];
    document.getElementById('pageSubtitle').textContent = subtitles[view];

    // Filter tasks based on view
    filterTasks();
}

/**
 * Filter tasks based on current view and filter
 */
function filterTasks() {
    const taskItems = document.querySelectorAll('.task-item');
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    taskItems.forEach(item => {
        let showByView = true;
        let showByFilter = true;

        const isCompleted = item.classList.contains('completed');
        const reminderTime = item.dataset.reminderTime;

        // View filtering
        if (currentView === 'today' && reminderTime) {
            const taskDate = new Date(reminderTime);
            const taskDay = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate());
            showByView = taskDay.getTime() === today.getTime();
        } else if (currentView === 'upcoming' && reminderTime) {
            const taskDate = new Date(reminderTime);
            showByView = taskDate > now && !isCompleted;
        } else if (currentView === 'completed') {
            showByView = isCompleted;
        }

        // Filter by completion status
        if (currentFilter === 'active') {
            showByFilter = !isCompleted;
        } else if (currentFilter === 'completed') {
            showByFilter = isCompleted;
        }

        item.style.display = (showByView && showByFilter) ? 'flex' : 'none';
    });

    updateEmptyState();
}

/**
 * Initialize alarm audio using Web Audio API
 */
function initializeAlarmAudio() {
    alarmAudio = {
        play: function () {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();

                // First tone
                const oscillator1 = audioContext.createOscillator();
                const gainNode1 = audioContext.createGain();

                oscillator1.connect(gainNode1);
                gainNode1.connect(audioContext.destination);

                oscillator1.frequency.value = 800;
                oscillator1.type = 'sine';

                gainNode1.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode1.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

                oscillator1.start(audioContext.currentTime);
                oscillator1.stop(audioContext.currentTime + 0.5);

                // Second tone
                setTimeout(() => {
                    const oscillator2 = audioContext.createOscillator();
                    const gainNode2 = audioContext.createGain();

                    oscillator2.connect(gainNode2);
                    gainNode2.connect(audioContext.destination);

                    oscillator2.frequency.value = 1000;
                    oscillator2.type = 'sine';

                    gainNode2.gain.setValueAtTime(0.3, audioContext.currentTime);
                    gainNode2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

                    oscillator2.start(audioContext.currentTime);
                    oscillator2.stop(audioContext.currentTime + 0.5);
                }, 200);
            } catch (error) {
                console.error('Error playing alarm sound:', error);
            }
        }
    };
}

/**
 * Check notification permission and show banner if needed
 */
function checkNotificationPermission() {
    const permissionBanner = document.getElementById('notificationPermission');

    if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return;
    }

    if (Notification.permission === 'default') {
        permissionBanner.classList.remove('hidden');
    }
}

/**
 * Request notification permission
 */
function requestNotificationPermission() {
    if (!('Notification' in window)) {
        alert('This browser does not support desktop notifications');
        return;
    }

    Notification.requestPermission().then(function (permission) {
        const permissionBanner = document.getElementById('notificationPermission');

        if (permission === 'granted') {
            permissionBanner.classList.add('hidden');
            new Notification('TaskMaster Pro 🎉', {
                body: 'Notifications enabled! You\'ll receive timely reminders for your tasks.',
                icon: '✅',
                tag: 'permission-granted'
            });
        } else {
            alert('Please enable notifications in your browser settings to receive task reminders.');
        }
    });
}

/**
 * Start checking for due tasks
 */
function startNotificationChecker() {
    // Check every 10 seconds
    notificationCheckInterval = setInterval(() => {
        // Only run check and potentially reload if user isn't typing
        if (!document.activeElement || !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            checkForDueTasks();
        }
    }, 10000);
    // Check immediately
    checkForDueTasks();
}

/**
 * Check for tasks that are due
 */
function checkForDueTasks() {
    const taskList = document.getElementById('taskList');
    const now = new Date();

    // Normalize "now" to minutes for strict comparison if needed
    // but here we want exact or past due
    let dueCount = 0;

    taskList.querySelectorAll('.task-item').forEach(function (taskItem) {
        if (taskItem.classList.contains('completed')) {
            return;
        }

        const reminderTime = taskItem.dataset.reminderTime;
        if (!reminderTime) {
            return;
        }

        const taskTime = new Date(reminderTime);

        // FIX 4 & 5: Strict Comparison
        // We compare the full Date objects (Date + Time)
        // Alarm only triggers if current time is >= scheduled time
        if (now >= taskTime) {
            if (taskItem.dataset.notified !== 'true') {
                const taskText = taskItem.querySelector('.task-text').textContent;

                // Audio alarm
                alarmAudio.play();

                // Visual alarm
                taskItem.style.animation = 'pulse 1s ease-in-out infinite';
                taskItem.classList.add('priority-high');

                // Desktop notification
                if (Notification.permission === 'granted') {
                    sendTaskNotification(taskText, taskTime);
                }

                // Mark as notified and save state
                taskItem.dataset.notified = 'true';
                saveTasks();

                dueCount++;
            }
        } else {
            // Task is still in the future, just update urgency if applicable
            const timeDiff = taskTime - now;
            updateTaskUrgency(taskItem, timeDiff);
        }
    });

    // Update notification badge
    const badge = document.getElementById('notificationBadge');
    if (dueCount > 0) {
        badge.textContent = dueCount;
        badge.classList.remove('hidden');
    }
}

/**
 * Send notification for a due task
 */
function sendTaskNotification(taskText, taskTime) {
    const notification = new Notification('⏰ Task Reminder - TaskMaster Pro', {
        body: `${taskText}\nDue: ${formatDateTime(taskTime)}`,
        icon: '📝',
        tag: 'task-' + Date.now(),
        requireInteraction: true
    });

    notification.onclick = function () {
        window.focus();
        notification.close();
    };
}

/**
 * Update task urgency styling
 */
function updateTaskUrgency(taskItem, timeDiff) {
    const timeBadge = taskItem.querySelector('.time-badge');
    if (!timeBadge) {
        return;
    }

    // Mark as urgent if less than 1 hour remaining
    if (timeDiff > 0 && timeDiff <= 3600000) {
        timeBadge.classList.add('urgent');
    } else {
        timeBadge.classList.remove('urgent');
    }
}

/**
 * Add a new task
 */
function addTask() {
    const taskInput = document.getElementById('taskInput');
    const taskDateTime = document.getElementById('taskDateTime');
    const taskPriority = document.getElementById('taskPriority');

    const taskText = taskInput.value.trim();
    const reminderTime = taskDateTime.value;
    const priority = taskPriority.value;

    if (taskText === '') {
        alert('⚠️ Please enter a task description!');
        taskInput.focus();
        return;
    }

    // Create the task
    createTaskElement(taskText, false, reminderTime, priority);

    // Clear inputs
    taskInput.value = '';
    taskDateTime.value = '';
    taskPriority.value = 'medium';
    taskInput.focus();

    // Save and update
    saveTasks();
    updateEmptyState();
    updateTaskCounts();
    updateProductivityRate();

    // Show notification permission if needed
    if (reminderTime && Notification.permission === 'default') {
        document.getElementById('notificationPermission').classList.remove('hidden');
    }
}

/**
 * Create a task element
 */
function createTaskElement(taskText, isCompleted, reminderTime, priority = 'medium', notified = false) {
    const taskList = document.getElementById('taskList');

    const taskItem = document.createElement('li');
    taskItem.className = `task-item priority-${priority}`;
    if (isCompleted) {
        taskItem.classList.add('completed');
    }

    if (reminderTime) {
        taskItem.dataset.reminderTime = reminderTime;
    }
    taskItem.dataset.priority = priority;
    if (notified) {
        taskItem.dataset.notified = 'true';
    }

    // Task content
    const taskContent = document.createElement('div');
    taskContent.className = 'task-content';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'task-checkbox';
    checkbox.checked = isCompleted;

    checkbox.addEventListener('change', function () {
        taskItem.classList.toggle('completed');
        saveTasks();
        updateTaskCounts();
        updateProductivityRate();
        filterTasks();
    });

    const taskDetails = document.createElement('div');
    taskDetails.className = 'task-details';

    const taskTextSpan = document.createElement('div');
    taskTextSpan.className = 'task-text';
    taskTextSpan.textContent = taskText;

    const taskMeta = document.createElement('div');
    taskMeta.className = 'task-meta';

    // Add time badge if reminder is set
    if (reminderTime) {
        const timeBadge = document.createElement('span');
        timeBadge.className = 'time-badge';
        timeBadge.innerHTML = `⏰ ${formatDateTime(new Date(reminderTime))}`;
        taskMeta.appendChild(timeBadge);
    }

    // Add priority badge
    const priorityBadge = document.createElement('span');
    priorityBadge.className = `priority-badge ${priority}`;
    priorityBadge.textContent = priority;
    taskMeta.appendChild(priorityBadge);

    taskDetails.appendChild(taskTextSpan);
    taskDetails.appendChild(taskMeta);

    taskContent.appendChild(checkbox);
    taskContent.appendChild(taskDetails);

    // Add click event to toggle
    taskTextSpan.addEventListener('click', function () {
        checkbox.checked = !checkbox.checked;
        taskItem.classList.toggle('completed');
        saveTasks();
        updateTaskCounts();
        updateProductivityRate();
        filterTasks();
    });

    // Task actions
    const taskActions = document.createElement('div');
    taskActions.className = 'task-actions';

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.textContent = 'Delete';

    deleteBtn.addEventListener('click', function () {
        taskItem.style.animation = 'taskSlideIn 0.3s ease-out reverse';
        setTimeout(function () {
            taskItem.remove();
            saveTasks();
            updateEmptyState();
            updateTaskCounts();
            updateProductivityRate();
        }, 300);
    });

    taskActions.appendChild(deleteBtn);

    taskItem.appendChild(taskContent);
    taskItem.appendChild(taskActions);

    taskList.appendChild(taskItem);
}

/**
 * Format datetime for display
 */
function formatDateTime(date) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const taskDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    let dateStr = '';
    if (taskDate.getTime() === today.getTime()) {
        dateStr = 'Today';
    } else if (taskDate.getTime() === tomorrow.getTime()) {
        dateStr = 'Tomorrow';
    } else {
        dateStr = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
    }

    const timeStr = date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    return `${dateStr} ${timeStr}`;
}

/**
 * Handle Enter key press
 */
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        addTask();
    }
}

/**
 * Save tasks to localStorage
 */
function saveTasks() {
    const taskList = document.getElementById('taskList');
    const tasks = [];

    taskList.querySelectorAll('.task-item').forEach(function (taskItem) {
        const taskText = taskItem.querySelector('.task-text').textContent;
        const isCompleted = taskItem.classList.contains('completed');
        const reminderTime = taskItem.dataset.reminderTime || null;
        const priority = taskItem.dataset.priority || 'medium';
        const notified = taskItem.dataset.notified === 'true';

        tasks.push({
            text: taskText,
            completed: isCompleted,
            reminderTime: reminderTime,
            priority: priority,
            notified: notified
        });
    });

    localStorage.setItem('todoTasks', JSON.stringify(tasks));
}

/**
 * Load tasks from localStorage
 */
function loadTasks() {
    const savedTasks = localStorage.getItem('todoTasks');

    if (savedTasks) {
        const tasks = JSON.parse(savedTasks);
        tasks.forEach(function (task) {
            createTaskElement(task.text, task.completed, task.reminderTime, task.priority, task.notified);
        });
    }
}

/**
 * Update empty state visibility
 */
function updateEmptyState() {
    const taskList = document.getElementById('taskList');
    const emptyState = document.getElementById('emptyState');

    const visibleTasks = Array.from(taskList.children).filter(
        item => item.style.display !== 'none'
    );

    if (visibleTasks.length === 0) {
        emptyState.classList.remove('hidden');
    } else {
        emptyState.classList.add('hidden');
    }
}

/**
 * Update task counts in navigation
 */
function updateTaskCounts() {
    const taskItems = document.querySelectorAll('.task-item');
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    let allCount = 0;
    let todayCount = 0;
    let upcomingCount = 0;
    let completedCount = 0;

    taskItems.forEach(item => {
        const isCompleted = item.classList.contains('completed');
        const reminderTime = item.dataset.reminderTime;

        allCount++;

        if (isCompleted) {
            completedCount++;
        }

        if (reminderTime) {
            const taskDate = new Date(reminderTime);
            const taskDay = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate());

            if (taskDay.getTime() === today.getTime()) {
                todayCount++;
            }

            if (taskDate > now && !isCompleted) {
                upcomingCount++;
            }
        }
    });

    document.getElementById('allCount').textContent = allCount;
    document.getElementById('todayCount').textContent = todayCount;
    document.getElementById('upcomingCount').textContent = upcomingCount;
    document.getElementById('completedCount').textContent = completedCount;
}

/**
 * Update productivity rate
 */
function updateProductivityRate() {
    const taskItems = document.querySelectorAll('.task-item');
    const total = taskItems.length;

    if (total === 0) {
        document.getElementById('productivityRate').textContent = '0%';
        return;
    }

    const completed = Array.from(taskItems).filter(
        item => item.classList.contains('completed')
    ).length;

    const rate = Math.round((completed / total) * 100);
    document.getElementById('productivityRate').textContent = rate + '%';
}
