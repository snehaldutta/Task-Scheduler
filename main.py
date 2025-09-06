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
        // Track which alerts have been shown today
        const alertedTasks = new Set();
        const today = new Date().toDateString();
        
        console.log('🚀 Alert system initializing...');
        
        // Load previously alerted tasks from localStorage (with error handling)
        try {
            const storedAlerts = localStorage.getItem('alertedTasks');
            if (storedAlerts) {
                const parsed = JSON.parse(storedAlerts);
                if (parsed.date === today) {
                    parsed.tasks.forEach(t => alertedTasks.add(t));
                    console.log('📚 Loaded', alertedTasks.size, 'previously alerted tasks');
                }
            }
        } catch (e) {
            console.warn('⚠️ localStorage not available or corrupted:', e);
        }
        
        // ============================================
        // DELETE TASK FUNCTION - Deletes from DB and Webpage
        // ============================================
        async function deleteTask(taskId) {
            console.log(`🗑️ Attempting to delete task ${taskId}...`);
            
            try {
                // 1. First, delete from database
                const response = await fetch(`/delete-task/${taskId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    console.log(`✓ Task ${taskId} deleted from database`);
                    
                    // 2. Then remove from webpage with animation
                    const taskElement = document.getElementById(`task-${taskId}`) || 
                                      document.querySelector(`[data-task-id="${taskId}"]`);
                    
                    if (taskElement) {
                        console.log(`Found task element, removing from webpage...`);
                        
                        // Apply animation styles
                        taskElement.style.transition = 'all 0.5s ease-out';
                        taskElement.style.opacity = '0';
                        taskElement.style.transform = 'translateX(100%)';
                        taskElement.style.backgroundColor = '#fee2e2';
                        
                        // Remove from DOM after animation completes
                        setTimeout(() => {
                            taskElement.remove();
                            console.log(`✓ Task ${taskId} removed from webpage`);
                        }, 500);
                        
                        return true;
                    } else {
                        console.error(`Could not find task element with id: task-${taskId}`);
                        await refreshTaskList();
                        return true;
                    }
                } else {
                    console.error(`✗ Failed to delete task ${taskId}: Server returned ${response.status}`);
                    return false;
                }
                
            } catch (error) {
                console.error(`✗ Error deleting task ${taskId}:`, error);
                return false;
            }
        }
        
        // Function to refresh the task list from server
        async function refreshTaskList() {
            try {
                const response = await fetch('/get-tasks', {
                    method: 'GET'
                });
                
                if (response.ok) {
                    const newHTML = await response.text();
                    const taskList = document.getElementById('task_list');
                    if (taskList) {
                        taskList.outerHTML = newHTML;
                        console.log('✓ Task list refreshed from server');
                    }
                }
            } catch (error) {
                console.error('Error refreshing task list:', error);
            }
        }
        
        // ============================================
        // IMPROVED ALERT SYSTEM
        // ============================================
        function showAlert(taskText, taskId) {
            console.log('🔔 Showing alert for:', taskText);
            
            // Try multiple alert methods for better compatibility
            let alertShown = false;
            
            // Method 1: Browser Notification API
            if ('Notification' in window && Notification.permission === 'granted') {
                try {
                    new Notification('⏰ Task Reminder', {
                        body: taskText,
                        icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">⏰</text></svg>',
                        tag: `task-${taskId}`, // Prevent duplicates
                        requireInteraction: true // Keep notification visible
                    });
                    alertShown = true;
                    console.log('✓ Browser notification shown');
                } catch (e) {
                    console.warn('⚠️ Notification failed:', e);
                }
            }
            
            // Method 2: Browser alert (fallback)
            if (!alertShown) {
                try {
                    alert(`TASK REMINDER: ${taskText}`);
                    alertShown = true;
                    console.log('✓ Browser alert shown');
                } catch (e) {
                    console.warn('⚠️ Alert failed:', e);
                }
            }
            
            // Method 3: Visual alert on page (last resort)
            if (!alertShown) {
                showVisualAlert(taskText);
                alertShown = true;
                console.log('✓ Visual alert shown');
            }
            
            return alertShown;
        }
        
        function showVisualAlert(taskText) {
            // Create a visual alert div
            const alertDiv = document.createElement('div');
            alertDiv.innerHTML = `
                <div class="alert alert-warning shadow-lg fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md">
                    <div>
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                        <div>
                            <h3 class="font-bold">Task Reminder!</h3>
                            <div class="text-xs">${taskText}</div>
                        </div>
                    </div>
                    <div class="flex-none">
                        <button class="btn btn-sm" onclick="this.parentElement.parentElement.remove()">OK</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(alertDiv);
            
            // Auto-remove after 10 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 10000);
        }
        
        // ============================================
        // CHECK REMINDERS FUNCTION (IMPROVED)
        // ============================================
        async function checkReminders() {
            const now = new Date();
            const currentHour = String(now.getHours()).padStart(2, '0');
            const currentMinute = String(now.getMinutes()).padStart(2, '0');
            const currentTime = `${currentHour}:${currentMinute}`;
            
            console.log(`🔍 Checking reminders at ${currentTime}...`);
            
            // Get all task elements dynamically
            const taskElements = document.querySelectorAll('[data-task-time]');
            console.log(`📋 Found ${taskElements.length} tasks to check`);
            
            if (taskElements.length === 0) {
                console.log('📋 No tasks found to check');
                return;
            }
            
            for (const elem of taskElements) {
                const taskTime = elem.dataset.taskTime;
                const taskId = elem.dataset.taskId;
                const taskText = elem.querySelector('.card-title')?.textContent || 'Unknown Task';
                
                if (!taskTime || !taskId) {
                    console.warn('⚠️ Task missing time or ID:', {taskTime, taskId});
                    continue;
                }
                
                // Extract HH:MM from HH:MM:SS format
                const taskHourMin = taskTime.substring(0, 5);
                
                // Create unique key for this task alert
                const alertKey = `${taskId}-${taskTime}`;
                
                console.log(`🕐 Checking task ${taskId} (${taskText}): ${taskHourMin} vs ${currentTime}`);
                
                // Check if time matches and we haven't alerted yet
                if (taskHourMin === currentTime && !alertedTasks.has(alertKey)) {
                    console.log(`🎯 TIME MATCH! Triggering alert for: ${taskText}`);
                    
                    // Show notification
                    const alertShown = showAlert(taskText, taskId);
                    
                    if (alertShown) {
                        // Mark as alerted
                        alertedTasks.add(alertKey);
                        
                        // Save to localStorage (with error handling)
                        try {
                            localStorage.setItem('alertedTasks', JSON.stringify({
                                date: today,
                                tasks: Array.from(alertedTasks)
                            }));
                            console.log('💾 Saved alert to localStorage');
                        } catch (e) {
                            console.warn('⚠️ Could not save to localStorage:', e);
                        }
                        
                        // AUTO-DELETE AFTER NOTIFICATION
                        console.log(`⏳ Will delete task ${taskId} in 2 seconds...`);
                        
                        setTimeout(async () => {
                            console.log(`🗑️ Now deleting task ${taskId}...`);
                            const deleteSuccess = await deleteTask(taskId);
                            
                            if (deleteSuccess) {
                                console.log(`✅ Task "${taskText}" completed and deleted`);
                            } else {
                                console.log(`❌ Failed to delete task "${taskText}"`);
                            }
                        }, 2000);
                    }
                }
            }
        }
        
        // ============================================
        // INITIALIZATION
        // ============================================
        console.log('🔐 Requesting notification permission...');
        
        // Request notification permission on load
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                Notification.requestPermission().then(permission => {
                    console.log('🔔 Notification permission:', permission);
                });
            } else {
                console.log('🔔 Current notification permission:', Notification.permission);
            }
        } else {
            console.warn('⚠️ Notifications not supported in this browser');
        }
        
        // Check every 15 seconds instead of 30 for better accuracy
        const checkInterval = setInterval(checkReminders, 15000);
        console.log('⏰ Started reminder checker (every 15 seconds)');
        
        // Check immediately on load
        setTimeout(() => {
            console.log('🚀 Running initial reminder check...');
            checkReminders();
        }, 1000);
        
        // Debug function to test alerts
        window.testAlert = function(taskText = 'Test Task') {
            console.log('🧪 Testing alert system...');
            showAlert(taskText, 'test');
        };
        
        // Make functions available globally
        window.deleteTask = deleteTask;
        window.checkReminders = checkReminders;
        window.refreshTaskList = refreshTaskList;
        window.showAlert = showAlert;
        
        console.log('✅ Alert system fully initialized!');
        console.log('💡 Test with: testAlert("My Test Task")
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
                # Optional: Add manual delete button
                Button(
                    "🗑️",
                    onclick=f"deleteTask({task_id})",
                    cls="btn btn-sm btn-ghost btn-circle",
                    title="Delete task"
                ),
                cls="flex justify-between items-center"
            ),
            P(f"{task['time']}"),
            cls="card-body"
        ),
        cls="card bg-base-200 shadow-md my-2 transition-all duration-500",
        # IMPORTANT: Add both id and data attributes
        id=f"task-{task_id}",  # This was missing!
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
                cls="input input-bordered w-full"
            ),
            Input(
                type="time",
                name="time",
                required=True,
                cls="input input-bordered w-full mt-2"
            ),
            Button("➕ Add Task", type="submit", cls="btn btn-primary mt-4 w-full"),
            cls="card-body"
        ),
        method="post",
        hx_post="/submit-task",
        hx_target="#task_list",
        hx_swap="outerHTML",
        hx_on_after_request="this.reset(); checkReminders();",
        cls="card bg-base-100 shadow-xl w-96"
    )

    return Div(
        Header("🗓 Task Scheduler", cls="text-3xl font-bold text-center mb-4"),
        Div(
            form,
            cls="flex justify-center mb-8"
        ),
        Hr(),
        get_task_list(),
        reminder_script(),
        # Fixed: Use Div instead of Footer
        Div("Made with ❤️ by Snehal", cls="text-xs text-center mt-8 text-gray-500"),
        cls="container mx-auto p-4"
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