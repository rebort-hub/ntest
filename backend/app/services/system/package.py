import subprocess
import os

from fastapi import Request

from ...schemas.system import package as schema
from ...models.config.model_factory import Config


async def get_package_list(request: Request):
    """ 获取pip包列表 """
    try:
        pip_command = await Config.get_pip_command()
        
        # 确保pip命令存在
        if not pip_command or not os.path.exists(pip_command):
            return request.app.fail(msg=f"pip命令不存在: {pip_command}")
        
        result = subprocess.run([pip_command, 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            return request.app.get_success(result.stdout)
        else:
            return request.app.fail(msg=f"获取包列表失败: {result.stderr}")
            
    except Exception as e:
        return request.app.fail(msg=f"获取包列表异常: {str(e)}")


async def install_package(request: Request, form: schema.PackageInstallForm):
    """ pip安装包 """
    try:
        package = f'{form.name.strip()}=={form.version.strip()}' if form.version else form.name
        pip_command = await Config.get_pip_command()
        
        # 确保pip命令存在
        if not pip_command or not os.path.exists(pip_command):
            return request.app.fail(msg=f"pip命令不存在: {pip_command}")
        
        result = subprocess.run([pip_command, 'install', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            return request.app.success(msg="安装成功")
        else:
            return request.app.fail(msg=f"安装失败：{result.stderr}")
            
    except Exception as e:
        return request.app.fail(msg=f"安装包异常: {str(e)}")
