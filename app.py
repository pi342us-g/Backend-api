#signup form
from flask import *
import pymysql
import pymysql.cursors
import os
app=Flask(__name__)

app.config['UPLOAD_FOLDER']='static/images'

@app.route("/api/signup",methods=['POST'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        phone=request.form['phone']

        #connect to database
        connection=pymysql.connect(host='localhost',user='root',password='',database='ORYXSHOPBACKEND')

        cursor= connection.cursor()


        #do an insert
        cursor.execute('INSERT INTO users(username,email,password,phone)VALUES(%s,%s,%s,%s)',(username,email,password,phone))


        connection.commit()

        return jsonify({"success":"successfully created an account"})

#signin form

@app.route("/api/signin",methods=['POST'])
def signin():
    if request.method =='POST':
        email=request.form['email']

        password=request.form['password']

        #connect to database
        connection=pymysql.connect(host='localhost',user=('root'),password='',database=('ORYXSHOPBACKEND'))

        cursor=connection.cursor(pymysql.cursors.DictCursor)
        sql='SELECT * FROM users WHERE email= %s AND password= %s'
        data=(email,password)

        cursor.execute(sql,data) 


        count=cursor.rowcount

        if count== 0:
            return jsonify({"message":"Login failed."})
        else:
            if count >=2:
               user=cursor.fetchall()
               return jsonify({"accounts":user})
            user=cursor.fetchone()   
            return jsonify({"message":"Login success","user":user})
          
#add product form

@app.route("/api/add_product",methods=['POST'])
def add_product():
    if request.method=='POST':
        product_name=request.form['product_name']
        product_description=request.form['product_description']
        product_cost=request.form['product_cost']

        #extracting the image data
        product_photo=request.files['product_photo']

        filename= product_photo.filename

        #specify where image will be saved
        photo_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)

        product_photo.save(photo_path)

        #connect to our database
        connection=pymysql.connect(host='localhost',user='root',password='',database='ORYXSHOPBACKEND')

        #prepare to execute insert query
        cursor=connection.cursor(pymysql.cursors.DictCursor)

        sql='INSERT INTO product_details(product_name,product_description,product_cost,product_photo)VALUES(%s,%s,%s,%s)'
        data=(product_name,product_description,product_cost,filename)
        cursor.execute(sql,data)

        connection.commit()
        return jsonify({"message":"added product successfully"})

#get product details

@app.route("/api/get_products_details",methods=['GET'])
def get_product_details():
    if request.method =='GET':

        #connect to database
        connection=pymysql.connect(host='localhost',user='root',password='',database='ORYXSHOPBACKEND')

        cursor=connection.cursor(pymysql.cursors.DictCursor)

        sql='SELECT * FROM product_details'
        cursor.execute(sql)

        products =cursor.fetchall()
        return jsonify({"products":products})
# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret 
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
        # Create a POST Request to above url, providing headers, payload 
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) # 
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})
	 


app.run(debug=True)