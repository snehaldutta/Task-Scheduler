# 📅 Task Scheduler 

A modern, responsive task scheduler web application built with FastHTML and Supabase that automatically alerts and deletes tasks at their scheduled time.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastHTML](https://img.shields.io/badge/FastHTML-0.12.25-green.svg)
![Supabase](https://img.shields.io/badge/Supabase-Database-orange.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-06B6D4.svg)
![DaisyUI](https://img.shields.io/badge/DaisyUI-4.12.10-5A67D8.svg)

## ✨ Features

- **⏰ Smart Alerts**: Visual and browser notifications at scheduled task times
- **🗑️ Auto-Delete**: Tasks automatically delete 3 seconds after alert
- **💾 Persistent Storage**: Tasks stored in Supabase database
- **🎨 Modern UI**: Beautiful interface with TailwindCSS and DaisyUI
- **📱 Responsive Design**: Works seamlessly on desktop and mobile
- **⚡ Real-time Updates**: Instant UI updates without page refresh
- **🔔 Dual Notification System**: Visual alerts + browser notifications
- **🎵 Audio Alerts**: Sound notification when tasks are due

## 🚀 Live Demo

The application is deployed and running on Vercel. Add tasks with specific times and watch them alert and auto-delete at the scheduled moment!

## 🛠️ Tech Stack

- **Backend**: FastHTML (Python web framework)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTMX for dynamic updates
- **Styling**: TailwindCSS + DaisyUI
- **Deployment**: Vercel
- **Real-time**: JavaScript for timer-based alerts

## 📋 Prerequisites

- Python 3.8 or higher
- Supabase account and project
- Node.js (for Vercel deployment)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/task-scheduler.git
cd task-scheduler
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 4. Set up Supabase Database

Create a table in your Supabase project:

```sql
CREATE TABLE "TodoTable" (
    id SERIAL PRIMARY KEY,
    task VARCHAR(255) NOT NULL,
    time TIME NOT NULL,
);
```

### 5. Run locally

```bash
python main.py
```

Visit `http://localhost:5001` in your browser.

## 🚢 Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Create `vercel.json` in your project root:
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel
```

4. Set environment variables in the Vercel dashboard:
   - Go to your project settings
   - Add `SUPABASE_URL` and `SUPABASE_KEY`

## 💡 How It Works

1. **Add Task**: Enter a task name and select a time
2. **Task Storage**: Task is saved to Supabase database
3. **Active Monitoring**: JavaScript checks every 10 seconds for due tasks
4. **Alert System**: When time matches:
   - Shows a visual alert at the top of the screen
   - Plays notification sound
   - Sends browser notification (if permitted)
5. **Auto-Deletion**: Task automatically deletes after 3 seconds

## 🎯 Key Features Explained

### Visual Alert System
- Always works, even when browser notifications are blocked
- Slide-down animation with warning styling
- Shows task name and countdown to deletion
- Can be manually dismissed

### Browser Notifications
- Optional enhancement (requires user permission)
- Works as a secondary notification method
- Non-intrusive fallback system

### Auto-Delete Mechanism
- Prevents task accumulation
- Visual feedback during deletion (fade-out animation)
- Database and UI sync automatically

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page with task scheduler |
| `/submit-task` | POST | Add new task to database |
| `/delete-task/{id}` | DELETE | Remove task from database |
| `/get-tasks` | GET | Fetch all tasks as HTML |

## 🐛 Troubleshooting

### Alerts not working in production?
- The app uses visual alerts as the primary method (always works)
- Browser notifications are an optional enhancement
- Check browser console for error messages

### Tasks not saving?
- Verify Supabase credentials in environment variables
- Check the Supabase dashboard for database connectivity
- Ensure TodoTable exists with the correct schema

### Form not resetting?
- Both input fields should clear after submission
- Check browser console for JavaScript errors

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Made with ❤️ by Snehal**

- GitHub: [@snehaldutta](https://snehaldutta.github.io/snehaldutta/)
- LinkedIn: [Snehal Dutta](www.linkedin.com/in/snehal-python)

## 🙏 Acknowledgments

- [FastHTML](https://github.com/AnswerDotAI/fasthtml) for the amazing Python web framework
- [Supabase](https://supabase.com) for the backend infrastructure
- [TailwindCSS](https://tailwindcss.com) and [DaisyUI](https://daisyui.com) for beautiful styling
- [HTMX](https://htmx.org) for seamless dynamic updates

## 📊 Project Status

🟢 **Deployed** - Up and running .....

---

⭐ If you find this project useful, please consider giving it a star!
