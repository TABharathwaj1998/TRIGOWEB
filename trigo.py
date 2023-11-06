from flask import Flask,render_template,request,redirect
from pymongo import MongoClient
from crudpymongo import collection

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
         
        for doc in collection.find({"Contract Number":contract},{"_id":0}):
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
    if request.method=="POST":
        partNumber=request.form.get("PartNo")
        flag = 0
        for document in range(len(list)):
            ls = list[document]
            for x, y in ls.items():
                if partNumber in ls[x]:
                    print("Part Number ",partNumber, " present in Contract ",x)
                    flag = 1
            if flag == 1:
                break
        
        if flag == 0:
            String="Part Number not in Contract"
            return render_template("errors.html", String=String,contractList=contractList)
        else:
            return render_template("serial.html",partNumber=partNumber,contractList=contractList)

@app.route("/serialNo",methods=["POST","GET"])
def serial():
    if request.method == "POST":
        partNumber=request.form.get("PartNo")
        flag = 0
        for document in range(len(list)):
            ls = list[document]
            for x, y in ls.items():
                if partNumber in ls[x]:
                    print("Part Number ",partNumber, " present in Contract ",x)
                    flag = 1
            if flag == 1:
                break
        
        if flag == 0:
            String="Part Number not in Contract"
            return render_template("errors.html", String=String,contractList=contractList)
        else:
            serialNo = request.form.get("SerialNo")
            quantity = request.form.get("Qnty")
            certified = request.form.get("Crtfd")
            print("Serial, Quantity and Certified: ",serialNo,quantity,certified)
            return render_template("serial.html",partNumber=partNumber,contractList=contractList)
        
if __name__ == "main":
    app.run()