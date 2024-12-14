# agnia-smart-digest

Agnia Smart Digest is a smart assistant that can help you with your daily tasks.
It can fetch emails, summarize emails, send emails, schedule reminders, fetch weather, travel time estimation, news monitoring, moodle deadlines, search emails, and more.

## Capabilities

### Weather Forecast
Request:
```markdown
Hello, that is the weather for today?
```
Response:
```markdown
1 : Fetched today's weather ✅
🌆 Morning - ☀️ 22°C
🏙️ Afternoon - ☀️ 24°C
🌃 Evening - ☀️ 23°C

Plan status - Completed successfully : Done
```

### Email Fetching
Request:
```markdown
What are my the most recent 2 emails?
```
Response:
```markdown
1 : Extracted number of emails: 2 ✅

2 : Extracted 2 emails ✅

3 : Preprocessed 2 emails ✅

4 : Ranked technical emails ✅:
📧 "Apple Importance Notification"
📧 Accepted: Test Booking

5 : Summarized 2 emails ✅
✉️ «"Apple Importance Notification"» Sun, 07 Jul 2024 02:04:55 +0300
Apple is important

✉️ «Accepted: Test Booking» Sun, 07 Jul 2024 00:48:25 +0300
 Your request was accepted.



Plan status - Completed successfully : Done
```

### Email Search
```markdown
Find emails related to food
```

Response:
```markdown
1 : Extracted query from request ✅
🔎 emails related to food

2 : Extracted number of emails: 3 ✅

3 : Extracted 3 emails ✅

4 : Find 3 emails ✅

5 : Summarized 3 emails ✅
✉️ «Saturdays Dinner Invitation» Sun, 07 Jul 2024 03:09:31 +0300
send email to a.kudryavtsev@innopolis.university about Saturdays dinner

✉️ «Meeting Request with Anton» Sun, 07 Jul 2024 03:04:11 +0300
I would like to schedule a meeting with you to discuss the upcoming project. Hello, I hope this email finds you well. Please let me know a convenient time for you. Best regards, Anton

✉️ «"Apple Importance Notification"» Sun, 07 Jul 2024 02:04:55 +0300
Apple is important



Plan status - Completed successfully : Done
```

### Email Sending
Request:
```markdown
send email to a.kudryavtsev@innopolis.university saying "Hello,

I hope this email finds you well. I would like to schedule a meeting with you to discuss the upcoming project. Please let me know a convenient time for you.

Thank you.

Best regards,
Anton"
```
Response:
```markdown
1 : Extracted receiver from request ✅
👤 a.kudryavtsev@innopolis.university

2 : Extracted text from request ✅
Hello,

I hope this email finds you well. I would like to schedule a meeting with you to discuss the upcoming project. Please let me know a convenient time for you.

Thank you.

Best regards,
Anton
3 : Extracted subject from request ✅
📬 Meeting Request with Anton

4 : Email sent successfully! ✅

Plan status - Completed successfully : Done
```

### TeamFlame Tasks
Request:
```markdown
Whats my current tasks at work?
```
Response:
```markdown
1 : Extracted 4 tasks ✅
📝 «Example»: Описание моей задачи
📝 «Win Agnia Challenge»
📝 «Second task»
📝 «Test Task»


Plan status - Completed successfully : Done
```

### News Monitoring
Request:
```markdown
Tell me more than one news article and but less then eight divide by two news articles
```
Response:
```markdown
1 : Extracted number of acrticles: 3 ✅

2 : Fetched 3 articles ✅
📰 «Выглядит очень многообещающе»: скриншоты и детали киберпанк-экшена Replaced — Игры на DTF - DTF
📰 Нагельсманн высказался после вылета Германии с Евро-2024 - Евро-Футбол.Ру
📰 Что говорят об инициативе властей переснять киноклассику - 5 июля 2024 - Фонтанка.Ру


Plan status - Completed successfully : Done
```

### Moodle Deadlines
Request:
```markdown
What are my deadlines at moodle?
```
Response:
```markdown
1 : Fetched 2 deadlines from Moodle ✅
🎯 [Sum24] Deep Learning for Search / Глубокое обучение для задач поиска:
• «Lab 3: Ranking Metrics  (5 points total)» is due 23:59 on Sunday, 7 July 2024

🎯 [Sum24] Deep Learning for Search / Глубокое обучение для задач поиска:
• «Home Assignment 3: System Design (5 points total)» is due 23:59 on Wednesday, 10 July 2024


Plan status - Completed successfully : Done
```



### Reminders
Request Examples:
```markdown
Remind about the presentation today at 10 AM
```
```markdown
Remind me about apples in 5 minutes
```
```markdown
Remind about plain on 28 august 2024 at 10 AM
```

Request:
```markdown
Remind about sleep in 30 seconds
```

Response:
```markdown
1 : Extracted reminder timedelta ✅
⏰ Will remind in 29.66 seconds

2 : Generated reminder text ✅
Reminder: "sleep". Get some rest, you need it!
3 : Scheduled reminder ✅
📅 Sun Jul  7 03:07:43 2024

Plan status - Completed successfully : Done
```

### Travel Time Estimation
Request:
```markdown
How much time to arrive would take from Stuttgart to Karlsruhe?
```
Response:
```markdown
1 : Calculated time ✅
⏰ Travel time: 61 minutes
🗺️ Distance: 79 km


Plan status - Completed successfully : Done
```



## Actions JSON
```json
[{"system_name": "General", "action_name": "extract_format_action", "description": "ExtractFormatAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_format": {"type": "string", "description": "Extracted Format", "required": true}}}, {"system_name": "General", "action_name": "extract_platforms_action", "description": "ExtractPlatformsAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_platforms": {"items": {"type": "string"}, "type": "array", "description": "Extracted Platforms", "required": true}}}, {"system_name": "General", "action_name": "extract_email_number_action", "description": "ExtractEmailNumberAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_email_number": {"type": "integer", "description": "Extracted Email Number", "required": true}}}, {"system_name": "General", "action_name": "extract_acticle_number_action", "description": "ExtractArticleNumberAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_article_number": {"type": "integer", "description": "Extracted Article Number", "required": true}}}, {"system_name": "General", "action_name": "extract_email_receiver_action", "description": "ExtractEmailReceiverAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_receiver": {"type": "string", "description": "Extracted Receiver", "required": true}}}, {"system_name": "General", "action_name": "extract_email_subject_action", "description": "ExtractEmailSubjectAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_subject": {"type": "string", "description": "Extracted Subject", "required": true}}}, {"system_name": "General", "action_name": "extract_email_text_action", "description": "ExtractEmailTextAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_text": {"type": "string", "description": "Extracted Text", "required": true}}}, {"system_name": "General", "action_name": "generate_reminder_text_action", "description": "GenerateReminderTextAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"reminder_text": {"type": "string", "description": "Reminder Text", "required": true}}}, {"system_name": "General", "action_name": "extract_reminder_datetime_action", "description": "ExtractReminderDatetimeAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"reminder_datetime": {"type": "string", "description": "Reminder Datetime", "required": true}}}, {"system_name": "General", "action_name": "extract_search_query_action", "description": "ExtractSearchQueryAction", "input_parameters": {"user_request": {"type": "string", "description": "User Request", "required": true}}, "output_parameters": {"extracted_query": {"type": "string", "description": "Extracted Query", "required": true}}}, {"system_name": "General", "action_name": "weather_action", "description": "WeatherAction", "input_parameters": {"city": {"type": "string", "description": "City", "required": true}}, "output_parameters": {"morning_temperature": {"type": "integer", "description": "Morning Temperature", "required": true}, "morning_icon": {"type": "string", "description": "Morning Icon", "required": true}, "afternoon_temperature": {"type": "integer", "description": "Afternoon Temperature", "required": true}, "afternoon_icon": {"type": "string", "description": "Afternoon Icon", "required": true}, "evening_temperature": {"type": "integer", "description": "Evening Temperature", "required": true}, "evening_icon": {"type": "string", "description": "Evening Icon", "required": true}}}, {"system_name": "General", "action_name": "list_emails_action", "description": "EmailsAction", "input_parameters": {"outlook_email": {"type": "string", "description": "Outlook Email", "required": true}, "outlook_password": {"type": "string", "description": "Outlook Password", "required": true}, "last_n_emails": {"type": "integer", "description": "Last N Emails", "required": true}}, "output_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}}, {"system_name": "General", "action_name": "list_teamflake_tasks_action", "description": "TeamflameAcrion", "input_parameters": {"teamflame_email": {"type": "string", "description": "Teamflame Email", "required": true}, "teamflame_password": {"type": "string", "description": "Teamflame Password", "required": true}}, "output_parameters": {"teamflame_tasks": {"items": {"type": "string"}, "type": "array", "description": "Teamflame Tasks", "required": true}}}, {"system_name": "General", "action_name": "clean_emails_action", "description": "EmailsAction", "input_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}, "output_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}}, {"system_name": "General", "action_name": "summarize_emails_action", "description": "EmailsAction", "input_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}, "output_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}}, {"system_name": "General", "action_name": "travel_time_action", "description": "TravelTimeAction", "input_parameters": {"travel_source": {"type": "string", "description": "Travel Source", "required": true}, "travel_destination": {"type": "string", "description": "Travel Destination", "required": true}, "api_key": {"type": "string", "description": "Api Key", "required": true}}, "output_parameters": {"travel_time": {"type": "integer", "description": "Travel Time", "required": true}, "distance": {"type": "integer", "description": "Distance", "required": true}}}, {"system_name": "General", "action_name": "news_action", "description": "NewsAction", "input_parameters": {"n_articles": {"type": "integer", "description": "N Articles", "required": true}, "news_api_key": {"type": "string", "description": "News Api Key", "required": true}}, "output_parameters": {"articles": {"items": {"type": "string"}, "type": "array", "description": "Articles", "required": true}}}, {"system_name": "General", "action_name": "moodle_action", "description": "EmailsAction", "input_parameters": {"moodle_email": {"type": "string", "description": "Moodle Email", "required": true}, "moodle_password": {"type": "string", "description": "Moodle Password", "required": true}}, "output_parameters": {"deadlines": {"items": {"type": "string"}, "type": "array", "description": "Deadlines", "required": true}}}, {"system_name": "General", "action_name": "send_email_action", "description": "SendEmailAction", "input_parameters": {"outlook_email": {"type": "string", "description": "Outlook Email", "required": true}, "outlook_password": {"type": "string", "description": "Outlook Password", "required": true}, "email_receiver": {"type": "string", "description": "Email Receiver", "required": true}, "email_subject": {"type": "string", "description": "Email Subject", "required": true}, "email_content": {"type": "string", "description": "Email Content", "required": true}}, "output_parameters": {"status": {"type": "string", "description": "Status", "required": true}}}, {"system_name": "General", "action_name": "schedule_reminder_action", "description": "ScheduleReminderAction", "input_parameters": {"reminder_text": {"type": "string", "description": "Reminder Text", "required": true}, "reminder_datetime": {"type": "string", "description": "Reminder Datetime", "required": true}, "telegram_user_id": {"type": "integer", "description": "Telegram User Id", "required": true}}, "output_parameters": {"reminder_datetime": {"type": "string", "description": "Reminder Datetime", "required": true}}}, {"system_name": "General", "action_name": "ranking_emails_action", "description": "RankingEmailsAction", "input_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}, "output_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}}, {"system_name": "General", "action_name": "search_emails_action", "description": "SearchEmailsAction", "input_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}, "query_texts": {"type": "string", "description": "Query Texts", "required": true}, "n_results": {"type": "integer", "description": "N Results", "required": true}}, "output_parameters": {"emails": {"items": {"type": "string"}, "type": "array", "description": "Emails", "required": true}}}]
```

## Plans JSON
```json
[{"id":"5ba7c92d-f85f-49ca-9d3f-72c3d909231a","description":"tasks, cards, board, kanban, teamflame, todo, work","initial_data":{"teamflame_email":"antonkudryavtsevdoem@gmail.com","teamflame_password":"vazTdCjnL85Bm4z"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"teamflame_email":"initial_data[teamflame_email]","teamflame_password":"initial_data[teamflame_password]"},"action_name":"list_teamflake_tasks_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.289274"},{"id":"bdfaa2ec-138a-46c3-ac84-08e97a4207fb","description":"moodle, deadline, assignment, task, due, submission, course, homework","initial_data":{"moodle_email":"a.kudryavtsev@innopolis.university","moodle_password":"sepnud-9taqry-nupzuT"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"moodle_email":"initial_data[moodle_email]","moodle_password":"initial_data[moodle_password]"},"action_name":"moodle_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.352626"},{"id":"19da4561-ee05-4d15-ac7a-d7958db9f805","description":"weather, sunny, temperature, humidity, rain, cloud, wear, clother","initial_data":{"city":"Innopolis"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"city":"initial_data[city]"},"action_name":"weather_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.246838"},{"id":"bc6f1d21-3496-430a-bf81-244620afebc2","description":"route, travel, distance, time, latency, map, gps, arrive","initial_data":{"api_key":"873b398257ee8ef980f1d65094d0789e","travel_source":"Stuttgart","travel_destination":"Karlsruhe"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"api_key":"initial_data[api_key]","travel_source":"initial_data[travel_source]","travel_destination":"initial_data[travel_destination]"},"action_name":"travel_time_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.309510"},{"id":"19460cb8-6da6-4047-9df4-139c803daeab","description":"send, email, sent, contact, message, text, @","initial_data":{"user_request":"","outlook_email":"a.kudryavtsev@innopolis.university","outlook_password":"sepnud-9taqry-nupzuT"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_email_receiver_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"2":{"system":"General","action_id":2,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_email_text_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"3":{"system":"General","action_id":3,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_email_subject_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"4":{"system":"General","action_id":4,"depends_on":[1,2,3],"input_data":{"email_content":"actions[2][extracted_text]","email_subject":"actions[3][extracted_subject]","outlook_email":"initial_data[outlook_email]","email_receiver":"actions[1][extracted_receiver]","outlook_password":"initial_data[outlook_password]"},"action_name":"send_email_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.373717"},{"id":"fedca56b-eb8c-4a32-a007-c6543bb7daf9","description":"get, emails, list, fetch, inbox, contacts","initial_data":{"user_request":"","outlook_email":"a.kudryavtsev@innopolis.university","outlook_password":"sepnud-9taqry-nupzuT"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_email_number_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"2":{"system":"General","action_id":2,"depends_on":[1],"input_data":{"last_n_emails":"actions[1][extracted_email_number]","outlook_email":"initial_data[outlook_email]","outlook_password":"initial_data[outlook_password]"},"action_name":"list_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"3":{"system":"General","action_id":3,"depends_on":[2],"input_data":{"emails":"actions[2][emails]"},"action_name":"clean_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"4":{"system":"General","action_id":4,"depends_on":[3],"input_data":{"emails":"actions[3][emails]"},"action_name":"ranking_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"5":{"system":"General","action_id":5,"depends_on":[4],"input_data":{"emails":"actions[4][emails]"},"action_name":"summarize_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.267624"},{"id":"c400de9c-7cb6-4c3e-9639-c088227092ac","description":"news, articles, newspaper, headline, world, happning, info","initial_data":{"news_api_key":"4fcd28abd84b4fd286ec5b395b2ccb24","user_request":""},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_acticle_number_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"2":{"system":"General","action_id":2,"depends_on":[1],"input_data":{"n_articles":"actions[1][extracted_article_number]","news_api_key":"initial_data[news_api_key]"},"action_name":"news_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.332080"},{"id":"3f0f6b6f-3cf6-486d-a8fc-03317cf10ece","description":"remind, reminder, schedule, note, postpone, calendar, event, deadline, time, date","initial_data":{"user_request":"","telegram_user_id":675635828,"reminder_datetime":"0001-01-01T00:00:00"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_reminder_datetime_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"2":{"system":"General","action_id":2,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"generate_reminder_text_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"3":{"system":"General","action_id":3,"depends_on":[1,2],"input_data":{"reminder_text":"actions[2][reminder_text]","telegram_user_id":"initial_data[telegram_user_id]","reminder_datetime":"actions[1][reminder_datetime]"},"action_name":"schedule_reminder_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.393666"},{"id":"ab0e0819-c664-4da2-8033-e065d6d2eb7d","description":"search, find, email, retrieve, get, extract, topic, related to, about","initial_data":{"n_results":5,"user_request":"","outlook_email":"a.kudryavtsev@innopolis.university","outlook_password":"sepnud-9taqry-nupzuT"},"actions":{"1":{"system":"General","action_id":1,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_search_query_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"2":{"system":"General","action_id":2,"depends_on":[],"input_data":{"user_request":"initial_data[user_request]"},"action_name":"extract_email_number_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"3":{"system":"General","action_id":3,"depends_on":[2],"input_data":{"last_n_emails":"actions[2][extracted_email_number]","outlook_email":"initial_data[outlook_email]","outlook_password":"initial_data[outlook_password]"},"action_name":"list_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"4":{"system":"General","action_id":4,"depends_on":[1,2,3],"input_data":{"emails":"actions[3][emails]","n_results":"initial_data[n_results]","query_texts":"actions[1][extracted_query]"},"action_name":"search_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true},"5":{"system":"General","action_id":5,"depends_on":[4],"input_data":{"emails":"actions[4][emails]"},"action_name":"summarize_emails_action","action_type":"TeamAction","requires_confirmation":false,"requires_visualization":true}},"created_at":"2024-07-07T00:16:13.414433"}]
```
