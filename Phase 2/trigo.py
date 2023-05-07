from flask import Flask,render_template,request

app = Flask(__name__,template_folder="template",static_folder="css")

list=[]

@app.route('/',methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/add',methods=["POST"])
def add():
    if request.method=="POST":
        contract=request.form.get("Contract")
        contractRev=request.form.get("ContractRev")
        wiRev=request.form.get("WIRev")
        contract=contract+'.'+contractRev+'.'+wiRev
        if contract not in list:
            list.append(contract)
    return render_template("index.html",list=list)

@app.route('/delete',methods=["POST"])
def delete():
    if request.method == 'POST':
        conValue=request.form.get('name')
        print(conValue)
        if conValue in list:
            list.remove(conValue)        
    return render_template("index.html",list=list)

if __name__ == "main":
    app.run()