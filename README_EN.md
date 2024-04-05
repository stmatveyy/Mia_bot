# Mia bot 
### — Asyncrounos Telegram chat-bot built to help RUDN students in the everyday life.
>[!IMPORTANT]
>Bot is in a development, is inaccessable for now :(
#### Funcionality:

- 🔔 Notifications about deadlines, important info, etc. 
- ❕  Reminders (private & to whole group)
- 🗒️ Notes
- 🤓 GPT mode
- ✔️ Separate head of the group functionality
   
### Access rights:
|                  |     **Head of the group**     |      **Students**      |
|------------------|:-----------------------------:|:----------------------:|
| Schedule         |            Editing            |         Viewing        |
| Notifications    |            Editing            | Editing (private only) |
| Notes            |          Private only         |      Private only      |
| _Important info_ |           _Editing_           |        _Viewing_       |
| _Group editing_  | _Adding & excluding students_ |         _None_         |

>[!NOTE]
>Functionality in italic will be added in future releases

## Stack:
- Python 3.2
  - aiogram
  - apscheduler
  - g4f
  - asyncio
  - asyncpg
  - datetime
- PostgreSQL
