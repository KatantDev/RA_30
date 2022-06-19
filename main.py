import csv
import seaborn
import vk
from flask import Flask, render_template, jsonify


TOKEN = 'TOKEN'
GROUP_ID = '206944280'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

session = vk.Session(access_token=TOKEN)
api = vk.API(session, v='5.131')


@app.route('/')
def dashboard():
    subscribers = api.groups.getMembers(group_id=GROUP_ID)['count']
    with open('output.csv') as csv_file:
        posts = list(csv.DictReader(csv_file))[1:]
        return render_template('dashboard.html', subscribers=subscribers, posts=posts)


@app.route('/comments/<post_id>')
def get_comments(post_id):
    comments = api.wall.getComments(owner_id=f'-{GROUP_ID}', post_id=post_id, need_likes=1)['items']
    sorted_comments = sorted(comments, key=lambda item: item['likes']['count'], reverse=True)[:5]
    user_ids = [item['from_id'] for item in sorted_comments]

    users = api.users.get(user_ids=user_ids, name_case='gen')
    labels = [f'От {item["first_name"]} {item["last_name"]}' for item in users]
    values = [item['likes']['count'] for item in sorted_comments]
    colors = seaborn.color_palette('hls', 5).as_hex()
    return jsonify({'labels': labels, 'values': values, 'colors': colors})


if __name__ == '__main__':
    app.run(port=8000, debug=True)
