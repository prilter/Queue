group_name = "БСБО-51-25"
updated_rules_date = "27.11.25"
commands_list      = f"/start 🚀: запуск бота\n/src 🔓:     репозиторий бота(open source)\n"
contributers       = ", ".join(["Богатырев"])
src_rep            = "https://github.com/prilter/queue" 
rules              = f"""Все правила соответствуют договоренностям с {updated_rules_date}


Правило 1:
    Запуск очереди происходит за 3 часа до начала занятия
    
Правило 2:
    Занять очередь можно только для 1 выступления на предмет, то есть каждый пользователь может быть записан в очередь только до 1 раза, пока это значение не изменится

Правило 3:
    Если очередь не заканчивается, то она просто переносится на следующий раз"""

history_not = "🔔 Напоминание про историю!\n\nПроверь очередь: /queue история"
org_not     = "🔔 Напоминание про ОРГ!    \n\nПроверь очередь: /queue орг"
limit_mes   = "Простите, но вы превысили лимит в 3 записи. Ознакомьтесь с правилами(/rules)"
locked_auth = "❌Очередь закрыта!"

no_sub   = "Вы не выбрали предмет"
no_queue = "Очереди нет!"

# LOGS
adding_user_log         = "User was added to"
adding_user_err_log     = "Cannot add user to"
sending_mes_log         = "Sended message to user"
sending_mes_err_log     = "Cannot send message"
entries_limit_log       = "User tried to join to queue more than 1 time"
time_limit_log          = "User tried to join before opening queue"
del_user_from_queue_log = "User was deleted from queue cause he is done his presentation"
check_queue_log         = "User checked queue"
superuser_operation_log = "changed all parameters"

# REPLY BUTTONS
help_button_text    = "❓Хелп меню"
rules_button_text   = "📜Правила очереди"
choose_subject_text = "📚Выбрать предмет"
check_button_text   = "📜Проверить очередь"
join_button_text    = "➕Присоедениться к очереди"
done_button_text    = "☑️Выход из очереди"
