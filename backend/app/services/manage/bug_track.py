from fastapi import Request, Depends

from ...models.manage.model_factory import BugTrack
from ...schemas.manage import bug_track as schema

async def get_bug_track_iteration(request: Request):
    data_list = await BugTrack.filter().distinct().values("iteration")
    return request.app.get_success(data=[data["iteration"] for data in data_list])


async def get_bug_track_list(request: Request, form: schema.GetBugListForm = Depends()):
    get_filed = ["id", "status", "replay", "business_id", "name", "detail", "iteration"]
    query_data = await form.make_pagination(BugTrack, user=request.state.user, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_bug_track_status(request: Request, form: schema.ChangeBugStatusForm):
    await BugTrack.filter(id=form.id).update(status=form.status)
    return request.app.put_success()


async def change_bug_track_replay(request: Request, form: schema.ChangeBugReplayForm):
    await BugTrack.filter(id=form.id).update(replay=form.replay)
    return request.app.put_success()


async def change_bug_track_sort(request: Request, form: schema.ChangeSortForm):
    await BugTrack.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_bug_track_detail(request: Request, form: schema.GetBugForm = Depends()):
    data = await BugTrack.validate_is_exist("bug记录不存在", id=form.id)
    return request.app.get_success(data=data)


async def add_bug_track(request: Request, form: schema.AddBugForm):
    await form.validate_request(request)
    await BugTrack.model_create(form.dict(), request.state.user)
    return request.app.post_success()


async def change_bug_track(request: Request, form: schema.ChangeBugForm):
    await BugTrack.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_bug_track(request: Request, form: schema.GetBugForm):
    await BugTrack.filter(id=form.id).delete()
    return request.app.delete_success()
