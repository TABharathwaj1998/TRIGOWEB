from flask import Flask,render_template,request,redirect,json
from pymongo import MongoClient
from crudpymongo import collection1,collection2
import psycopg2
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from werkzeug.utils import secure_filename
import os
from PIL import Image
import base64
from io import BytesIO 

app = Flask(__name__,template_folder="template",static_folder="css")

list=[]
contractList = []
defects = []
defect_descriptions = []
contractPartValues = {}
selectedContract = ""
dfct = "" 
rwrk = ""
prt_No = 0
x = ""
y = ""

number_of_images = 0
UPLOAD_FOLDER = "C:/Users/tabha/Documents/Python/trigoWeb"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient("mongodb://localhost:27017")
print(client)
conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="postgres", password="xxxx")
cur = conn.cursor()

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
    global selectedContract
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
            selectedContract = doc["Contract Number"]
            if len(defects) != 0 and len(defect_descriptions) != 0:
                defects.clear()
                defect_descriptions.clear()
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
    global selectedContract,prt_No
    if request.method == "POST":
        partNumber=request.form.get("PartNo")
        prt_No = partNumber
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
            selectedContract = doc["Contract Number"]
            print("SELECTED CONTRACT: ",selectedContract)
            if len(defects) != 0 and len(defect_descriptions) != 0:
                defects.clear()
                defect_descriptions.clear()
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
            return render_template("defects.html",partNumber=partNumber,serialNo=serialNo,quantity=quantity,certified=certified,contractList=contractList,defects=json.dumps(defects),defect_descriptions=json.dumps(defect_descriptions))

@app.route("/rjctAndRwrk",methods=["POST","GET"])
def rjctAndRwrk():
    global selectedContract, dfct, rwrk
    noOfRejects = 0
    noOfReworks = 0
    if request.method == "POST":
        noOfInspected = request.form.get("Insp")
        for defect in collection2.find({"Contract Number":selectedContract},{"_id":0}):
            for d in defect["Defects"]:
                dfct = d+"d"
                rwrk = d+"r"
                reject = request.form.get(dfct)
                rework = request.form.get(rwrk)
                noOfRejects = int(noOfRejects) + int(reject)
                noOfReworks = int(noOfReworks) + int(rework)
        OKForLine = int(noOfInspected) - int(noOfRejects)
        return render_template("finalData.html",noOfInspected=noOfInspected,noOfRejects=noOfRejects,noOfReworks=noOfReworks,OKForLine=OKForLine,contractList=contractList,defects=json.dumps(defects),defect_descriptions=json.dumps(defect_descriptions))

@app.route("/final",methods=["POST"])
def final():
    global prt_No, number_of_images, x, y
    if request.method == "POST":
        inspectedNo = request.form.get("Insp")
        rejectedNo = request.form.get("Rejectvalue")
        reworkNo = request.form.get("Reworkedvalue")
        note = request.form.get("note")
        
        
        try:
            data = request.get_json()
            for i,j in data.items():
                print("DATA",i,": ",j)
                j = j[j.index(',')+1:]
                bytes_decoded = base64.b64decode(j)
                img=Image.open(BytesIO(bytes_decoded))
                out_jpg=img.convert('RGB')
                number_of_images += 1
                filename = "uploadedImages"+str(number_of_images)+".jpg"
                out_jpg.save(filename)
            
            
        except:
            print("json load not working")
        
        
        
        
        
        '''

        

        account_url = "https://tabsamplestorage.blob.core.windows.net"
        default_credential = "Ti4CfXXg/C274mrvnCl0ICnQsqSqokiHitO+lXgjg6oR3fssKlgirQ96wUXX7NHW2OSOkf7vl9hG+AStNqk6DA=="

        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)

        container_client = blob_service_client.get_container_client(container="trigoimg")

        if container_client.exists():
            print("Container Exists")
        else:
            print("Not Exists")
            container_client.create_container()

        for f in (files):
            filename = "trigoSample"+str(number_of_images)+".jpg"
            print(filename)
            #file = secure_filename(f.filename)
            blob_client = container_client.upload_blob(name=filename,data=f,overwrite=True)
            number_of_images += 1

            blob = blob_service_client.get_blob_client(container="trigoimg", blob=filename)
            with open(file=os.path.join(UPLOAD_FOLDER, filename), mode="wb") as sample_blob:
                download_stream = blob_client.download_blob()
                sample_blob.write(download_stream.readall())'''


        #print(prt_No,inspectedNo,rejectedNo,reworkNo,note)
        return render_template("parts.html",contractList=contractList)

if __name__ == "main":
    app.run()
