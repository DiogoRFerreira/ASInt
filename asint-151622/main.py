"""`main` is the top level module for your Bottle application."""
# import the Bottle framework
from bottle import Bottle, run, debug, template, request, redirect
import json
import urllib2
from google.appengine.ext import ndb
debug(True)
# Create the Bottle WSGI application.
bottle = Bottle()
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# Define an handler for the root URL of our application.
@bottle.route('/hello')
def hello():
	"""Return a friendly HTTP greeting."""
	return " Hello World!"

class Space(ndb.Model):
	room_id = ndb.StringProperty()
	room_name = ndb.StringProperty()

class User(ndb.Model):
	user_username = ndb.StringProperty()
	user_id = ndb.StringProperty()
	user_room = ndb.StringProperty()

class Check(ndb.Model):
	user_id = ndb.StringProperty()
	type = ndb.StringProperty()
	room = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

#Admin
temp_admin = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
h3 {text-align: center;color: #282828;font-size: 200%;}
p {text-align: center;}
</style>
<h3>Admin</h3><p>
<a class="btn" href="/html/admin/occupation"><button type="button">See occupation</button></a>​
<a class="btn" href="/html/admin/searchroom"><button type="button">Search Rooms</button></a>​</p>
"""

temp_admin_occupation_get = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
h3 {text-align: center;color: #282828;font-size: 200%;}
ul {text-align: center;}
</style>
<h3>Spaces:</h3>
<ul style="list-style-type:none">
	%for b in spaces:
	<li>Name: <a href="/html/admin/occupation/{{b["id"]}}"> {{b["name"]}}</a></li>
	%end
</ul>
"""

temp_admin_occupation = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
h3 {text-align: center;color: #282828;font-size: 200%;}
ul {text-align: center;}
</style>
<h3>Occupation: {{occup}} </h3>
<ul style="list-style-type:none">
	%for b in list:
	<li>Name: {{b["name"]}}</li>
	%end
</ul>
"""

temp_admin_searchfenix = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
h3 {text-align: left;color: #282828;font-size: 200%;}
ul {text-align: center;}
</style>
<h3>Spaces:</h3>
<ul style="list-style-type:none">
	%for b in json:
	<!--<li>{{b["type"]}}, Id: {{b["id"]}}, Name: <a href="/html/admin/searchroom/{{b["id"]}}"> {{b["name"]}}</a></li>-->
	<li>{{b["type"]}}: <a href="/html/admin/searchroom/{{b["id"]}}"> {{b["name"]}}</a></li>
	%end
</ul>
"""

temp_admin_searchfenix_room =  """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
p {text-align: center;color: #282828;font-size: 200%;}
</style>
<!--<p>Spaces: {{json["name"]}} - "{{json["id"]}}"</p>-->
<p>{{json["type"]}}: {{json["name"]}}</p>
<p><button type="button" id="add" onclick="add()">ADD</button></p>
<p id="demo"></p>

<script>
function add(){
	document.getElementById("demo").innerHTML = "Added1!"
	var xhttp = new XMLHttpRequest();
	var h = {};
	h['space']={'id':"{{json["id"]}}",'name':"{{json["name"]}}"};
	document.getElementById("demo").innerHTML = "Added2!"
	xhttp.open("PUT", "/html/admin/addroom", true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(h));
	document.getElementById("demo").innerHTML = "Added!"
}
</script>
"""

#Admin
@bottle.route('/html/admin')
def admin():
	return template(temp_admin)

##########Ocupation######
@bottle.route('/html/admin/occupation')
def adminoccupation():
	ret_value = []
	spaces = Space.query().fetch()
	for m in spaces:
		ret_value.append({'id': m.room_id,'name':m.room_name})
	return template(temp_admin_occupation_get, spaces = ret_value)


@bottle.route('/html/admin/occupation/<room_id>')
def admino_occupation_get(room_id):
	ret_value = []
	x = User.query(User.user_room==room_id).fetch()
	for m in x:
		ret_value.append({'name': m.user_username})
	y = len(ret_value)
	return template(temp_admin_occupation, occup = y,list = ret_value)

###########SearchFenix#######
@bottle.route('/html/admin/searchroom')
def adminsearchfenix():
	URI = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'
	data = urllib2.urlopen(URI).read()
	print data
	d = json.loads(data)
	print d
	return template(temp_admin_searchfenix, json = d)

@bottle.route('/html/admin/searchroom/<room_id>')
def adminsearchfenix(room_id):
	URI = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'+room_id
	data = urllib2.urlopen(URI).read()
	print data
	d = json.loads(data)
	print d
	if d['type'] == "ROOM":
		return template(temp_admin_searchfenix_room,json = d)
	else:
		return template(temp_admin_searchfenix, json = d['containedSpaces'])

@bottle.put('/html/admin/addroom')
def adminput():
	rec_obj = json.dumps(request.json)
	obj = json.loads(rec_obj)
	space = Space.query(Space.room_id == obj["space"]["id"]).fetch()
	if not space:
		s = Space(room_id = obj["space"]["id"], room_name = obj["space"]["name"])
		key = s.put()
	return " "
	#return 'Space %s added with key %s' %(obj["space"]["name"], str(key.id()))


#User
temp_user = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
h3 {text-align: left;color: #282828;font-size: 200%;}
p {text-align: center;}
</style>
<h3>User: {{id1}} - {{username}}</h3>
<p>Room: {{room_user}}</p>
<p><a class="btn" href="/html/{{id1}}/rooms"><button type="button">Rooms Available</button></a>​</p>
<p><a class="btn" href="/html/{{id1}}/searchfriend"><button type="button">Search Friend</button></a>​</p>
"""

temp_user_rooms = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
p {text-align: left;color: #282828;font-size: 200%;}
ul {text-align: center;}
</style>
<p>Rooms Available:</p>
<ul style="list-style-type:none">
	%for item in spaces:
	<li>Name: <a href="/html/{{id1}}/rooms/{{item['id']}}"> {{item['name']}}</a></li>
	%end
</ul>
"""

temp_user_rooms_check = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
h3 {text-align: left;color: #282828;font-size: 200%;}
p {text-align: center;}
ul {text-align: center;}
</style>
<h3>Check {{type}}</h3>
<p>Room: {{roomname}}</p>

<p><button type="button" id="add" onclick="check()">Check {{type}}</button></p>
<p id="demo"></p>
<p>Users:</p>
<ul style="list-style-type:none">
	%for b in list:
	<li>Name: {{b["name"]}}</li>
	%end
</ul>
<script>
function check(){
	var xhttp = new XMLHttpRequest();
	var h = {};
	h['check'] = {'type':"{{type}}",'room':"{{room}}"};
	xhttp.open("PUT", "/html/"+{{id1}}+"/check", true);
	xhttp.setRequestHeader("Content-type", "application/json");
	xhttp.send(JSON.stringify(h));
	document.getElementById("demo").innerHTML = "Checked!"
}
</script>
"""

@bottle.route('/html/<id>')
def user(id):
	allusers = User.query().fetch()
	room = User.query(User.user_id == id).fetch()
	room_name = ""
	user_name = " "
	if not room:
		return """<p> User id does not exist.</p>
		"""
	else:
		for n in room:
			if n.user_room == "None":
				room_name = "No room"
			else:
				room1 = Space.query(Space.room_id == n.user_room).fetch()
				for k in room1:
					room_name = k.room_name
			user_name = n.user_username
		return template(temp_user, id1=id, room_user=room_name, username = user_name)

@bottle.route('/html/<id>/rooms')
def userrooms(id):
	ret_value = []
	spaces = Space.query().fetch()
	for m in spaces:
		ret_value.append({'id': m.room_id,'name':m.room_name})
	return template(temp_user_rooms, id1 = id, spaces = ret_value)

@bottle.route('/html/<id>/rooms/<room_id>')
def userrooms(id, room_id):
	#Define Space name
	room = Space.query(Space.room_id == room_id).fetch()
	room_name = " "
	if not room:
		return """<p>Not a valid room id!"""
	else:
		for i in room:
			room_name = i.room_name
	#Define the users inside the Space
	ret_value = []
	x = User.query(User.user_room==room_id).fetch()
	for m in x:
		ret_value.append({'name': m.user_username})
	#Define IN/OUT
	room_user_id = " "
	room_id = " "
	room_user = User.query(User.user_id == id).fetch()
	for m in room:
		room_id = m.room_id
	for n in room_user:
		room_user_id = n.user_room

	if room_user_id == room_id:
		return template(temp_user_rooms_check, id1 = id, roomname = room_name, room = room_id, type = "OUT",list = ret_value)
	else:
		return template(temp_user_rooms_check, id1 = id, roomname = room_name, room = room_id, type = "IN",list = ret_value)

@bottle.put('/html/<id>/check')
def userchecks_put(id):
	rec_obj = json.dumps(request.json)
	obj = json.loads(rec_obj)
	if obj['check']['type'] == "IN":
		room_user = User.query(User.user_id == id).fetch()
		room_user_id = " "
		for n in room_user:
			room_user_id = n.user_room
		if room_user_id == "None":
			n = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
			key = n.put()
			room_user2 = User.query(User.user_id == id).get()
			room_user2.user_room = obj['check']['room']
			key = room_user2.put()
		else:
			n = Check(user_id = id,type = "OUT", room = room_user_id)
			key = n.put()
			m = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
			key = m.put()
			room_user2 = User.query(User.user_id == id).get()
			room_user2.user_room = obj['check']['room']
			key = room_user2.put()
	else:
		n = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
		key = n.put()
		room_user2 = User.query(User.user_id == id).get()
		room_user2.user_room = "None"
		key = room_user2.put()
	return " "


@bottle.route('/html/signup')
def signup():
    return """
		<style>
		body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
		h3 {text-align: left;color: #282828;font-size: 200%;}
		</style>
		<form action="/html/login" method="post">
		<h3>Username: <input name="username" type="text" />
		<input value="Login" type="submit" /></h3>
		</form>
		"""

temp_login = """
<style>
body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
p {text-align: left;color: #282828;font-size: 200%;}
</style>
<p>Your ID is {{id1}}</p>
<p><a href="/html/{{id1}}">Click here to go to the user menu</a></p>
"""
@bottle.post('/html/login')
def do_login():
	username = request.forms.get('username')
	user = User.query(User.user_username == username).fetch()
	if not user:
		biggestid = "0"
		try:
			biggestid = User.query().order(-User.user_id).get().user_id
		except:
			biggestid = "0"
		id = long(biggestid) + 1
		u = User(user_username = username, user_id = str(id), user_room = "None")
		key1 = u.put()
		return template(temp_login, id1 = id)
	else:
		return """<style>
		body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
		p {text-align: left;color: #282828;font-size: 200%;}
		</style><p>Login failed. User already exists</p>"""

temp_search = """
		<style>
		body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
		p {text-align: left;color: #282828;font-size: 200%;}
		</style>
		<p>Search Friend: </p>
		<form action="/html/{{id1}}/searchfriend" method="post">
		<p>Username: <input name="username" type="text" />
		<input value="Search" type="submit" /></p>
		</form>
		"""
@bottle.route('/html/<id>/searchfriend')
def search_friend(id):
	return template(temp_search, id1 =id)


temp_search_friend = """
		<style>
		body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
		p {text-align: left;color: #282828;font-size: 200%;}
		</style>
		<p>Friend is inside room {{r}} </p>
		"""
@bottle.post('/html/<id>/searchfriend')
def search_friend(id):
	username = request.forms.get('username')
	user = User.query(User.user_username == username).fetch()
	room = " "
	room_name = " "
	if not user:
		return """
		<style>
		body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
		p {text-align: left;color: #282828;font-size: 200%;}
		<p> Username does not exist!</p>
		"""
	else:
		for m in user:
			room = m.user_room
		room = Space.query(Space.room_id == room).fetch()
		for n in room:
			room_name = n.room_name
		if room_name == " ":
			return """
			<style>
			body {background-image: url('/assets/images/tecnico.jpg');background-size: contain;background-repeat: no-repeat;}
			p {text-align: left;color: #282828;font-size: 200%;}
			</style>
			<p> Friend does not have a room!</p>
			"""
	return template(temp_search_friend, r=room_name)

#######ADMIN API###############################################################
#basta enviar os 3 jsons(User,space,Check) diferentes
#Fenix
@bottle.route('/api/admin/searchroom')
def adminsearchfenix_api():
	URI = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'
	data = urllib2.urlopen(URI).read()
	print data
	d = json.loads(data)
	return d
@bottle.route('/api/admin/searchroom/<room_id>')
def adminsearchfenix_api(room_id):
	URI = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'+room_id
	data = urllib2.urlopen(URI).read()
	print data
	d = json.loads(data)
	return d

#Addroom
@bottle.put('/api/admin/addroom')
def adminput_api():
	rec_obj = json.dumps(request.json)
	obj = json.loads(rec_obj)
	s = Space(room_id = obj["space"]["id"], room_name = obj["space"]["name"])
	key = s.put()
	return " "

@bottle.put('/api/<id>/check')
def userchecksapi_put(id):
	rec_obj = json.dumps(request.json)
	obj = json.loads(rec_obj)
	if obj['check']['type'] == "IN":
		room_user = User.query(User.user_id == id).fetch()
		room_user_id = " "
		for n in room_user:
			room_user_id = n.user_room
		if room_user_id == "None":
			n = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
			key = n.put()
			room_user2 = User.query(User.user_id == id).get()
			room_user2.user_room = obj['check']['room']
			key = room_user2.put()
		else:
			n = Check(user_id = id,type = "OUT", room = room_user_id)
			key = n.put()
			m = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
			key = m.put()
			room_user2 = User.query(User.user_id == id).get()
			room_user2.user_room = obj['check']['room']
			key = room_user2.put()
	else:
		n = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
		key = n.put()
		room_user2 = User.query(User.user_id == id).get()
		room_user2.user_room = "None"
		key = room_user2.put()
	return " "

@bottle.route('/api/rooms')
def userrooms_api(id):
	ret_value = []
	spaces = Space.query().fetch()
	for m in spaces:
		ret_value.append({'id': m.room_id,'name':m.room_name})
	value = {}
	value["rooms"] = ret_value
	return value

@bottle.route('/api/users')
def users_api(id):
	ret_value = []
	users = User.query().fetch()
	for m in users:
		ret_value.append({'username': m.user_username,'id':m.user_id,'room':m.user_room})
	value = {}
	value["users"] = ret_value
	return value

@bottle.route('/api/checks')
def checks_api(id):
	ret_value = []
	checks = Check.query().fetch()
	for m in checks:
		ret_value.append({'user_id': m.user_id,'type':m.type,'room':m.room,'time':m.time})
	value = {}
	value["checks"] = ret_value
	return value

#Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
	"""Return a custom 404 error."""
	return 'Sorry, Nothing at this URL.'
