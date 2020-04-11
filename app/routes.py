from flask import render_template, redirect, url_for, request, abort, jsonify
from sqlalchemy.orm.exc import NoResultFound
from app import app, db
from app.models import User, Setting
import random

suits = ['S', 'H', 'D', 'C'] #["spades", "hearts", "diamonds", "clubs"]
ranks = [
	'02', '03', '04', '05', '06', '07', '08', '09', '10',
	'11', '12', '13', '01'
]
# [
# 	"two", "three", "four", "five", "six", 
# 	"seven", "eight", "nine", "ten", 
# 	"jack", "queen", "king", "ace"
# ]

def full_deck():
	return [
		f'{suit}{rank}' for rank in ranks for suit in suits
	]

get_seed = lambda: Setting.query.filter(Setting.name=='seed').one()

@app.route('/admin')
def admin():
	return render_template('admin.html', users=User.query.all(), seed=get_seed())

@app.route('/admin/add', methods = ['POST'])
def add_user():
	name = request.form['name']

	if name != "":
		new_user = User(name=name, mask=0, ready=False)
		db.session.add(new_user)
		db.session.commit()

	return redirect(url_for('admin'))

@app.route('/admin/delete', methods = ['POST'])
def delete_user():
	name = request.form['name']

	users = User.query.filter_by(name=name)
	for user in users:
		db.session.delete(user)
	db.session.commit()

	return redirect(url_for('admin'))

@app.route('/admin/user/<name>', methods = ['DELETE'])
def user_delete(name):

	users = User.query.filter_by(name=name)
	for user in users:
		db.session.delete(user)
	db.session.commit()

	return ''


@app.route('/admin/next', methods = ['POST'])
def admin_next():
	next_round()

	return redirect(url_for('admin'))


def next_round():
	new_seed = random.randint(1, 10**5)

	try:
		seed = get_seed()
		seed.value = new_seed
	except NoResultFound:
		seed = Setting(name='seed', value=new_seed)
		db.session.add(seed)

	for user in User.query.all():
		user.ready = False
		user.mask = 0

	try:
		extra_mask = Setting.query.filter(Setting.name=='extra_mask').one()
		extra_mask.value = 0
	except NoResultFound:
		extra_mask = Setting(name='extra_mask', value=0)
		db.session.add(extra_mask)

	db.session.commit()


@app.route('/<username>')
def user(username):
	user_i = 0
	ready = None
	mask = None
	for test_user in User.query.order_by(User.name):
		if test_user.name == username:
			ready = test_user.ready
			mask = test_user.mask
			break
		user_i += 1
	else:
		abort(404)

	cards = deal_str_cards(user_i, get_seed(), User.query.count())
	return render_template('user.html', hand=cards, name=username, ready=ready, mask='{:b}'.format(mask)[::-1])

@app.route('/<username>/next', methods = ['POST'])
def user_next(username):
	user_obj = User.query.filter(User.name == username).one()
	if user_obj.ready:
		user_obj.ready = False
		db.session.commit()
	else:
		user_obj.ready = True
		db.session.commit()

		if User.query.filter(User.ready == False).count() == 0:
			next_round()

	return redirect(url_for('user', username=username))

@app.route('/<username>/ready', methods = ['GET'])
def user_ready(username):
	users = User.query.filter_by(name=username)
	ready = True;
	for user in users:
		ready = ready and user.ready
	return jsonify(ready=ready)

@app.route('/<username>/faceup/<i>', methods = ['POST'])
def user_faceup(username, i):
	i = int(i)
	user_obj = User.query.filter(User.name == username).one()
	user_obj.mask &= ~(1<<i)
	db.session.commit()
	return ''

@app.route('/<username>/facedown/<i>', methods = ['POST'])
def user_facedown(username, i):
	i = int(i)
	user_obj = User.query.filter(User.name == username).one()
	user_obj.mask |= 1<<i
	db.session.commit()
	return ''

@app.route('/extra/faceup/<i>', methods = ['POST'])
def extra_faceup(i):
	i = int(i)
	extra_mask = Setting.query.filter(Setting.name=='extra_mask').one()
	extra_mask.value &= ~(1<<i)
	db.session.commit()
	return ''

@app.route('/extra/facedown/<i>', methods = ['POST'])
def extra_facedown(i):
	i = int(i)
	extra_mask = Setting.query.filter(Setting.name=='extra_mask').one()
	extra_mask.value |= 1<<i
	db.session.commit()
	return ''


@app.route('/extra')
def extra_hand():
	count = User.query.count()
	cards = deal_str_cards(count, get_seed(), count)
	mask = Setting.query.filter(Setting.name=='extra_mask').one().value
	return render_template('extra-hand.html', name='extra', hand=cards, mask='{:b}'.format(mask)[::-1])

def deal_str_cards(user_id, seed, users):
	cards = deal(user_id, seed, users)
	all_cards = full_deck()
	return [all_cards[i] for i in cards]

def deal(user_id, seed, users):
	print(seed.value)
	min_card = 52 - (52 // (users+1)) * (users+1) 
	cards = list(range(min_card, 52))
	hand_length = len(cards) // (users+1)

	random.Random(seed.value).shuffle(cards)
	return cards[user_id*hand_length:user_id*hand_length+hand_length]

