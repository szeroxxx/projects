doc_type = (
    ("general","General"),
    ("invoice","Invoice"),
    ("order","Order"),
)

user_type = (
    (1,"Internal"),
    (2,"Customer"),
)

task_status = (
    ("not_started", "Not started"),
    ("in_progress", "In progress"),    
    ("completed", "Completed"),
)

task_priority = (
    ("low", "Low"),
    ("medium", "Medium"),    
    ("high", "High"),
    ("urgent", "Urgent")
)

remark_type = (
    ("normal", "Normal"),
    ("rejection", "Rejection"),
)

notification_type = (
    ("comment_mension", "Mension in comment"),
)

event_group = (
    ("others", "Others"),
)

event_action = (
    ("remark", "Remark"),
)

app_label = (
    ('user', 'User'),
)

mail_type = (
    ("po_quote_reminder", "Purchase order quotation"),
)