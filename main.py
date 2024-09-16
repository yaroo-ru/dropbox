import dropbox
from datetime import datetime, timedelta
import time

# Замените 'YOUR_TEAM_ACCESS_TOKEN' на ваш реальный токен доступа к командному Dropbox
ACCESS_TOKEN = ''
# dbxt = dropbox.DropboxTeam(ACCESS_TOKEN)
dbxt = dropbox.DropboxTeam(
    app_key='',
    app_secret='',
    oauth2_refresh_token=""
)

result = dbxt.team_members_list()
first_member_id = ""

r = dbxt.team_namespaces_list()

namespace_id = None
for namespace in r.namespaces:
    if namespace.name == 'Мастерская документалистики Семейная история':
        namespace_id = namespace.namespace_id
        break

assert namespace_id is not None, "Could not find needed namespace."

dbxtm = dbxt.as_admin(first_member_id)
path = dropbox.common.PathRoot.namespace_id(namespace_id)
dbxtmp = dbxtm.with_path_root(path)


def delete_raw_files(folder_path, flag=False):
    try:
        # Получаем список файлов и папок в папке
        res = dbxtmp.files_list_folder(folder_path)
        for entry in res.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                print(f'{entry.path_lower} {entry.client_modified}')
            if isinstance(entry, dropbox.files.FileMetadata) and flag:
                delete_file(entry)
            elif isinstance(entry, dropbox.files.FolderMetadata):
                # Рекурсивно обрабатываем вложенные папки
                # Если папка содержит "raw" и НЕ содержит "согласие", то папка обрабатывается

                flag = "raw" in entry.name.lower() and "согласие" not in entry.name.lower()
                delete_raw_files(entry.path_lower, flag)

    except Exception as e:
        print(f"Ошибка: {e}")


def delete_file(entry):
    print("check1")
    # Проверяем, если файл старше 120 дней
    if entry.client_modified > datetime.now() - timedelta(days=120):
        return

    print("check2")
    formats = [
            '.3fr', '.ari', '.arw', '.bay', '.braw', '.crw',
            '.cr2', '.cr3', '.cap', '.data', '.dcs', '.dcr',
            '.dng', '.drf', '.eip', '.erf', '.fff', '.gpr',
            '.iiq', '.k25', '.kdc', '.mdc', '.mef', '.mos',
            '.mrw', '.nef', '.nrw', '.obm', '.orf', '.pef',
            '.ptx', '.pxn', '.r3d', '.raf', '.raw', '.rwl',
            '.rw2', '.rwz', '.sr2', '.srf', '.srw', '.tif',
            '.x3f', '.xmp'
        ]

    try:
        if any(entry.name.lower().endswith(fmt) for fmt in formats):
            # Удаляем файл
            dbxtmp.files_delete(entry.path_lower)
            print("delete")

    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")


while True:
    delete_raw_files('/Архив')
    print("sleep")
    time.sleep(60*60*24*7)
