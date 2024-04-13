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
from datetime import datetime, timezone, date
import pytz

app = Flask(__name__,template_folder="template",static_folder="css")

list=[]
contractList = []
defects = []
defect_descriptions = []
contractPartValues = {}
selectedContract = ""
dfct = "" 
rwrk = ""
part_Number = 0
serial_Number = 0
quantity = 0
certified = 0
no_of_inspected = 0
no_of_rejected = 0
rejected = 0
no_of_reworks = 0
reworked = 0
note = ""
flag = 0
img_url = []

number_of_images = 0
UPLOAD_FOLDER = "C:/Users/tabha/Documents/Python/trigoWeb"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient("mongodb://localhost:27017")
print(client)
conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="postgres", password="*****")
cur = conn.cursor()
account_url = "https://trgoimgs.blob.core.windows.net"
default_credential = "*****************************************************************************"

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
    global selectedContract, part_Number
    if request.method=="POST":
        part_Number=request.form.get("PartNo")
        flag = 0
        for document in range(len(list)):
            ls = list[document]
            for x, y in ls.items():
                if part_Number in ls[x]:
                    flag = 1
            if flag == 1:
                break
        
        for doc in collection1.find({"Part Numbers":part_Number},{"_id":0}):
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
            return render_template("serial.html",partNumber=part_Number,contractList=contractList)

@app.route("/serialNo",methods=["POST","GET"])
def serial():
    global selectedContract,part_Number, serial_Number, quantity, certified
    if request.method == "POST":
        part_Number=request.form.get("PartNo")
        flag = 0
        for document in range(len(list)):
            ls = list[document]
            for x, y in ls.items():
                if part_Number in ls[x]:
                    flag = 1
            if flag == 1:
                break
        
        for doc in collection1.find({"Part Numbers":part_Number},{"_id":0}):
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
            serial_Number = request.form.get("SerialNo")
            quantity = request.form.get("Qnty")
            certified = request.form.get("Crtfd")
            return render_template("finalData.html",contractList=contractList,partNumber=part_Number,serialNo=serial_Number,quantity=quantity,certified=certified,defects=json.dumps(defects),defect_descriptions=json.dumps(defect_descriptions))

@app.route("/final",methods=["POST"])
def final():
    global selectedContract, dfct, rwrk, part_Number, serial_Number, quantity, certified, number_of_images, no_of_inspected, no_of_rejected, no_of_reworks, note, flag
    rejects = []
    reworks = []
    if request.method == "POST":
        no_of_inspected = request.form.get("Insp")
        no_of_rejected = request.form.get("Rejectvalue")
        no_of_reworks = request.form.get("Reworkedvalue")
        note = request.form.get("note")

        for defect in collection2.find({"Contract Number":selectedContract},{"_id":0}):
            for d in defect["Defects"]:
                dfct = d+"d"
                rwrk = d+"r"
                reject = request.form.get(dfct)
                rework = request.form.get(rwrk)
                print(reject,rework)
                




        time = datetime.now(pytz.utc)
        #fetch the timezone information
        est = pytz.timezone('US/Eastern')

        #convert utc to est
        est_time = time.astimezone(est)

        current_date = date.today()
        current_time = str(est_time.hour) + ":" + str(est_time.minute)
        
        try:
            data = request.get_json()
            for i,j in data.items():
                img_url.append(j)
                datum = j[j.index(',')+1:]
                bytes_decoded = base64.b64decode(datum)
                img=Image.open(BytesIO(bytes_decoded))
                out_jpg=img.convert('RGB')
                number_of_images += 1
                filename = str(selectedContract)+str(part_Number)+str(serial_Number)+str(number_of_images)+".jpg"
                out_jpg.save(filename)
                
        except:
            print("json load not working")

        no = 0

        for image in img_url:
            no += 1
            

            azureFile = str(selectedContract)+str(part_Number)+str(serial_Number)+str(no)+".txt"
            print(azureFile)

            container_name = str(current_date)
            # Create the BlobServiceClient object
            blob_service_client = BlobServiceClient(account_url, credential=default_credential)
            container_client = blob_service_client.get_container_client(container=container_name)
            try:
                print("Not Exists")
                container_client.create_container()
            except:
                print("Container Exists")
            blob_client = container_client.upload_blob(name=azureFile,data=image,overwrite=True)

        
        print(selectedContract, part_Number, serial_Number, quantity, certified, no_of_inspected, no_of_rejected, no_of_reworks, note)
        

        if flag == 1 and no_of_inspected != None:
            print("flag before in if: ",flag)
            create_table = "CREATE TABLE IF NOT EXISTS "+str(selectedContract.split(".")[0])+"(part_number INTEGER, serial_number INTEGER, Quantity INTEGER, CERTIFIED VARCHAR(1), Inspected INTEGER, Rejected INTEGER, Reworked INTEGER, Note VARCHAR(255));"
            cur.execute(create_table)
            cur.execute("INSERT INTO "+str(selectedContract.split(".")[0])+"(part_number, serial_number, Quantity, CERTIFIED, Inspected, Rejected, Reworked, Note) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);",(part_Number, serial_Number, quantity, certified, no_of_inspected, no_of_rejected, no_of_reworks, note))
            conn.commit()
            flag *= 0
            print("flag after in if: ",flag)
        else:
            print("flag before in else: ",flag)
            flag += 1
            print("flag after in else: ",flag)
        
        img_url.clear()

        return render_template("parts.html",contractList=contractList)

if __name__ == "main":
    app.run()