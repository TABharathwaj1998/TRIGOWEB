from flask import Flask, redirect, render_template, request
import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["TRIGO"]
collection = db["Contract list"]

app = Flask(__name__, template_folder="template")

@app.route('/enter', methods=["POST","GET"])
def enter():
    return render_template("CRUD.html")

@app.route('/create', methods=["POST","GET"])
def create():
    if request.method=="POST":
        contractNo = request.form.get("ContractInsert")
        partNos = request.form.get("PartInsert")
        doc = {"Contract Number":contractNo,"Part Numbers":[partNos,]}
        collection.insert_one(doc)
        return redirect('/read')

@app.route('/read')
def read():    
    docValues = {} 
    for doc in collection.find({},{"_id":0}):
        docValues = {doc["Contract Number"]:doc["Part Numbers"]}
    print(docValues)
    return docValues

@app.route('/update', methods=["POST","GET"])
def update():
    if request.method=="POST":
        contractNo = request.form.get("Contract")
        updatedpartNo = request.form.get("UpdatedPart")
        collection.update_one({"Contract Number":contractNo}, {'$addToSet':{"Part Numbers":updatedpartNo}})
        return redirect('/read')

@app.route('/delete', methods=["POST","GET"])
def delete():
    if request.method=="POST":
        option = request.form.getlist('options')
        contractNo = request.form.get("Contract")
        partNo = request.form.get("Part")
        
        if option == ["PartNo"]:
            collection.update_one({"Contract Number":contractNo},{'$pull':{"Part Numbers":partNo}})
        elif option == ["ContractNo"]:
            collection.delete_one({"Contract Number":contractNo})
        elif option == ['Collection']:
            collection.drop()
        return redirect('/read')

if __name__=="main":
    app.run(host="localhost",debug=True)