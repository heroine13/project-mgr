"""
CRUD operations package
"""
from app.crud import gantt, project, issue, resource, document, comment, task, user, user_mgmt, i18n, search

crud_gantt = gantt
crud_project = project
crud_issue = issue
crud_resource = resource
crud_document = document
crud_comment = comment
crud_task = task
crud_user = user
crud_user_mgmt = user_mgmt
crud_i18n = i18n
crud_search = search