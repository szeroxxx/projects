from django.apps import apps
from attachment import views as attachment_views
from attachment.models import FileType

es = ""


class Attachment:
    @staticmethod
    def create_attachment_index(index_name):
        analysis = {
            "filter": {"english_stop": {"type": "stop", "stopwords": "_english_"}},
            "char_filter": {"undescore_replace": {"type": "pattern_replace", "pattern": "_", "replacement": " "}},
            "analyzer": {
                "keylower": {"type": "custom", "tokenizer": "keyword", "filter": ["lowercase"]},
                "english": {"type": "custom", "char_filter": ["undescore_replace"], "tokenizer": "whitespace", "filter": ["asciifolding", "lowercase", "english_stop"]},
                # "my_search_analyser": {
                #     "type": "custom",
                #     "char_filter": ["undescore_replace"],
                #     "tokenizer": "whitespace",
                #     "filter": ["asciifolding", "lowercase", "english_stop"],
                # }
            },
        }

        mappings = {
            "properties": {
                "app_name": {"type": "text"},
                "model_name": {"type": "text"},
                "name": {"type": "text", "analyzer": "english"},
                "title": {"type": "text", "analyzer": "english"},
                "subject": {"type": "text", "analyzer": "english"},
                "description": {"type": "text", "analyzer": "english"},
                "source_doc": {"type": "text", "analyzer": "english"},
                "user_id": {"type": "integer"},
                "size": {"type": "integer"},
                "uid": {"type": "text"},
                "entity_id": {"type": "integer"},
                "created_on": {"type": "date"},
                "attachment_id": {"type": "integer"},
                "tags": {"type": "nested", "properties": {"id": {"type": "integer"}}},
                "is_public": {"type": "boolean"},
            }
        }

        create_index_body = {
            "settings": {"analysis": analysis},
            "mappings": mappings,
        }

        es.indices.create(index=index_name, body=create_index_body)

    def insert(self, attachments, **kwargs):

        if es == "":
            return
        if not es.indices.exists(index="public" + "-attachment"):
            Attachment.create_attachment_index("public" + "-attachment")

        docs = []

        tag_model_name = kwargs["app_name"] + "AttachmentTag"
        model_exist = False
        try:
            apps.get_model(kwargs["app_name"], tag_model_name)
            model_exist = True
        except LookupError:
            model_exist = False

        for attachment in attachments:
            tags = []
            if model_exist:
                model = apps.get_model(kwargs["app_name"], tag_model_name)
                doc_tags = model.objects.filter(attachment_id=attachment.id)
                for doc_tag in doc_tags:
                    tags.append({"id": doc_tag.tag_id})
            doc = {
                "attachment_id": attachment.id,
                "app_name": kwargs["app_name"],
                "model_name": kwargs["model_name"],
                "name": attachment.name,
                "user_id": attachment.user_id,
                "entity_id": attachment.object_id,
                "size": attachment.size,
                "source_doc": attachment.source_doc,
                "uid": attachment.uid,
                "created_on": attachment.create_date,
                "title": attachment.title,
                "file_type_id": attachment.file_type_id,
                "subject": attachment.subject,
                "description": attachment.description,
                "tags": tags,
                "is_public": attachment.is_public,
            }

            doc_data = {
                "_index": "public" + "-attachment",
                "_id": kwargs["model_name"] + "_" + str(attachment.id),
                "_source": doc,
            }
            docs.append(doc_data)

    def delete_attachment(self, id, **kwargs):
        if es == "":
            return
        exists = es.exists(index="public" + "-attachment", id=kwargs["model_name"] + "_" + str(id))
        if exists:
            es.delete(index="public" + "-attachment", id=kwargs["model_name"] + "_" + str(id))

    def update_attachment(self, **kwargs):
        if es == "":
            return
        update_statement = ""
        # tag_update_statement = ""
        tags = False
        if "title" in kwargs:
            tags = False
            update_statement += "ctx._source.title='" + kwargs["title"] + "';"
        if "subject" in kwargs:
            update_statement += "ctx._source.subject='" + kwargs["subject"] + "';"
        if "description" in kwargs:
            tags = False
            update_statement += "ctx._source.description='" + kwargs["description"] + "';"
        if "app_name" in kwargs:
            tags = False
            update_statement += "ctx._source.app_name='" + kwargs["app_name"] + "';"
        if "updated_model_name" in kwargs:
            tags = False
            update_statement += "ctx._source.model_name='" + kwargs["updated_model_name"] + "';"
        if "entity_id" in kwargs:
            tags = False
            update_statement += "ctx._source.entity_id='" + str(kwargs["entity_id"]) + "';"
        if "tags" in kwargs:
            tags = True
            tag_list = kwargs["tags"]
            update_statement = tag_list
        if tags:
            query = {
                "query": {"bool": {"must": {"match": {"_id": kwargs["model_name"] + "_" + str(kwargs["attachment_id"])}}}},
                "script": {"source": "ctx._source.tags= params.mifieldAsParam", "params": {"mifieldAsParam": update_statement}},
            }
        else:
            query = {
                "query": {"bool": {"must": {"match": {"_id": kwargs["model_name"] + "_" + str(kwargs["attachment_id"])}}}},
                "script": {"inline": "" + update_statement + ""},
            }

        es.indices.refresh("public" + "-attachment")
        es.update_by_query(index="public" + "-attachment", body=query, wait_for_completion=False)

    def get_es_attachments(self, page_start, page_size, search_data, entity_id, type):
        if not es.indices.exists(index="public" + "-attachment"):
            Attachment.create_attachment_index("public" + "-attachment")
        if search_data and type == "doc":
            response = es.search(
                index="public" + "-attachment",
                body={
                    "from": page_start,
                    "size": page_size,
                    "sort": [{"created_on": {"order": "desc"}}],
                    "query": {"query_string": {"fields": ["name", "source_doc", "title", "description", "subject"], "query": "" + search_data + "*"}},
                },
            )
        elif search_data and type == "tag":
            response = es.search(
                index="public" + "-attachment",
                body={"query": {"nested": {"path": "tags", "query": {"bool": {"must": {"terms": {"tags.id": search_data}}}}}}},
            )
        elif entity_id:
            response = es.search(
                index="public" + "-attachment",
                body={
                    "from": page_start,
                    "size": page_size,
                    "sort": [{"created_on": {"order": "desc"}}],
                    "query": {"bool": {"must": {"match": {"entity_id": {"query": entity_id}}}}},
                },
            )
        else:
            response = es.search(
                index="public" + "-attachment",
                body={"from": page_start, "size": page_size, "sort": [{"created_on": {"order": "desc"}}], "query": {"bool": {"must": {"match_all": {}}}}},
            )
        return response

    def get_attachments(self, page_start, page_size, search_data, entity_id, type, app, model):
        if es == "":
            return self.get_rdb_attachments(page_start, page_size, search_data, entity_id, type, app, model)
        return self.get_es_attachments(page_start, page_size, search_data, entity_id, type)

    def get_rdb_attachments(self, page_start, page_size, search_data, object_id, type, app_name, model_name):
        model = apps.get_model(app_name, model_name)
        attachments = model.objects.filter(object_id=object_id, deleted=False).order_by("id")
        file_types = list(FileType.objects.all().values("id", "name"))
        response = {"hits": {"hits": [], "total": {}}}
        response["file_types"] = file_types
        for attachment in attachments:
            attachment_res = attachment_views.get_attchment_object(attachment)
            attachment_res["app_name"] = app_name
            attachment_res["model_name"] = model_name
            response["hits"]["hits"].append({"_id": app_name + "_" + model_name + "_" + str(attachment_res["attachment_id"]), "_source": attachment_res})
        response["hits"]["total"]["value"] = attachments.count()
        return response
