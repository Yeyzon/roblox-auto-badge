from flask import Flask
from flask_restful import Api, Resource
import requests, re
from os import environ

app = Flask(__name__)
api = Api(app)

cookie = environ["robloxcookie"]
pw = environ["password"]

class Roblox():
    def __init__(self, cookie):
        with requests.Session() as self.session:
            self.session.cookies[".ROBLOSECURITY"] = cookie
    
    def token(self):
        return self.session.post("https://auth.roblox.com/v2/logout").headers["X-CSRF-TOKEN"]
    
    def createBadge(self, username):
        data = {
            "name": username,
            "description": "",
            "paymentSourceType": "User",
        }

        r = self.session.post("https://badges.roblox.com/v1/universes/1800603069/badges", data=data, files={"request.files": open("free.png", "rb")}, headers={"X-CSRF-TOKEN": self.token()})
        if r.status_code == 200:
            print(f"Created badge {username}")
            badgeId = r.json()["id"]
            with open("badges.txt", "a") as f:
                f.write(f"{badgeId}\n")
            self.updateGameName()
        return r.json()
    
    def updateGameName(self):
        gameInfo = self.session.get("https://games.roblox.com/v1/games/multiget-place-details?placeIds=5166670285").json()[0]
        name, desc = gameInfo["name"], gameInfo["description"]
        badges = int("".join(i for i in name if i.isdigit())) + 1
        game = self.session.get("https://www.roblox.com/games/5166670285/10-894-Badge-Walk-Free-Badges").text
        verifToken = re.findall(r"<input name=__RequestVerificationToken type=hidden value=(.+)><div id=rbx-game-passes", game)
        data = {
            "__RequestVerificationToken": verifToken,
            "Name": f"🎖️{badges:,} Badge Walk🎖️ Free Badges",
            "Description": desc
        }
        self.session.post("https://www.roblox.com/places/5166670285/update", data=data, headers={"X-CSRF-TOKEN": self.token()})

session = Roblox(cookie)

class Badges(Resource):
    def get(self):
        with open("badges.txt", "r") as f:
            badges = f.read().splitlines()
        return {"data": badges}

class CreateBadge(Resource):
    def post(self, username, password):
        if password == pw: # change da password
            return session.createBadge(username)
        else:
            return {"error": "wrong password loser"}

api.add_resource(Badges, "/badges")
api.add_resource(CreateBadge, "/createbadge/<string:username>/<string:password>")

if __name__ == "__main__":
    app.run(debug=False)
