from flask import render_template, redirect, url_for, request, abort
from app import app, db
from app.models import User, Setting
import random

suits = ["spades", "hearts", "diamonds", "clubs"]
ranks = [
	"two", "three", "four", "five", "six", 
	"seven", "eight", "nine", "ten", 
	"jack", "queen", "king", "ace"
]

def full_deck():
	return [
		f'{rank} of {suit}' for rank in ranks for suit in suits
	]

get_seed = lambda: Setting.query.filter(Setting.name=='seed').one()

@app.route('/admin')
def admin():
	return render_template('admin.html', users=User.query.all(), seed=get_seed())

@app.route('/admin/add', methods = ['POST'])
def add_user():
	name = request.form['name']

	if name != "":
		new_user = User(name=name, ready=False)
		db.session.add(new_user)
		db.session.commit()

	return redirect(url_for('admin'))


@app.route('/admin/next', methods = ['POST'])
def admin_next():
	next_round()

	return redirect(url_for('admin'))


def next_round():
	new_seed = random.randint(1, 10**5)
	seed = get_seed()
	seed.value = new_seed

	for user in User.query.all():
		user.ready = False

	db.session.commit()


@app.route('/<username>')
def user(username):
	user_i = 0
	for test_user in User.query.all():
		if test_user.name == username:
			break
		user_i += 1
	else:
		abort(404)

	cards = deal_str_cards(user_i, get_seed(), User.query.count())
	return render_template('user.html', hand=cards, name=username)

@app.route('/<username>/next', methods = ['POST'])
def user_next(username):
	user_obj = User.query.filter(User.name == username).one()
	user_obj.ready = True
	db.session.commit()

	if User.query.filter(User.ready == False).count() == 0:
		next_round()

	return redirect(url_for('user', username=username))


@app.route('/extra')
def extra_hand():
	count = User.query.count()
	cards = deal_str_cards(count, get_seed(), count)
	return render_template('user.html', hand=cards)

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
	return cards[user_id*hand_length:user_id*hand_length+hand_length+1]

