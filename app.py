from flask import Flask, request, render_template, render_template_string, redirect, session
import sqlite3, os

app=Flask(__name__)
app.secret_key="dev-only-secret"
DB="shop.db"

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    c=db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT);
    CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT, image TEXT, description TEXT, stock INTEGER);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, username TEXT, total REAL, status TEXT);
    """)
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        c.executemany("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                      [("student","labpass","customer"),("admin","admin123","admin")])
    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
        c.executemany("""INSERT INTO products(name,price,category,image,description,stock)
                        VALUES(?,?,?,?,?,?)""",[
            ("Cyber Hoodie",1499,"Fashion","🧥","Premium dark hoodie",15),
            ("Dev Keyboard",2499,"Electronics","⌨️","Mechanical RGB keyboard",8),
            ("Security Mug",499,"Lifestyle","☕","Pentester coffee mug",30),
            ("USB-C Hub",1799,"Electronics","🔌","7-in-1 development hub",12),
            ("Laptop Stand",1299,"Accessories","💻","Aluminium ergonomic stand",20),
            ("Code Cap",699,"Fashion","🧢","Minimal developer cap",25)
        ])
    c.commit(); c.close()

@app.context_processor
def inject():
    return {"cart_count":len(session.get("cart",[]))}

@app.route("/")
def home():
    c=db(); products=c.execute("SELECT * FROM products").fetchall(); c.close()
    return render_template("index.html",products=products)

@app.route("/products")
def products():
    category=request.args.get("category","")
    c=db()
    if category:
        rows=c.execute("SELECT * FROM products WHERE category=?",(category,)).fetchall()
    else: rows=c.execute("SELECT * FROM products").fetchall()
    cats=c.execute("SELECT DISTINCT category FROM products").fetchall(); c.close()
    return render_template("products.html",products=rows,categories=cats,selected=category)

@app.route("/product/<int:pid>")
def product(pid):
    c=db(); p=c.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone(); c.close()
    return render_template("product.html",p=p)

# INTENTIONAL SQLi lab endpoint
@app.route("/search")
def search():
    q=request.args.get("q",""); c=db()
    sql="SELECT * FROM products WHERE name LIKE '%"+q+"%' OR category LIKE '%"+q+"%'"
    rows=c.execute(sql).fetchall(); c.close()
    return render_template("search.html",products=rows,q=q)

@app.route("/cart/add/<int:pid>")
def add(pid):
    cart=session.get("cart",[]); cart.append(pid); session["cart"]=cart
    return redirect(request.referrer or "/products")

@app.route("/cart")
def cart():
    ids=session.get("cart",[]); c=db()
    products=[]
    for pid in ids:
        p=c.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone()
        if p: products.append(p)
    c.close(); total=sum(p["price"] for p in products)
    return render_template("cart.html",products=products,total=total)

@app.route("/checkout",methods=["GET","POST"])
def checkout():
    if not session.get("user"): return redirect("/login")
    ids=session.get("cart",[]); c=db()
    products=[c.execute("SELECT * FROM products WHERE id=?",(x,)).fetchone() for x in ids]
    products=[p for p in products if p]; total=sum(p["price"] for p in products)
    msg=""
    if request.method=="POST" and products:
        c.execute("INSERT INTO orders(username,total,status) VALUES(?,?,?)",
                  (session["user"],total,"Processing")); c.commit()
        session["cart"]=[]; msg="Order placed successfully!"
    c.close(); return render_template("checkout.html",products=products,total=total,msg=msg)

@app.route("/login",methods=["GET","POST"])
def login():
    msg=""
    if request.method=="POST":
        u=request.form.get("username",""); pw=request.form.get("password","")
        c=db(); row=c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,pw)).fetchone(); c.close()
        if row: session["user"]=row["username"]; session["role"]=row["role"]; return redirect("/")
        msg="Invalid credentials"
    return render_template("login.html",msg=msg)

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

# INTENTIONAL REFLECTED XSS lab endpoint
@app.route("/review")
def review():
    name=request.args.get("name","Guest"); comment=request.args.get("comment","")
    return render_template_string("<h2>Review Preview</h2><p>Reviewer: %s</p><p>Comment: %s</p><p><a href='/'>Back</a></p>"%(name,comment))

# INTENTIONAL FILE-INCLUSION-STYLE flaw, restricted to project pages directory.
@app.route("/page")
def page():
    name=request.args.get("name","about.html")
    try:
        with open(os.path.join("pages",name),encoding="utf8") as f: content=f.read()
        return render_template_string(content)
    except Exception as e: return "Page error: "+str(e),404

@app.route("/admin")
def admin():
    if session.get("role")!="admin": return "Admin access required",403
    c=db(); orders=c.execute("SELECT * FROM orders ORDER BY id DESC").fetchall(); c.close()
    return render_template("admin.html",orders=orders)

@app.route("/vulnerabilities")
def vulnerabilities(): return render_template("vulnerabilities.html")

if __name__=="__main__":
    init_db(); app.run(host="127.0.0.1",port=5000,debug=True)
