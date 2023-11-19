from flask import Flask,render_template,request,redirect
from pymongo import MongoClient
from crudpymongo import collection1,collection2

app = Flask(__name__,template_folder="template",static_folder="css")

list=[]
contractList = []
contractPartValues = {}

client = MongoClient("mongodb://localhost:27017")
print(client)

@app.route("/",methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/add",methods=["POST","GET"])
def add():
    if request.method=="POST":
        contract=request.form.get("Contract")
        contractRev=request.form.get("ContractRev")
        wiRev=request.form.get("WIRev")
        flag = 0
        contract=contract+"."+contractRev+"."+wiRev
         
        for doc in collection1.find({"Contract Number":contract},{"_id":0}):
            contractPartValues = {doc["Contract Number"]:doc["Part Numbers"]}
            if (contract not in list) and (contract in doc["Contract Number"]):
                list.append(contractPartValues)
                contractList.append(contract)
                print(list)
                flag += 1 
        if flag == 1:
            return render_template("parts.html",contractList=contractList)
        else:
            String="Contract not in list"
            return render_template("errors.html", String=String,contractList=contractList)

@app.route("/delete",methods=["POST","GET"])
def delete():
    if request.method == "POST":
        conValue=request.form.get("name")
        print("Value to delete: ", conValue)
        print("List of values are: ")
        dictList=0
        while (dictList < len(list)):
            if conValue in list[dictList]:
                del list[dictList][conValue]
                contractList.remove(conValue)
            else:
                print(list[dictList])
            dictList+=1        
        return render_template("parts.html",contractList=contractList)

@app.route("/partNo",methods=["POST","GET"])
def partNo():
    defects = []
    defect_descriptions = []
    if request.method=="POST":
        partNumber=request.form.get("PartNo")
        flag = 0
        for document in range(len(list)):
            ls = list[document]
            for x, y in ls.items():
                if partNumber in ls[x]:
                    flag = 1
            if flag == 1:
                break
        
        for doc in collection1.find({"Part Numbers":partNumber},{"_id":0}):
            print("Part Number ",doc["Part Numbers"], " present in Contract ",doc["Contract Number"])
            if len(defects) != 0 and len(defect_descriptions) != 0:
                del defects
                del defect_descriptions
            for defect in collection2.find({"Contract Number":doc["Contract Number"]},{"_id":0}):
                for dfct in defect["Defects"]:
                    defects.append(dfct)
                for desc in defect["Description"]:
                    defect_descriptions.append(desc)
        
        print("DEFECTS LIST: ",defects)
        print("DESCRIPTION LIST: ",defect_descriptions)

        if flag == 0:
            String="Part Number not in Contract"
            return render_template("errors.html", String=String,contractList=contractList)
        else:
            return render_template("serial.html",partNumber=partNumber,contractList=contractList)

@app.route("/serialNo",methods=["POST","GET"])
def serial():
    defects = []
    defect_descriptions = []
    if request.method == "POST":
        partNumber=request.form.get("PartNo")
        flag = 0
        for document in range(len(list)):
            ls = list[document]
            for x, y in ls.items():
                if partNumber in ls[x]:
                    flag = 1
            if flag == 1:
                break
        
        for doc in collection1.find({"Part Numbers":partNumber},{"_id":0}):
            print("Part Number ",doc["Part Numbers"], " present in Contract ",doc["Contract Number"])
            if len(defects) != 0 and len(defect_descriptions) != 0:
                del defects
                del defect_descriptions
            for defect in collection2.find({"Contract Number":doc["Contract Number"]},{"_id":0}):
                for dfct in defect["Defects"]:
                    defects.append(dfct)
                for desc in defect["Description"]:
                    defect_descriptions.append(desc)
        
        print("DEFECTS LIST: ",defects)
        print("DESCRIPTION LIST: ",defect_descriptions)

        if flag == 0:
            String="Part Number not in Contract"
            return render_template("errors.html", String=String,contractList=contractList)
        else:
            serialNo = request.form.get("SerialNo")
            quantity = request.form.get("Qnty")
            certified = request.form.get("Crtfd")
            print("Serial, Quantity and Certified: ",serialNo,quantity,certified)
            return render_template("defects.html",partNumber=partNumber,serialNo=serialNo,quantity=quantity,certified=certified,contractList=contractList,defects=defects,defect_descriptions=defect_descriptions)
        
if __name__ == "main":
    app.run()