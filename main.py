from telebot.types import InputMediaPhoto
from traceback import format_exc
from operator import itemgetter
import telebot
import vk_api
import time
import os

bot = telebot.TeleBot(os.getenv('TG_TOKEN'))
tg_channel = os.getenv('TG_CHANNEL')
tg_admin = os.getenv('TG_ADMIN')
vk_group = os.getenv('VK_GROUP')
vk_token = os.getenv('VK_TOKEN')


def get_quality(post=None):
    urls = []
    if not post:
        return urls
    for attachment in post['attachments']:
        if attachment['type'] != 'photo':
            continue
        max_size_url = max(attachment['photo']['sizes'], key=itemgetter('height'))['url']
        urls.append(InputMediaPhoto(max_size_url))
    return urls


def main():
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()

    while True:
        post = vk.wall.get(
            owner_id=int(vk_group),
            filter='owner'
        )['items'][1]

        with open('data/latest_date.txt', 'r+') as f:
            old_date = int(f.read())

        if post['marked_as_ads'] == 1:
            time.sleep(600)
            continue

        try:
            post_date = post['date']

            if post_date > old_date:
                bot.send_media_group(chat_id=tg_channel, media=get_quality(post))
                with open('data/latest_date.txt', 'r+') as f:
                    f.seek(0)
                    f.write(str(post_date))
        except KeyError:
            time.sleep(600)
            continue
        except:
            bot.send_message(chat_id=tg_admin, text=f'Something went wrong:\n{format_exc()}')
        time.sleep(600)


if __name__ == '__main__':
    main()
