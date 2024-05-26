from pyrogram import Client, filters
import sqlite3
from datetime import datetime

api_id =   ""
api_hash = ""  
bot_token = "" 

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
              (id INTEGER PRIMARY KEY, user_id INTEGER, task TEXT, due_date TEXT, completed INTEGER)''')

conn.commit()
conn.close()

def add_task(user_id, task, due_date):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, task, due_date, completed) VALUES (?, ?, ?, ?)", 
                   (user_id, task, due_date, 0))
    conn.commit()
    conn.close()

def get_tasks(user_id, completed=False):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, due_date FROM tasks WHERE user_id=? AND completed=?", (user_id, completed))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def complete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("أهلاً بك في بوت إدارة المهام! استخدم /howtouse لمعرفة كيفية استخدام البوت.")

@app.on_message(filters.command("howtouse"))
async def how_to_use(client, message):
    commands = (
        "/addtask <المهمة> <التاريخ> - إضافة مهمة جديدة\n"
        "  مثال: /addtask كتابة تقرير الاجتماع 2024-06-01\n"
        "/viewtasks - عرض المهام الحالية\n"
        "  مثال: /viewtasks\n"
        "/completetask <رقم المهمة> - وضع علامة على مهمة كمنجزة\n"
        "  مثال: /completetask 1\n"
        "/completedtasks - عرض المهام المنجزة\n"
        "  مثال: /completedtasks\n"
    )
    await message.reply(commands)

@app.on_message(filters.command("addtask"))
async def add_task_command(client, message):
    try:
        task_details = message.text.split(maxsplit=2)[1:]
        task, due_date = task_details[0], task_details[1]
        user_id = message.from_user.id
        add_task(user_id, task, due_date)
        await message.reply(f"تمت إضافة المهمة: {task} بتاريخ {due_date}")
    except Exception as e:
        await message.reply("حدث خطأ أثناء إضافة المهمة. تأكد من تنسيق الأمر الصحيح: /addtask <مهمة> <تاريخ>")

@app.on_message(filters.command("viewtasks"))
async def view_tasks_command(client, message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id)
    if tasks:
        tasks_list = "\n".join([f"{task[0]}: {task[1]} - {task[2]}" for task in tasks])
        await message.reply(f"مهامك الحالية:\n{tasks_list}")
    else:
        await message.reply("لا توجد مهام حالياً.")

@app.on_message(filters.command("completetask"))
async def complete_task_command(client, message):
    try:
        task_id = int(message.text.split()[1])
        complete_task(task_id)
        await message.reply(f"تم وضع علامة على المهمة رقم {task_id} كمنجزة.")
    except Exception as e:
        await message.reply("حدث خطأ أثناء وضع علامة على المهمة. تأكد من تنسيق الأمر الصحيح: /completetask <رقم المهمة>")

@app.on_message(filters.command("completedtasks"))
async def completed_tasks_command(client, message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id, completed=True)
    if tasks:
        tasks_list = "\n".join([f"{task[0]}: {task[1]} - {task[2]}" for task in tasks])
        await message.reply(f"مهامك المنجزة:\n{tasks_list}")
    else:
        await message.reply("لا توجد مهام منجزة حالياً.")

app.run()
