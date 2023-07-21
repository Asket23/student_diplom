# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import engine, add_user, user_verification


class BotInterface():

    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.params = {}
        self.offset = 0
        self.keys = []

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )

    def new_bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def questions(self, event):
        if self.params['name'] is None:
            self.message_send(event.user_id, 'Введите имя и фамилию:')
            return event.text

        if self.params['sex'] is None:
            self.message_send(event.user_id, 'Введите пол (1-м, 2-ж):')
            return int(event.text)

        elif self.params['city'] is None:
            self.message_send(event.user_id, 'Введите город, в котором проживаете:')
            return event.text

        elif self.params['year'] is None:
            self.message_send(event.user_id, 'Введите дату рождения в формате (дд.мм.гггг):')
            return self.new_bdate_toyear(event.text)

    def event_handler(self):

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй, {self.params["name"]}')

                    # обработка данных, которые не получили
                    self.keys = self.params.keys()
                    for i in self.keys:
                        if self.params[i] is None:
                            self.params[i] = self.questions(event)

                    self.message_send(event.user_id, 'Регистрация прошла успешно')

                elif command == 'поиск':
                    users = []
                    while True:
                        if users:
                            user = users.pop()
                            #здесь логика дял проверки и добавления в бд
                            if user_verification(engine, event.user_id, user['id']) is False:
                                add_user(engine, event.user_id, user['id'])
                                break
                        else:
                            users = self.api.serch_users(self.params, self.offset)

                    photos_user = self.api.get_photos(user['id'])
                    self.offset += 10

                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                        if num == 2:
                            break
                    self.message_send(event.user_id,
                                      f'Встречайте {user["name"]} ссылка: vk.com/id{user["id"]}',
                                      attachment=attachment
                                      )

                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()



