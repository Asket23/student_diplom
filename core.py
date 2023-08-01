import datetime

import vk_api

from config import acces_token



class VkTools():
    def __init__(self, acces_token):
       self.api = vk_api.VkApi(token=acces_token)

    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation,home_town' 
                            }
                            )
        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if
                     'first_name' in info and 'last_name' in info else None,
                     'bdate': self._bdate_toyear(info.get('bdate')) if info.get('bdate') is not None else None,
                     'sex': info.get('sex'),
                     'city': info.get('city')['title'] if info.get('city') is not None else None
                     }
        return user_info
    
    def serch_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        home = params['city']

        user_year = params['bdate']
        age_from = user_year - 5
        age_to = user_year + 5
        offset = offset

        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'home': home,
                                 'is_closed': False
                                }
                            )
        try:
            users = users['items']
        except ApiError as e:
            users = []
            print(f'error = {e}')
        
        res = []

        for user in users:
            if user['is_closed'] is False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        try:
            photos = photos['items']
        except KeyError as k:
            photos = {}
            print(f'error = {k}')
        
        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
            
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(789657038)
    users = bot.serch_users(params, 20)
    print(bot.get_photos(users[2]['id']))

