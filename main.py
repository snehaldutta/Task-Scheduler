from fasthtml.common import * 
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

# --- Add Tailwind + DaisyUI via CDN ---
app, rt = fast_app(
    hdrs=[
        Link(rel="icon", href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📅</text></svg>"),
        # Load Tailwind first
        Script(src="https://cdn.tailwindcss.com"),
        # Then load DaisyUI as a separate CDN
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"),
        # Optional: Configure theme
        Script("""
            // Optional theme configuration
            document.documentElement.setAttribute('data-theme', 'light');
        """),
    ],
    debug=True, live=True
)

db_client: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# ---------------- Script ----------------
js_script = """
(function() {
    // Wrap everything in an IIFE to avoid global scope pollution
    console.log('🚀 Alert system initializing...');
    
    // Use in-memory storage instead of localStorage for production compatibility
    let alertedTasks = new Set();
    const today = new Date().toDateString();
    
    // Safe localStorage wrapper
    const storage = {
        get: function(key) {
            try {
                if (typeof(Storage) !== "undefined" && localStorage) {
                    return localStorage.getItem(key);
                }
            } catch(e) {
                console.warn('Storage not available:', e);
            }
            return null;
        },
        set: function(key, value) {
            try {
                if (typeof(Storage) !== "undefined" && localStorage) {
                    localStorage.setItem(key, value);
                    return true;
                }
            } catch(e) {
                console.warn('Storage not available:', e);
            }
            return false;
        }
    };
    
    // Try to load from storage, but don't fail if it doesn't work
    try {
        const stored = storage.get('alertedTasks');
        if (stored) {
            const parsed = JSON.parse(stored);
            if (parsed.date === today) {
                parsed.tasks.forEach(t => alertedTasks.add(t));
                console.log('📚 Loaded', alertedTasks.size, 'previously alerted tasks');
            }
        }
    } catch(e) {
        console.log('Starting with fresh alert tracking');
    }
    
    // ============================================
    // DELETE TASK FUNCTION
    // ============================================
    window.deleteTask = async function(taskId) {
        console.log(`🗑️ Attempting to delete task ${taskId}...`);
        
        try {
            const response = await fetch(`/delete-task/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log(`✓ Task ${taskId} deleted from database`);
                
                // Find and remove the task element
                const taskElement = document.getElementById(`task-${taskId}`);
                
                if (taskElement) {
                    console.log(`Found task element, removing from webpage...`);
                    
                    // Apply fade out animation
                    taskElement.style.transition = 'all 0.5s ease-out';
                    taskElement.style.opacity = '0';
                    taskElement.style.transform = 'translateX(100%)';
                    taskElement.style.backgroundColor = '#fee2e2';
                    
                    // Remove after animation
                    setTimeout(() => {
                        taskElement.remove();
                        console.log(`✓ Task ${taskId} removed from webpage`);
                    }, 500);
                    
                    return true;
                } else {
                    console.error(`Could not find task element with id: task-${taskId}`);
                    // Refresh the task list as fallback
                    window.refreshTaskList();
                    return true;
                }
            } else {
                console.error(`Failed to delete task: ${response.status}`);
                return false;
            }
        } catch (error) {
            console.error(`Error deleting task:`, error);
            return false;
        }
    };
    
    // ============================================
    // REFRESH TASK LIST
    // ============================================
    window.refreshTaskList = async function() {
        try {
            const response = await fetch('/get-tasks');
            if (response.ok) {
                const newHTML = await response.text();
                const taskList = document.getElementById('task_list');
                if (taskList) {
                    taskList.outerHTML = newHTML;
                    console.log('✓ Task list refreshed');
                }
            }
        } catch (error) {
            console.error('Error refreshing:', error);
        }
    };
    
    // ============================================
    // VISUAL ALERT (ALWAYS WORKS)
    // ============================================
    function showVisualAlert(taskText, taskId) {
        const alertDiv = document.createElement('div');
        alertDiv.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; animation: slideDown 0.5s ease;';
        alertDiv.innerHTML = `
            <div class="alert alert-warning shadow-lg" style="min-width: 300px; max-width: 500px;">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <div>
                        <h3 class="font-bold">Task Reminder!</h3>
                        <div class="text-sm">${taskText}</div>
                        <div class="text-xs opacity-70">This task will be auto-deleted in 3 seconds...</div>
                    </div>
                </div>
                <div class="flex-none">
                    <button class="btn btn-sm" onclick="this.closest('div[style]').remove()">Dismiss</button>
                </div>
            </div>
        `;
        
        // Add animation keyframes if not already added
        if (!document.getElementById('alert-animations')) {
            const style = document.createElement('style');
            style.id = 'alert-animations';
            style.textContent = `
                @keyframes slideDown {
                    from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
                    to { opacity: 1; transform: translateX(-50%) translateY(0); }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(alertDiv);
        
        // Play sound if possible
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0fPTgjMGHm7A7+OZURE');
            audio.play().catch(e => console.log('Audio play failed:', e));
        } catch(e) {
            console.log('Audio not supported');
        }
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 10000);
    }
    
    // ============================================
    // IMPROVED ALERT SYSTEM
    // ============================================
    window.showAlert = function(taskText, taskId) {
        console.log('🔔 Showing alert for:', taskText);
        
        // Always show visual alert first (guaranteed to work)
        showVisualAlert(taskText, taskId);
        
        // Try browser notification as bonus
        if ('Notification' in window && Notification.permission === 'granted') {
            try {
                new Notification('Task Reminder', {
                    body: taskText,
                    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">⏰</text></svg>',
                    tag: `task-${taskId}`,
                    requireInteraction: false
                });
                console.log('✓ Browser notification shown');
            } catch(e) {
                console.log('Notification API not available');
            }
        }
        
        return true;
    };
    
    // ============================================
    // CHECK REMINDERS FUNCTION
    // ============================================
    window.checkReminders = function() {
        const now = new Date();
        const currentHour = String(now.getHours()).padStart(2, '0');
        const currentMinute = String(now.getMinutes()).padStart(2, '0');
        const currentTime = `${currentHour}:${currentMinute}`;
        
        console.log(`🔍 Checking reminders at ${currentTime}...`);
        
        // Get all task elements
        const taskElements = document.querySelectorAll('[data-task-time]');
        console.log(`📋 Found ${taskElements.length} tasks to check`);
        
        taskElements.forEach(elem => {
            const taskTime = elem.dataset.taskTime;
            const taskId = elem.dataset.taskId;
            const taskTextElem = elem.querySelector('.card-title');
            const taskText = taskTextElem ? taskTextElem.textContent : 'Task Reminder';
            
            if (!taskTime || !taskId) return;
            
            // Extract HH:MM from time
            const taskHourMin = taskTime.substring(0, 5);
            const alertKey = `${taskId}-${taskTime}-${today}`;
            
            console.log(`Checking: Task ${taskId} at ${taskHourMin} vs current ${currentTime}`);
            
            if (taskHourMin === currentTime && !alertedTasks.has(alertKey)) {
                console.log(`🎯 TIME MATCH! Alerting for: ${taskText}`);
                
                // Mark as alerted immediately to prevent duplicates
                alertedTasks.add(alertKey);
                
                // Save to storage (but don't fail if it doesn't work)
                try {
                    storage.set('alertedTasks', JSON.stringify({
                        date: today,
                        tasks: Array.from(alertedTasks)
                    }));
                } catch(e) {
                    console.log('Could not persist alert state');
                }
                
                // Show the alert
                window.showAlert(taskText, taskId);
                
                // Auto-delete after 3 seconds
                console.log(`⏳ Scheduling deletion for task ${taskId}...`);
                setTimeout(() => {
                    console.log(`🗑️ Auto-deleting task ${taskId}...`);
                    window.deleteTask(taskId).then(success => {
                        if (success) {
                            console.log(`✅ Task "${taskText}" completed and deleted`);
                        }
                    });
                }, 3000);
            }
        });
    };
    
    // ============================================
    // INITIALIZATION
    // ============================================
    
    // Request notification permission (but don't rely on it)
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            console.log('Notification permission:', permission);
        }).catch(e => {
            console.log('Notification permission request failed');
        });
    }
    
    // Start checking every 10 seconds for better accuracy
    let checkInterval;
    
    function startChecking() {
        // Clear any existing interval
        if (checkInterval) clearInterval(checkInterval);
        
        // Check every 10 seconds
        checkInterval = setInterval(window.checkReminders, 10000);
        console.log('Started reminder checker (every 10 seconds)');
        
        // Initial check after 2 seconds
        setTimeout(window.checkReminders, 2000);
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startChecking);
    } else {
        startChecking();
    }
    
    // Test function
    window.testAlert = function(text = 'Test Task') {
        console.log('🧪 Testing alert system...');
        window.showAlert(text, 'test-id');
    };
    
    console.log('✅ Alert system ready!');
    console.log('💡 Test with: testAlert("My Test")');
})();
"""

# ---------------- Database helpers ----------------
def delete_task_from_db(task_id):
    """Delete a task from the database"""
    db_client.table("TodoTable").delete().eq("id", task_id).execute()
    return True

def add_tasks_to_db(task, time):
    """Add a new task to the database"""
    db_client.table("TodoTable").insert(
        {"task": task, "time": time}
    ).execute()

def get_tasks_from_db():
    """Get all tasks from the database"""
    task_res = db_client.table("TodoTable").select("*").order("id", desc=True).execute()
    return task_res.data

# ---------------- UI helpers ----------------
def render_tasks(task):
    """Render a single task card"""
    task_id = task.get("id", "")
    
    return Div(
        Div(
            Div(
                Header(task["task"], cls="card-title"),
                Button(
                    "🗑️",
                    onclick=f"deleteTask({task_id})",
                    cls="btn btn-sm btn-ghost btn-circle",
                    title="Delete task"
                ),
                cls="flex justify-between items-center"
            ),
            P(f"{task['time']}", cls="text-sm opacity-75"),
            cls="card-body"
        ),
        cls="card bg-base-200 shadow-md my-2 transition-all duration-500 hover:shadow-lg",
        # CRITICAL: Both id and data attributes are needed
        id=f"task-{task_id}",
        **{
            "data-task-id": str(task_id),
            "data-task-time": task["time"]
        }
    )

def get_task_list():
    """Get the task list component"""
    tasks = get_tasks_from_db()
    if not tasks:
        return Div(
            P("No tasks scheduled yet. Add your first task above!", 
              cls="text-center text-gray-500 italic py-4"),
            id="task_list",
            cls="space-y-2"
        )
    
    return Div(
        *[render_tasks(task) for task in tasks],
        id="task_list",
        cls="space-y-2"
    )

def reminder_script():
    """Return the JavaScript for reminders and auto-delete"""
    return Script(js_script)

def render_content():
    """Render the main page content"""
    form = Form(
        Div(
            Input(
                type="text",
                name="task",
                placeholder="Enter task",
                required=True,
                maxlength=50,
                id='task-input',
                cls="input input-bordered w-full"
            ),
            Input(
                type="time",
                name="time",
                required=True,
                id='time-input',
                cls="input input-bordered w-full mt-2"
            ),
            Button("➕ Add Task", type="submit", cls="btn btn-primary mt-4 w-full"),
            cls="card-body"
        ),
        method="post",
        hx_post="/submit-task",
        hx_target="#task_list",
        hx_swap="outerHTML",
        hx_on__after_request="""
            document.getElementById('task-input').value=''; 
            document.getElementById('time-input').value=''; 
            document.getElementById('task-input').classList.add('input-success');
            setTimeout(() => {
                document.getElementById('task-input').classList.remove('input-success');
            }, 1000);
            setTimeout(checkReminders, 100);
        """,
        id='task-form',
        cls="card bg-base-100 shadow-xl w-96"
    )

    return Div(
        Header("📅 Task Scheduler", cls="text-3xl font-bold text-center mb-4"),
        P("Tasks will alert at scheduled time and auto-delete after 3 seconds", 
          cls="text-center text-sm text-gray-600 mb-4"),
        Div(
            form,
            cls="flex justify-center mb-8"
        ),
        Hr(),
        get_task_list(),
        reminder_script(),
        Div("Made with ❤️ by Snehal", cls="text-xs text-center mt-8 text-gray-500"),
        cls="container mx-auto p-4 max-w-2xl"
    )

# ---------------- Routes ----------------
@rt("/", methods=["GET"])
def get():
    """Main page route"""
    return Titled(render_content())

@rt("/submit-task", methods=["POST"])
def post(task: str, time: str):
    """Handle task submission"""
    # Normalize time input
    try:
        # Try parsing as HH:MM first
        parsed_time = datetime.strptime(time, "%H:%M")
        new_time = parsed_time.strftime("%H:%M:%S")
    except ValueError:
        try:
            # Try parsing as HH:MM:SS
            parsed_time = datetime.strptime(time, "%H:%M:%S")
            new_time = parsed_time.strftime("%H:%M:%S")
        except ValueError:
            # Invalid time format - return error
            return Div(
                Div("Invalid time format!", cls="alert alert-error mb-4"),
                get_task_list(),
                id="task_list"
            )
    
    add_tasks_to_db(task, new_time)
    return get_task_list()

@rt("/delete-task/{task_id}", methods=["DELETE"])
def delete_task(task_id: int):
    """Handle task deletion"""
    try:
        delete_task_from_db(task_id)
        return {"status": "success", "message": f"Task {task_id} deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@rt("/get-tasks", methods=["GET"])
def get_tasks_endpoint():
    """Endpoint to get just the task list HTML"""
    return get_task_list()

serve()