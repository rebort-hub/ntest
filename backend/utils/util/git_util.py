# -*- coding: utf-8 -*-
import os

from git.repo import Repo
from git.repo.fun import is_git_dir

GIT_FILE_ADDRESS = os.path.abspath(os.path.join(os.path.abspath("..."), "../../../" + r"/git_files/"))
print(GIT_FILE_ADDRESS)


class GitRepository:
    """ git仓库管理 """

    def __init__(self, local_path, repo_url, branch="master"):
        self.local_path = local_path
        self.repo_url = repo_url
        self.repo = None
        self.initial(repo_url, branch)

    def initial(self, repo_url, branch):
        """ 初始化git仓库 """
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)

        git_local_path = os.path.join(self.local_path, ".git")
        if not is_git_dir(git_local_path):
            self.repo = Repo.clone_from(repo_url, to_path=self.local_path, branch=branch)
        else:
            self.repo = Repo(self.local_path)

    def pull(self):
        """ 从线上拉最新代码 """
        self.repo.git.pull()

    def branches(self):
        """ 获取所有分支 """
        branches = self.repo.remote().refs
        return [item.remote_head for item in branches if item.remote_head not in ["HEAD", ]]

    def commits(self):
        """ 获取所有提交记录 """
        commit_log = self.repo.git.log(
            '--pretty={"commit":"%h","author":"%an","summary":"%s","date":"%cd"}',
            max_count=50,
            date="format:%Y-%m-%d %H:%M"
        )
        log_list = commit_log.split("\n")
        return [eval(item) for item in log_list]

    def tags(self):
        """ 获取所有tag """
        return [tag.name for tag in self.repo.tags]

    def change_to_branch(self, branch):
        """ 切换分支 """
        self.repo.git.checkout(branch)

    def change_to_commit(self, branch, commit):
        """ 切换commit """
        self.change_to_branch(branch=branch)
        self.repo.git.reset("--hard", commit)

    def change_to_tag(self, tag):
        """ 切换tag """
        self.repo.git.checkout(tag)


if __name__ == "__main__":
    # repo = GitRepository(
    #     GIT_FILE_ADDRESS,
    #     "https://codeup.aliyun.com/5fbe3118672533690be72b12/xintech-fms/xintech-fms-admin-front.git"
    # )
    # branch_list = repo.branches()
    # print(branch_list)
    # repo.change_to_branch("dev")
    # repo.pull()

    services_path = GIT_FILE_ADDRESS + "/src/services"
    for path in os.listdir(services_path):
        print(f'path: {path},  isfile: {os.path.isfile(services_path + "/" + path)}')
