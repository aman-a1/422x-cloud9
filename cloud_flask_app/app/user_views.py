from app import app
from flask import render_template, request, redirect, Response
from werkzeug.utils import secure_filename
import boto3
from boto3.dynamodb.conditions import Key
from os import environ
import time

# UPLOAD_FOLDER = "uploads"
BUCKET = str(environ.get('S3_BUCKET'))
S3_SECRET = environ.get('S3_SECRET')
S3_KEY = environ.get('S3_KEY')
contents = None

@app.route("/")
def user_dashboard():
    # show_image retrieves a list of temporary, public image urls
    # contents = show_image(BUCKET)
    global contents
    # contents = get_bucket_files(environ.get('USERNAME'))
    return render_template("public/index.html")

@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        resource = boto3.resource('s3')
        bucket = resource.Bucket(BUCKET)
        bucket.Object(f.filename).put(Body=f)
        # add to dynamodb
        dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
        table = dynamodb.Table('Images')
        ImageObj = {
            "ImageName": f.filename,
            "UserName": environ.get('USERNAME')
        }
        table.put_item(Item=ImageObj)
    return redirect("/user/dashboard")

@app.route("/download", methods=['POST'])
def download():
    obj_key = request.form['key']
    resource = boto3.resource('s3')
    bucket = resource.Bucket(BUCKET)
    file_obj = bucket.Object(obj_key).get()

    resp = Response(file_obj['Body'].read())
    resp.headers['Content-Disposition'] = 'attachment;filename=' + format(obj_key)
    resp.mimetype = 'text/plain'

    return resp

@app.route('/search', methods=['GET'])
def search():
    file_name = request.args.get("search")
    resource = boto3.resource('s3')
    bucket = resource.Bucket(BUCKET)
    # object_list = bucket.objects.filter(Prefix=file_name)
    object_list = []
    global contents
    for word in contents:
        if(file_name in word.key):
            object_list.append(word)

    return render_template('/', contents=object_list)

def show_image(bucket):
    s3_client = boto3.client('s3')
    # public_urls = []
    files = []
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            # presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
            # tuple = (presigned_url, item['Key'])
            # public_urls.append(tuple)
            # print(tuple)
            files.append(item['Key'])

    except Exception as e:
        print(e)
        pass
    return files

def upload_file(file_name, bucket):
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response

def get_bucket_files(username):
    resource = boto3.resource('s3')
    bucket = resource.Bucket(BUCKET)
    allImages = bucket.objects.all()
    toRet = []
    dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
    table = dynamodb.Table('Images')
    userImages = table.query(KeyConditionExpression=Key('UserName').eq(username))

    for i in userImages['Items']:
        for image in allImages:
            print(i['ImageName'])
            if(i['ImageName'] == image.key):
                toRet.append(image)

    return toRet

@app.route('/user/AddForSale', methods=['GET', 'POST'])
def addForSale():
    print("Request Method: " + request.method)
    if request.method == 'POST':
        make = request.form['make']
        category = request.form['category']
        manu = request.form['manu']
        descrip = request.form['descrip']
        price = request.form['price']
        color = request.form['color']
        miles = request.form['miles']
        year = request.form['year']
        condition = request.form['condition']
        phone = request.form['phone']
        city = request.form['city']

        dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
        table = dynamodb.Table('ForSale')
        dTable = {
            "itemCode": time.time_ns(),
            "category": category,
            "City": city,
            "Color": color,
            "Condition": condition,
            "Manufacturer": manu,
            "Make": make,
            "Miles": miles,
            "PhoneNumber": phone,
            "Description": descrip,
            "Price": price,
            "Year": year,
        }
        print(dTable)
        table.put_item(Item=dTable)
        return redirect("/user/dashboard")

    return render_template("user/AddForSale.html")

@app.route('/ForSale', methods=['GET', 'POST'])
def get_items():
    category = request.form['category']
    dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
    table = dynamodb.Table('Users')
    response =table.query()
    contents = []
    for i in response['items']:
        if category == (i['category']):
            contents.append(i)
    return render_template('public/ListView.html', contents)

@app.route('/user/AddCommunity', methods=['GET', 'POST'])
def addCommunity():
    print("Request Method: " + request.method)
    if request.method == 'POST':
        dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
        table = dynamodb.Table('Community')
        dTable = {
            "itemCode": time.time_ns(),
            "category": request.form['category'],
            "description": request.form['description'],
            "location": request.form['location'],
            "time": request.form['time'],
            "requirements": request.form['requirements'],
            "PhoneNumber": request.form['phone']
        }
        print(dTable)
        table.put_item(Item=dTable)
        return redirect("/user/dashboard")

    return render_template("user/AddCommunity.html")

@app.route('/user/AddHousing', methods=['GET', 'POST'])
def addHousing():
    print("Request Method: " + request.method)
    if request.method == 'POST':
        dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
        table = dynamodb.Table('Community')
        dTable = {
            "itemCode": time.time_ns(),
            "category": request.form['category'],
            "location": request.form['location'],
            "description": request.form['description'],
            "rent": request.form['rent'],
            "description": request.form['description'],
            "PhoneNumber": request.form['phone']
        }
        print(dTable)
        table.put_item(Item=dTable)
        return redirect("/user/dashboard")

    return render_template("user/AddHousing.html")

@app.route('/user/AddJob', methods=['GET', 'POST'])
def addJob():
    print("Request Method: " + request.method)
    if request.method == 'POST':
        dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
        table = dynamodb.Table('Community')
        dTable = {
            "itemCode": time.time_ns(),
            "category": request.form['category'],
            "experience": request.form['experience'],
            "salary": request.form['salary'],
            "location": request.form['location'],
            "description": request.form['description'],
            "PhoneNumber": request.form['phone']
        }
        print(dTable)
        table.put_item(Item=dTable)
        return redirect("/user/dashboard")

    return render_template("user/AddJob.html")

@app.route('/user/AddService', methods=['GET', 'POST'])
def addService():
    print("Request Method: " + request.method)
    if request.method == 'POST':
        dynamodb = boto3.resource('dynamodb',aws_access_key_id=S3_KEY,aws_secret_access_key=S3_SECRET,region_name="us-east-1")
        table = dynamodb.Table('Community')
        dTable = {
            "itemCode": time.time_ns(),
            "category": request.form['category'],
            "availability": request.form['availability'],
            "location": request.form['location'],
            "description": request.form['description'],
            "price": request.form['price'],
            "PhoneNumber": request.form['phone']
        }
        print(dTable)
        table.put_item(Item=dTable)
        return redirect("/user/dashboard")

    return render_template("user/AddService.html")
