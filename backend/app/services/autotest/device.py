import httpx
from fastapi import Request, Depends

from ...models.autotest.model_factory import AppRunServer as Server, AppRunPhone as Phone
from ...schemas.autotest import device as schema
from ...routers.base_view import APIRouter

module_router = APIRouter()


async def get_server_list(request: Request, form: schema.GetServerListForm = Depends()):
    get_filed = ["id", "name",  "status"]
    if form.detail:
        get_filed.extend(["os", "ip", "port", "appium_version"])
    query_data = await form.make_pagination(Server, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_server_sort(request: Request, form: schema.ChangeSortForm):
    await Server.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_server(request: Request, form: schema.GetServerForm):
    server = await Server.validate_is_exist("服务器不存在", id=form.id)
    new_server = await server.copy()
    return request.app.success("复制成功", data=new_server)


async def run_server(request: Request, form: schema.GetServerForm):
    server = await Server.validate_is_exist("服务器不存在", id=form.id)
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(f'http://{server.ip}:{server.port}', timeout=5)
            status_code = response.status_code
    except Exception as error:
        await server.request_fail()
        return request.app.fail(msg="设置的appium服务器地址不能访问，请检查")
    if status_code > 499:  # 5开头的
        await server.request_fail()
        return request.app.fail(msg=f'设置的appium服务器地址响应状态码为 {status_code}，请检查')
    await server.request_success()
    return request.app.success(msg=f'服务器访问成功，响应为：状态码为 {status_code}')


async def get_server_detail(request: Request, form: schema.GetServerForm = Depends()):
    server = await Server.validate_is_exist("服务器不存在", id=form.id)
    return request.app.get_success(server)


async def add_server(request: Request, form: schema.AddServerForm):
    await Server.batch_insert([data.dict() for data in form.data_list], request.state.user)
    return request.app.post_success()


async def change_server(request: Request, form: schema.EditServerForm):
    await Server.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_server(request: Request, form: schema.GetServerForm):
    await Server.filter(id=form.id).delete()
    return request.app.delete_success()


async def get_phone_list(request: Request, form: schema.GetPhoneListForm = Depends()):
    get_filed = Phone.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["os", "os_version", "device_id", "screen"])
    query_data = await form.make_pagination(Phone, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_phone_sort(request: Request, form: schema.ChangeSortForm):
    await Phone.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_phone(request: Request, form: schema.GetPhoneForm):
    phone = await Phone.validate_is_exist("运行设备不存在", id=form.id)
    new_phone = await phone.copy()
    return request.app.success("复制成功", data=new_phone)


async def get_phone_detail(request: Request, form: schema.GetPhoneForm = Depends()):
    phone = await Phone.validate_is_exist("运行设备不存在", id=form.id)
    return request.app.get_success(phone)


async def add_phone(request: Request, form: schema.AddPhoneForm):
    await Phone.batch_insert([data.dict() for data in form.data_list], request.state.user)
    return request.app.post_success()


async def change_phone(request: Request, form: schema.EditPhoneForm):
    await Phone.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_phone(request: Request, form: schema.GetPhoneForm):
    await Phone.filter(id=form.id).delete()
    return request.app.delete_success()
