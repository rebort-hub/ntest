from datetime import datetime

from fastapi import Request, Depends

from ...models.manage.model_factory import Todo
from ...schemas.manage import todo as schema
from app.schemas.enums import TodoListEnum


async def get_todo_list(request: Request):
    query_list = await Todo.filter().order_by("num").all().values(
        "id", "title", "status", "create_user", "create_time", "done_user", "done_time")
    return request.app.get_success(query_list)


async def change_todo_sort(request: Request, form: schema.ChangeSortForm):
    await Todo.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def change_todo_status(request: Request, form: schema.ChangeStatusForm):
    done_user = done_time = None
    if form.status == TodoListEnum.DONE:
        done_user, done_time = request.state.user.id, datetime.now()
    await Todo.filter(id=form.id).update(status=form.status, done_user=done_user, done_time=done_time)
    return request.app.put_success()


async def get_todo(request: Request, form: schema.GetTodoForm = Depends()):
    data = await Todo.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data)


async def add_todo(request: Request, form: schema.AddTodoForm):
    data_list, max_num = [], await Todo.get_max_num()
    for index, item in enumerate(form.data_list):
        if not item.title or not item.detail:
            ValueError(f"第 {index} 行，请完善数据")
        data_list.append({"title": item.title, "detail": item.detail, "num": max_num + index + 1})
    await Todo.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_todo(request: Request, form: schema.ChangeTodoForm):
    await Todo.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_todo(request: Request, form: schema.GetTodoForm):
    await Todo.filter(id=form.id).delete()
    return request.app.delete_success()
