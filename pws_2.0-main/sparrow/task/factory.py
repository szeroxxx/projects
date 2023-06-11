import datetime

from django.contrib.contenttypes.models import ContentType

from base.factory.factory_data import FactoryDemoData
from task.models import Task, TaskType


class TaskFactory(object):
    @staticmethod
    def create_task():
        task_data = FactoryDemoData.TASKS
        for data in task_data:
            task_type = TaskType.objects.filter(code=data["task_type"]).values("id").first()
            task = Task.objects.filter(name=data["name"], task_type_id=task_type["id"]).first()
            if task is None:
                contenttype = ContentType.objects.filter(model=data["content_type_model"]).values("id").first()
                task = Task.objects.create(
                    name=data["name"], created_on=data["created_on"], status=data["status"], content_type_id=contenttype["id"], created_by_id=data["created_by_id"]
                )
                task.task_type_id = task_type["id"]
                task.assign_to_id = data["created_by_id"]
                task.due_date = data["created_on"] + datetime.timedelta(days=1)
                task.priority = data["priority"]
                task.save()
