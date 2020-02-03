import requests
import json
import os
from time import localtime, strftime


def getUsersInfo(url):
    USER_ID_FIELD = 'id'
    NAME_FIELD = 'name'
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    COMPANY_FIELD = 'company'
    COMPANY_NAME_FIELD = 'name'

    users = {}
    for user in requests.get(url).json():
        users[user[USER_ID_FIELD]] = {
            'name': user[NAME_FIELD],
            'username': user[USERNAME_FIELD],
            'email': user[EMAIL_FIELD],
            'company': user[COMPANY_FIELD][COMPANY_NAME_FIELD]
        }
    return users


def getTasks(tasks_url, users_url):
    USER_ID_FIELD = 'userId'
    TASK_TITLE_FIELD = 'title'
    TASK_STATUS_FIELD = 'completed'
    TASK_STATUS_COMPLETED = 'true'
    TASK_STATUS_INCOMPLITED = 'false'

    users = getUsersInfo(users_url)
    for task in requests.get(tasks_url).json():
        task_stat = 'done' if task[TASK_STATUS_FIELD] else 'undone'
        if len(task[TASK_TITLE_FIELD]) > 50:
            task_title = task[TASK_TITLE_FIELD][:50] + '...'
        else:
            task_title = task[TASK_TITLE_FIELD]
        users[task[USER_ID_FIELD]].setdefault(task_stat, []).append(task_title)
    return users


def writeToFile(filename, user_info):
    try:
        with open(filename, 'w') as file:
            file.write('{name} <{email}> {data} {time} \n'.format(
                name=user_info['name'],
                email=user_info['email'],
                data=strftime("%Y-%m-%d", localtime()),
                time=strftime("%H:%M", localtime()),
            ))
            file.write(user_info['company'] + '\n')
            file.write('\n')
            file.write('Завершенные задачи:\n')
            for done_task in user_info['done']:
                file.write(done_task + '\n')
            file.write('\n')
            file.write('Оставшиеся задачи:\n')
            for done_task in user_info['undone']:
                file.write(done_task + '\n')
    except:
        print('Ошибка при записи файла ' + filename)


def main():
    FILES_DIRECTORY = 'tasks/'
    DIRECTORY_EXIST = False
    FILE_FORMAT = '.txt'

    if os.path.isdir(FILES_DIRECTORY):
        DIRECTORY_EXIST = True
    else:
        try:
            os.mkdir(FILES_DIRECTORY)
        except:
            print('Не удалось создать папку tasks/')
        else:
            DIRECTORY_EXIST = True

    if DIRECTORY_EXIST:
        try:
            tasks = getTasks(
                "https://json.medrating.org/todos",
                "https://json.medrating.org/users"
                )
        except:
            print('Ошибка при получении данных, проверьте подключение к интернету')
            return
        for user_id, user_info in tasks.items():
            filename = FILES_DIRECTORY + user_info['username']
            if os.path.exists(filename + FILE_FORMAT):
                with open(filename + FILE_FORMAT, 'r') as f:
                    date_time = f.readline().split()[-2:]
                os.rename(
                    filename + FILE_FORMAT,
                    filename + '_' + date_time[0] + 'T' + date_time[1] + FILE_FORMAT
                )
            writeToFile(filename + FILE_FORMAT, user_info)


if __name__ == '__main__':
    main()
