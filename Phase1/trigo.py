from flask import Flask,render_template,request

app = Flask(__name__,template_folder="template",static_folder="css")

list=[]

@app.route('/',methods=["GET"])
def home():
    return render_template("index.html")

@app.route('/add',methods=["GET","POST"])
def add():
    if request.method=="POST":
        contract=request.form.get("Contract")
        list.append(contract)
        return render_template("index.html",length=len(list),list=list)

if __name__ == "main":
    app.run()