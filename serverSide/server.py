from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
import sys
import hashing
import formatting
import usersDB

class MyRequestHandler (BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Content-Length")
        self.end_headers()
        return

    def do_POST(self):
        if self.path == "/defaults":
            i = 0
            self.encryptDefault()
            # self.end_headers()
        elif self.path == "/customs":
            self.encryptCustom()
        else:
            self.send404()
        return

    def do_GET(self):
        if self.path == "/specifications":
            self.retrieveCollection()
        else:
            self.send404()
        return

#Here I start the implementation:

    def encryptDefault(self):
        print(self.headers)
        length = int(self.headers["Content-Length"])

        # Retrieve data:
        body = self.rfile.read(length).decode("utf-8")
        print("Body:", body)
        parsedBody = parse_qs(body)
        print("Parsed Body:", parsedBody)
        
        # Gather data:
        username = parsedBody["username"][0]
        password = parsedBody["password"][0]
        website = parsedBody["website"][0]
        counter = parsedBody["counter"][0]

        print(parsedBody["username"][0])
        print(parsedBody["password"][0])
        print(parsedBody["website"][0])
        print(parsedBody["counter"][0])

        salt = username + website + counter

        print("Password and salt:")
        print(password)
        print(salt)

        #here I need to hash the salt probably with sha256 before passing it in

        finalPassword = hashing.encrypt(password, salt)

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.sendPassword(finalPassword)

        #now we will check if the user needs to be added to the database
        self.checkDatabase(username, website, counter, -1, "", False, False, False)

        return

    def sendPassword(self, encryptedPassword):
        encryptedJSON = {}
        encryptedJSON["encryptedPassword"] = encryptedPassword
        intoBytes = bytes(json.dumps(encryptedJSON), "utf-8")
        self.wfile.write(intoBytes)
        return
    

    def encryptCustom(self):
        print(self.headers)
        length = int(self.headers["Content-Length"])

        # Retrieve data:
        body = self.rfile.read(length).decode("utf-8")
        print("Body:", body)
        parsedBody = parse_qs(body)
        print("Parsed Body:", parsedBody)
        
        # Gather data:
        username = parsedBody["username"][0]
        password = parsedBody["password"][0]
        website = parsedBody["website"][0]
        counter = parsedBody["counter"][0]
        passwordLength = parsedBody["length"][0]
        symbols = parsedBody["symbols"][0]
        uppercase = parsedBody["uppercase"][0]
        lowercase = parsedBody["lowercase"][0]
        numbers = parsedBody["numbers"][0]

        # allowing for no given length or symbols
        if passwordLength != "default":
            passwordLength = int(passwordLength)
        #passing a empty string so the alphabet doesn't mess up and we can still check.
        # if symbols == "default":
        #     symbols = ""

        if (uppercase == "true"):
            uppercase = True
        else:
            uppercase = False
        if (lowercase == "true"):
            lowercase = True
        else:
            lowercase = False
        if (numbers == "true"):
            numbers = True
        else:
            numbers = False
        

        print(username)
        print(password)
        print(website)
        print(counter)
        print(passwordLength)
        print(symbols)
        print("uppercase, lowercase, and numbers as booleans:")
        print(uppercase)
        print(lowercase)
        print(numbers)

        salt = username + website + counter

        encryptedPassword = hashing.encrypt(password, salt)
        finishedPassword = formatting.formatAsCustom(encryptedPassword, passwordLength, symbols, numbers, uppercase, lowercase)

        print("finished:")
        print(finishedPassword)
        print(len(finishedPassword))

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.sendPassword(finishedPassword)

        self.checkDatabase(username, website, counter, passwordLength, symbols, uppercase, lowercase, numbers)

        return

    def checkDatabase(self, username, website, counter, passwordLength, symbols, uppercase, lowercase, numbers):
        db = usersDB.Users()
        result = db.getUserByUsername(username)
        needToAdd = True
        for r in result:
            if (r["username"] == username) and (r["website"] == website) and (r["count"] == counter) and (r["length"] == passwordLength) and (r["symbols"] == symbols) and (r["uppercase"] == uppercase) and (r["lowercase"] == lowercase) and (r["numbers"] == numbers):
                needToAdd = False
        if needToAdd:
            db.addUser(username, website, counter, passwordLength, symbols, uppercase, lowercase, numbers)
            print("Added user")
        return

    def retrieveCollection(self):
        print("retrieving Collection")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        db = usersDB.Users()
        allSpecifications = db.getAllUsers()

        print("sending collection")

        self.wfile.write(bytes(json.dumps(allSpecifications), "utf-8"))
        print(allSpecifications)
        return



    # def checkRegistrations(self):
    #     print(self.headers)
    #     length = int(self.headers["Content-Length"])
    #     body = self.rfile.read(length).decode("utf-8")
    #     print("Body:", body)
    #     parsedBody = parse_qs(body)
    #     print("Parsed Body:", parsedBody)
    #     username = parsedBody["username"][0]
    #     password = parsedBody["password"][0]
    #     firstName = parsedBody["firstName"][0]
    #     lastName = parsedBody["lastName"][0]
        
    #     db = characters_db.Users()
    #     Uid = db.getUserByUsername(username)
    #     if Uid == None:
    #         password = bcrypt.hash(password)
    #         db.addUser(username, password, firstName, lastName)
    #         self.send_response(201)
    #         self.end_headers()
    #         print("Uid:", Uid)
    #         self.session["userId"] = Uid["id"]
    #         #might want to change previous line to:
    #         #self.session["userId"] = db.getUserByUsername(username)["id"]
    #     else:
    #         self.send422()

    #     #need help to figure out how to register:
    #     return

    # def checkLogins(self):
    #     print(self.headers)
    #     length = int(self.headers["Content-Length"])
    #     body = self.rfile.read(length).decode("utf-8")
    #     print("Body:", body)
    #     parsedBody = parse_qs(body)
    #     print("Parsed Body:", parsedBody)
    #     username = parsedBody["username"][0]
    #     password = parsedBody["password"][0]
    #     db = characters_db.Users()
    #     user = db.getUserByUsername(username)
    #     if user != None:
    #         print("User:", user)
    #         hashed = user["password"]
    #         if bcrypt.verify(password, hashed):
    #             self.send_response(201)
    #             self.end_headers()
    #             print("Uid:", user)
    #             self.session["userId"] = user["id"]
    #         else:
    #             self.send401()
    #     else:
    #         self.send401()
    #     return

    def end_headers(self):
        # self.send_cookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)
        return

    #stuff that already works:


    def send404(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("Not Found", "utf-8"))
        return
    
    def send401(self):
        self.send_response(401)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not logged in", "utf-8"))

        return

    def send422(self):
        self.send_response(422)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Email exists", "utf-8"))
        return



def run():
    db = usersDB.Users()
    db.createTable()
    db = None # disconnect

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)

    print("Server listening on", "{}:{}".format(*listen))
    server.serve_forever()

run()
