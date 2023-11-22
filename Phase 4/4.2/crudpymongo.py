from flask import Flask, redirect, render_template, request
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["TRIGO"]
collection1 = db["Contract list"]
collection2 = db["Defects list"]

app = Flask(__name__, template_folder="template")

@app.route("/enter", methods=["POST","GET"])
def enter():
    return render_template("CRUD.html")

@app.route("/create", methods=["POST","GET"])
def create():
    if request.method=="POST":
        contract = request.form.get("ContractInsert")
        contractRev=request.form.get("ContractRev")
        wiRev=request.form.get("WIRev")
        contractNo=contract+"."+contractRev+"."+wiRev
        partNos = request.form.get("PartInsert")
        defect = request.form.get("defects")
        defectDscrptn = request.form.get("defectDescription")
        doc = {"Contract Number":contractNo,"Part Numbers":[partNos,]}
        collection1.insert_one(doc)
        if defect != "" and defectDscrptn != "":
            doc = {"Contract Number":contractNo,"Defects":[defect,],"Description":[defectDscrptn,]}
            collection2.insert_one(doc)
        return redirect("/read")

@app.route("/read")
def read():    
    docValues = {}
    for doc in collection1.find({},{"_id":0}):
        docValues = {doc["Contract Number"]:doc["Part Numbers"]}
    print(docValues)
    return docValues

@app.route("/updatePart", methods=["POST","GET"])
def updatePart():
    if request.method=="POST":
        contractNo = request.form.get("Contract")
        updatedpartNo = request.form.get("UpdatedPart")
        collection1.update_one({"Contract Number":contractNo}, {'$addToSet':{"Part Numbers":updatedpartNo}})
        return redirect("/read")
    
@app.route("/updateDefect", methods=["POST","GET"])
def updateDefect():
    if request.method=="POST":
        contractNo = request.form.get("Contract")
        updatedDefect = request.form.get("UpdatedDefect")
        defectDscrptn = request.form.get("defectDescription")
        collection2.update_one({"Contract Number":contractNo}, {'$addToSet':{"Defects":updatedDefect}})
        collection2.update_one({"Contract Number":contractNo}, {'$addToSet':{"Description":defectDscrptn}})
        return "Updated defects"

@app.route("/delete", methods=["POST","GET"])
def delete():
    if request.method=="POST":
        option = request.form.getlist("options")
        contractNo = request.form.get("Contract")
        partNo = request.form.get("Part")
        
        if option == ["PartNo"]:
            collection1.update_one({"Contract Number":contractNo},{'$pull':{"Part Numbers":partNo}})
        elif option == ["ContractNo"]:
            collection1.delete_one({"Contract Number":contractNo})
        elif option == ["Collection"]:
            collection1.drop()
            collection2.drop()
        return redirect("/read")

if __name__=="main":
    app.run(host="localhost",debug=True)