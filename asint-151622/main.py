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
	user_id = ndb.StringProperty()
	user_room = ndb.StringProperty()

class Check(ndb.Model):
	user_id = ndb.StringProperty()
	type = ndb.StringProperty()
	room = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

#Admin
temp_admin = """
<h3>Admin</h3>
<a class="btn" href="/html/admin/occupation"><button type="button">See occupation</button></a>​
<a class="btn" href="/html/admin/searchroom"><button type="button">Search Rooms</button></a>​
"""

temp_admin_occupation_get = """
<p>Spaces:</p>
<ul>
	%for b in spaces:
	<li>Name: <a href="/html/admin/occupation/{{b["id"]}}"> {{b["name"]}}</a></li>
	%end
</ul>
"""

temp_admin_occupation = """
<h3>Occupation: {{occup}} </h3>
<ul>
	%for b in list:
	<li>Name: {{b["id"]}}</li>
	%end
</ul>
"""

temp_admin_searchfenix = """
<p>Spaces:</p>
<ul>
	%for b in json:
	<li>Type: {{b["type"]}}, Id: {{b["id"]}}, Name: <a href="/html/admin/searchroom/{{b["id"]}}"> {{b["name"]}}</a></li>
	%end
</ul>
"""

temp_admin_searchfenix_room =  """
<p>Spaces: {{json["name"]}} - "{{json["id"]}}"</p>
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

#verificar o funcionamento deste
@bottle.route('/html/admin/occupation/<room_id>')
def admino_occupation_get(room_id):
	#lista de utilizadores no room
	ret_value = []
	x = User.query(User.user_room==room_id).fetch()
	for m in x:
		ret_value.append({'id': m.user_id})
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
	s = Space(room_id = obj["space"]["id"], room_name = obj["space"]["name"])
	key = s.put()
	return " "
	#return 'Space %s added with key %s' %(obj["space"]["name"], str(key.id()))


#User
temp_user = """
<h3>User: {{id1}}</h3>
<p>Room: {{room_user}}</p>
<a class="btn" href="/html/{{id1}}/rooms"><button type="button">Rooms Available</button></a>​
"""

temp_user_rooms = """
<p>Rooms Available:</p>
<ul>
	%for item in spaces:
	<li>Name: <a href="/html/{{id1}}/rooms/{{item['id']}}"> {{item['name']}} - {{item['id']}}</a></li>
	%end
</ul>
"""

temp_user_rooms_check = """
<h3>Check {{type}}</h3>
<p>Room: {{roomname}}</p>
<p><button type="button" id="add" onclick="check()">Check {{type}}</button></p>
<p id="demo"></p>

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
	if not room:
		room_name = "No room"
	else:
		for m in room:
			room = Space.query(Space.room_id == m.user_room).fetch()
			for n in room:
				room_name = n.room_name

	return template(temp_user, id1=id, room_user=room_name)

#Como aceder aos valores das querys? estou a usar fors para isso :/
@bottle.route('/html/<id>/rooms')
def userrooms(id):
	ret_value = []
	spaces = Space.query().fetch()
	for m in spaces:
		ret_value.append({'id': m.room_id,'name':m.room_name})
	return template(temp_user_rooms, id1 = id, spaces = ret_value)

@bottle.route('/html/<id>/rooms/<room_id>')
def userrooms(id, room_id):
	#Get room name
	room = Space.query(Space.room_id == room_id).fetch()
	room_name = room
	room_user_id = " "
	room_id = " "
	#get room do user e compara-lo
	room_user = User.query(User.user_id == id).fetch()
	for m in room:
		room_id = m.room_id
	for n in room_user:
		room_user_id = n.user_room

	if room_user_id == room_id:
		return template(temp_user_rooms_check, id1 = id, roomname = room_name, room = room_id, type = "OUT")
	else:
		return template(temp_user_rooms_check, id1 = id, roomname = room_name, room = room_id, type = "IN")

@bottle.put('/html/<id>/check')
def userchecks_put(id):
	rec_obj = json.dumps(request.json)
	obj = json.loads(rec_obj)
	#se for checkin realizar o checkout à anterior sala - por fazer! e alterar o valor do user em vez do colocar
	n = Check(user_id = id,type = obj['check']['type'], room = obj['check']['room'])
	key = n.put()
	u = User(user_id = id, user_room = obj['check']['room'])
	key1 = u.put()
	return " "


#Recepcao a outros programas sem ser via brownser, ver User management enunciado do projecto
#É enviar os jsons - para o cliente
@bottle.route('/api/occupation/<room_id>')
def book_id(id):
	return

#o put de cima serve para os dois ??
@bottle.put('/api/addroom/<room_id>')
def book_id(id):
	return

#Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
	"""Return a custom 404 error."""
	return 'Sorry, Nothing at this URL.'
