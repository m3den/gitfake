#!/usr/local/bin/python
import os
import sys
import logging
from datetime import datetime, date
from datetime import timedelta
from random import randint


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
GIT_USER_NAME = os.environ.get('GIT_USER_NAME')
GIT_USER_EMAIL = os.environ.get('GIT_USER_EMAIL')
GIT_REPO = os.environ.get('GIT_REPO', 'git@github.com:m3den/gitfake.git')
GIT_REPO_FOLDER = os.path.join(BASE_PATH, 'repo')
SSH_FOLDER = os.path.join(BASE_PATH, ".ssh")
ID_RSA_FILE = os.path.join(SSH_FOLDER, 'id_rsa')
ID_RSA_TEXT = os.environ.get('ID_RSA')


in_repo = lambda s: f'cd {GIT_REPO_FOLDER}; {s}'
with_id_rsa = lambda s: f'ssh-agent bash -c "ssh-add {ID_RSA_FILE}; {s}"'


# Recreate id_rsa
os.system(f'rm -rf {SSH_FOLDER}')
os.system(f'mkdir -p {SSH_FOLDER}')
with open(ID_RSA_FILE, 'w') as id_rsa_file:
    id_rsa_file.write(ID_RSA_TEXT)
    id_rsa_file.write('\n')
os.system(f'chmod 0600 {ID_RSA_FILE}')

# Clone git-repo
p = os.popen("git config core.sshCommand 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'", 'w')
p.write('yes\n')
os.system(f'rm -rf {GIT_REPO_FOLDER}')
os.system(with_id_rsa(f'yes yes 2>/dev/null | git clone {GIT_REPO} {GIT_REPO_FOLDER}'))

# Check daily commits
# last_commit_date = os.popen(in_repo('git log -1 --format="%at" | xargs -I{} date -d @{} +%Y-%m-%d')).read().strip()
# if last_commit_date == str(date.today()):
#     log.info('already has commits today')
#     exit(0)

# Configure git
os.system(in_repo(f'git config --local user.name "{GIT_USER_NAME}"'))
os.system(in_repo(f'git config --local user.email "{GIT_USER_EMAIL}"'))

# Make commits
today = datetime.now()
commits_count = randint(1, 10)
for i in range(1, commits_count):
    today = today - timedelta(0, i * randint(1, 3), i * randint(2, 9), i * randint(3, 6))
    strtoday = today.strftime('%a %b %d %H:%M:%S %Y -0600')
    command = with_id_rsa(in_repo(f'git commit --allow-empty -m "{strtoday}" --date="{strtoday}"'))
    os.system(command)

# Push commits
os.system(with_id_rsa(in_repo(f'git push origin main')))
