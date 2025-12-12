try:
    from flask import Flask,request,jsonify,redirect,render_template
    import mysql.connector
    import hashlib
    import base64
except ImportError as e:
    print(f"❌ Import error: {e}")

app=Flask(__name__)

DB_CONFIG = {
    'host':'localhost',
    'user':'root',
    'password':'Roja@0982',
    'database':'test',
    'port':3306
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def generate_short_url(long_url):
    hash_object=hashlib.sha256(long_url.encode())
    short_hash=base64.urlsafe_b64encode(hash_object.digest())[:6].decode()
    return short_hash

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/shorten',methods=['POST'])
def shorten_url():
    url=request.form.get('url')
    if not url:
        return "Invalid URL", 400
    
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)  # Fixed typo
    cursor.execute("SELECT short_url from url_mapping where long_url=%s",(url,))
    existing_entry=cursor.fetchone()
    if existing_entry:
        conn.close()
        return f"Shortened URL: <a href='{request.host_url}{existing_entry['short_url']}'>{request.host_url}{existing_entry['short_url']}</a>"

    short_url=generate_short_url(url)
    cursor.execute("INSERT into url_mapping (long_url,short_url) VALUES(%s,%s)",(url,short_url))  # Fixed SQL
    conn.commit()
    conn.close()
    return f"Shortened URL: <a href='{request.host_url}{short_url}'>{request.host_url}{short_url}</a>"  # Fixed variable

@app.route('/<short_url>')  # Fixed route parameter
def redirect_url(short_url):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT long_url from url_mapping where short_url=%s",(short_url,))
    entry=cursor.fetchone()
    if entry:
        cursor.execute("UPDATE url_mapping set clicks=clicks+1 where short_url=%s",(short_url,))
        conn.commit()  # Fixed commit object
        conn.close()
        return redirect(entry['long_url'])
    conn.close()
    return "Error, URL not found",404

if __name__=='__main__':
    app.run(debug=True)

