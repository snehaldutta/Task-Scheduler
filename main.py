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
        
        // Load previously alerted tasks from localStorage
        const storedAlerts = localStorage.getItem('alertedTasks');
        if (storedAlerts) {
            const parsed = JSON.parse(storedAlerts);
            if (parsed.date === today) {
                parsed.tasks.forEach(t => alertedTasks.add(t));
            }
        }
        
        // ============================================
        // DELETE TASK FUNCTION - Deletes from DB and Webpage
        // ============================================
        async function deleteTask(taskId) {
            console.log(`Attempting to delete task ${taskId}...`);
            
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
                    const taskElement = document.getElementById(`task-${taskId}`);
                    
                    if (taskElement) {
                        console.log(`Found task element, removing from webpage...`);
                        
                        // Apply animation styles
                        taskElement.style.transition = 'all 0.5s ease-out';
                        taskElement.style.opacity = '0';
                        taskElement.style.transform = 'translateX(100%)';
                        taskElement.style.backgroundColor = '#fee2e2'; // Light red background
                        
                        // Remove from DOM after animation completes
                        setTimeout(() => {
                            taskElement.remove();
                            console.log(`✓ Task ${taskId} removed from webpage`);
                        }, 500);
                        
                        return true;
                    } else {
                        console.error(`Could not find task element with id: task-${taskId}`);
                        
                        // Alternative: Try to find by data attribute
                        const taskByData = document.querySelector(`[data-task-id="${taskId}"]`);
                        if (taskByData) {
                            console.log(`Found task by data attribute, removing...`);
                            taskByData.style.transition = 'all 0.5s ease-out';
                            taskByData.style.opacity = '0';
                            taskByData.style.transform = 'translateX(100%)';
                            taskByData.style.backgroundColor = '#fee2e2';
                            
                            setTimeout(() => {
                                taskByData.remove();
                                console.log(`✓ Task ${taskId} removed from webpage (via data attribute)`);
                            }, 500);
                            
                            return true;
                        }
                        
                        console.error(`Task element not found in DOM`);
                        
                        // Last resort: Refresh the entire task list
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
        // CHECK REMINDERS FUNCTION
        // ============================================
        async function checkReminders() {
            const now = new Date();
            const currentHour = String(now.getHours()).padStart(2, '0');
            const currentMinute = String(now.getMinutes()).padStart(2, '0');
            const currentTime = `${currentHour}:${currentMinute}`;
            
            console.log(`Checking reminders at ${currentTime}...`);
            
            // Get all task elements dynamically
            const taskElements = document.querySelectorAll('[data-task-time]');
            console.log(`Found ${taskElements.length} tasks to check`);
            
            for (const elem of taskElements) {
                const taskTime = elem.dataset.taskTime;
                const taskId = elem.dataset.taskId;
                const taskText = elem.querySelector('.card-title')?.textContent || 'Task';
                
                // Extract HH:MM from HH:MM:SS format
                const taskHourMin = taskTime.substring(0, 5);
                
                // Create unique key for this task alert
                const alertKey = `${taskId}-${taskTime}`;
                
                console.log(`Checking task ${taskId}: ${taskHourMin} vs ${currentTime}`);
                
                // Check if time matches and we haven't alerted yet
                if (taskHourMin === currentTime && !alertedTasks.has(alertKey)) {
                    console.log(`Time match for task: ${taskText}`);
                    
                    // Show notification
                    let notificationShown = false;
                    
                    if (Notification.permission === 'granted') {
                        new Notification('⏰ Task Reminder', {
                            body: taskText,
                            icon: '⏰'
                        });
                        notificationShown = true;
                    } else {
                        alert(`⏰ Reminder: ${taskText}`);
                        notificationShown = true;
                    }
                    
                    // Mark as alerted
                    alertedTasks.add(alertKey);
                    
                    // Save to localStorage
                    localStorage.setItem('alertedTasks', JSON.stringify({
                        date: today,
                        tasks: Array.from(alertedTasks)
                    }));
                    
                    // AUTO-DELETE AFTER NOTIFICATION
                    if (notificationShown && taskId) {
                        console.log(`Will delete task ${taskId} in 1 second...`);
                        
                        // Wait 1 second, then delete the task
                        setTimeout(async () => {
                            console.log(`Now deleting task ${taskId}...`);
                            const deleteSuccess = await deleteTask(taskId);
                            
                            if (deleteSuccess) {
                                console.log(`✅ Task "${taskText}" deleted successfully`);
                            } else {
                                console.log(`❌ Failed to delete task "${taskText}"`);
                            }
                        }, 1000);
                    }
                }
            }
        }
        
        // Request notification permission on load
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        
        // Check every 30 seconds
        setInterval(checkReminders, 30000);
        
        // Check immediately on load
        checkReminders();
        
        // Make functions available globally for testing
        window.deleteTask = deleteTask;
        window.checkReminders = checkReminders;
        window.refreshTaskList = refreshTaskList;
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
            P(f"⏰ {task['time']}"),
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