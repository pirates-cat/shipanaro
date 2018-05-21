from fabric.api import *
from fabric.contrib import project

env.www_home = '/var/www'

env.local_static_root = './static'

env.remote_static_root = env.www_home + '/%s'


def setup_static():
    run('adduser www --home %s' % env.www.home)
    run('passwd -d www')
    run('passwd -l www')
    run('chown -R www: %s' % env.www.home)
    run('mkdir -p %s' % env.www.home)
    run('chmod 700 %s/.ssh' % env.www.home)
    run('touch %s/.ssh/authorized_keys' % env.www.home)
    run('chmod 400 %s/.ssh/authorized_keys' % env.www.home)


def deploy_static(host):
    local('python manage.py collectstatic --no-input --verbosity 0')
    run('mkdir -p ' + env.remote_static_root % host)
    project.rsync_project(
        remote_dir=env.remote_static_root % host,
        local_dir=env.local_static_root,
        delete=True,
        ssh_opts='-q',
        extra_opts='--quiet --no-motd', )


def format(extra_dirs=''):
    local('yapf -i -r --style pep8 shipanaro/ %s' % extra_dirs)
