tools = [
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Creates a new reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the reminder"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the reminder"
                    },
                    "reminder_time": {
                        "type": "string",
                        "description": "Time for the reminder in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                    },
                    "recurring_interval": {
                        "type": "integer",
                        "description": "Interval for recurring reminders in minutes, if applicable",
                        "minimum": 1
                    },
                    "urgency": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Urgency level of the reminder (1 to 5)"
                    }
                },
                "required": ["title", "description", "reminder_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_reminder",
            "description": "Edits an existing reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "ID of the reminder to edit"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title of the reminder"
                    },
                    "description": {
                        "type": "string",
                        "description": "New detailed description of the reminder"
                    },
                    "reminder_time": {
                        "type": "string",
                        "description": "New time for the reminder in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                    },
                    "recurring_interval": {
                        "type": "integer",
                        "description": "New interval for recurring reminders in minutes, if applicable",
                        "minimum": 1
                    },
                    "urgency": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "New urgency level of the reminder (1 to 5)"
                    }
                },
                "required": ["reminder_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_reminder",
            "description": "Deletes an existing reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "ID of the reminder to delete"
                    }
                },
                "required": ["reminder_id"]
            }
        }
    }
]