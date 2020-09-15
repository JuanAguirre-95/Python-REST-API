from flask import Flask, request, Response, jsonify, redirect, session
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
import configparser
import logging
from resources.db_controller import DbController
from resources.models.user_model import UserModel
from resources.models.item_model import ItemModel
from resources.common.errors import DbCreateError,DbDeleteError,DbListError,DbReadError,DbUpdateError

#log = logging.Logger() TO BE ADDED LATER

config = configparser.ConfigParser() #settings.ini parser
config.read("config/settings.cfg")
print("Loaded configs from file.")

SERVER_IP = config["SERVER"]["SERVER_IP"]
SERVER_PORT = config.getint("SERVER","SERVER_PORT")
SERVER_DEBUG_MODE = config.getboolean("SERVER","SERVER_DEBUG_MODE")

BASE_ROUTE = config.get("ROUTES", "BASE_ROUTE")
COLLECTION_ROUTE = BASE_ROUTE + config.get("ROUTES", "COLLECTION_ROUTE")
AUTH_ROUTE = BASE_ROUTE + config.get("ROUTES", "AUTH_ROUTE")

DATABASE_HOSTNAME = config.get("DATABASE", "DATABASE_HOSTNAME")
DATABASE_PORT = config.getint("DATABASE","DATABASE_PORT")
DATABASE_NAME = config.get("DATABASE", "DATABASE_NAME")
USER_COLLECTION = config.get("DATABASE", "USER_COLLECTION")
ITEM_COLLECTION = config.get("DATABASE", "ITEM_COLLECTION")

USER_ADMIN_NAME= config.get("ADMIN","ADMIN_NAME")
USER_ADMIN_PASS= config.get("ADMIN","ADMIN_PASS")

app = Flask(__name__)
app.secret_key = config.get("SECURITY","SECRET_KEY")

crypto = Bcrypt(app)

api = Api(app)

userDb = DbController(DATABASE_HOSTNAME, DATABASE_PORT,DATABASE_NAME, USER_COLLECTION)
try:
	if userDb.item_exists("username",USER_ADMIN_NAME) == False:
		pwsd = crypto.generate_password_hash(USER_ADMIN_PASS)
		admin = UserModel(username=USER_ADMIN_NAME,password=pwsd,is_admin=True)
		userDb.create(admin.get_dict())

except DbReadError:
	pass
itemDb = DbController(DATABASE_HOSTNAME, DATABASE_PORT,DATABASE_NAME, ITEM_COLLECTION)

class Login(Resource):
	def get(self):
		"""
		Redirect to login page
		"""
		if "USERNAME" in session:
			return Response("Already logged in.",200) #TO DO: Define where it goes by default
		return Response("Not logged in.",401)
	def post(self):
		"""
		Login the specified user
		"""
		try:
			username = request.form["username"]
			password = request.form["password"] #TODO: Revise security

			print(username,password)
			# Fetch user from db using received username
			user = userDb.read("username", username)
			if user is None:
				return Response("Username or password incorrect.",401)
			verification = crypto.check_password_hash(user["password"], password)

			if verification != None:  #
				session["USERNAME"] = user["username"]
				return Response("Logged in",200)
			return Response("Username or password is incorrect",401)
		except DbReadError:
			print("User does not exist. ")

class Logout(Resource):
	def get(self):
		"""
		Logout the current user
		"""
		session.pop("USERNAME", None)
		return Response("Logged out.",200)
		
class RegisterUser(Resource):
	def get(self):
		return redirect(AUTH_ROUTE + "/register")
	def post(self):
		
		try:
			if "USERNAME" in session:
				#req = request.get_json()
				usr = UserModel(request.form["username"],crypto.generate_password_hash(request.form["password"]),request.form["is_admin"])
				userDb.create(usr.get_dict())
				return Response("User Created.",201)
			else:
				return Response("Unauthorized.", 401)
		except DbCreateError:
			return Response("Internal server error.",500)


class DeleteUser(Resource):
	def get(self):
		pass
	
#CRUDL    
class Create(Resource):
	"""
	Adds item to the database
	"""
	def post(self): 
		try:
			#TODO Add some validation to the json
			if "USERNAME" in session:
				item = request.form.to_dict()
				item["_id"] = int(item["_id"])
				item["visibility"] = int(item["visibility"])
				item["price"] = float(item["price"])
				#model = ItemModel(reqdict=item)
				itemDb.create(item)
				return Response("Added item.",200)
			else:
				return Response("Unauthorized.",401)
		except DbCreateError:
			return Response("Could not add item.",500)
		
class Read(Resource):
	"""
	Reads item from database based on the item ID. If item is not visible and the user is not logged in returns empty
	"""
	def get(self,id):
		try:
			items = itemDb.read("_id",id)
			if items == None:
				return jsonify({})
			object = ItemModel(reqdict=items)
			if object.visibility == 0:
				if "USERNAME" in session:
					return jsonify(object.get_dict())
				else:
					return jsonify({})
			else:
				return jsonify(object.get_dict())        
		except DbReadError:
			return Response("Error reading item.",500)


class Update(Resource):
	"""
	Patches item from the database.
	"""
	def patch(self,id):
		try:
			req = request.get_json()
			print(req)
			itemDb.update(id,req)
			return Response("Patched item.",200)
		except DbUpdateError:
			return Response("Error patching item.",500)

class Delete(Resource):
	"""
	Deletes item from the database
	"""
	def delete(self,id):
		try:
			if "USERNAME" in session:
				itemDb.delete(id)
				return Response("Deleted.",200)
			else:
				return Response("Unauthorized.",401)
		except DbDeleteError:
			return Response("Error deleting item.",500)

class List(Resource):
	"""
	Lists all items added to the item database. If user is logged in lists all, if not only the active
	"""
	def get(self):
		try:
			lista = itemDb.list()
			if "USERNAME" in session:
				return jsonify(lista)
			else:
				filter = [elem for elem in lista if elem["visibility"] == 1]
				return jsonify(filter)
		except DbListError:
			return Response("Error listing items",500)

class MassImport(Resource):
	"""
	Mass Item processing endpoints
	"""

	def get(self):
		pass

	def post(self):
		"""
		Parses file and adds the items to the database. 
		"""
		pass

#AUTH ROUTES
api.add_resource(Login,AUTH_ROUTE,AUTH_ROUTE + "/login")
api.add_resource(Logout,AUTH_ROUTE,AUTH_ROUTE + "/logout")
api.add_resource(RegisterUser,AUTH_ROUTE,AUTH_ROUTE + "/register")

#RESOURCE ROUTES
api.add_resource(Create,COLLECTION_ROUTE,COLLECTION_ROUTE + "/create") #POST
api.add_resource(Read,COLLECTION_ROUTE,COLLECTION_ROUTE+"/read/<int:id>") #GET
api.add_resource(Update,COLLECTION_ROUTE,COLLECTION_ROUTE+"/update/<int:id>") #UPDATE
api.add_resource(Delete,COLLECTION_ROUTE,COLLECTION_ROUTE+"/delete/<int:id>") #DELETE
api.add_resource(List,COLLECTION_ROUTE,COLLECTION_ROUTE+"/list") #GET

#MASS IMPORT ROUTES


if __name__ == "__main__":
	app.run(host=SERVER_IP,port=SERVER_PORT,debug=SERVER_DEBUG_MODE)