import json
import pymongo

client = pymongo.MongoClient('localhost', 27017)
database = client['database']
pupils_table = database['pupils']
tasks_table = database['tasks']

# удаление всех учеников, только для тестирования
# !pupils_table.drop()

# если нет данных - добавляем
if not tasks_table.count_documents({}):
	all_tasks = []
	# интепритируем данные из dict[str, dict] -> list[dict]
	with open('tasks.json', 'r', encoding='utf-8') as file:
		for topic_number, tasks in json.load(file).items():
			for task in tasks:
				task['topic'] = int(topic_number)
				all_tasks.append(task)
	tasks_table.insert_many(all_tasks)


def update_pupil_data(pid: int, field: str, value, increment=False):
	command = '$inc' if increment else '$set'
	pupils_table.update_one({'pid': pid}, {command: {field: value}})
