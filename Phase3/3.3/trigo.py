from flask import Flask,render_template,request
from pymongo import MongoClient
from crudpymongo import collection

app = Flask(__name__,template_folder="template",static_folder="css")

list=[]

client = MongoClient("mongodb://localhost:27017")
print(client)

@app.route('/',methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/add',methods=["POST","GET"])
def add():
    if request.method=="POST":
        contract=request.form.get("Contract")
        contractRev=request.form.get("ContractRev")
        wiRev=request.form.get("WIRev")
        contract=contract+'.'+contractRev+'.'+wiRev
        if contract not in list:
            list.append(contract)
    return render_template("parts.html",list=list)

@app.route('/delete',methods=["POST","GET"])
def delete():
    if request.method == 'POST':
        conValue=request.form.get('name')
        print(conValue)
        if conValue in list:
            list.remove(conValue)        
    return render_template("parts.html",list=list)

@app.route('/partNo',methods=["POST","GET"])
def partNo():
    if request.method=="POST":
        docValues = {}
        for doc in collection.find({},{"_id":0}):
            docValues = {doc["Contract Number"]:doc["Part Numbers"]}
        print(docValues)
        partNumber=request.form.get('partNumber')
        print(partNumber)
        return render_template("parts.html",partNumber=partNumber)

if __name__ == "main":
    app.run()