from flask import Flask, request, jsonify, render_template, session
import vonage
import random
from pymongo import MongoClient
from bson import json_util
from bson import ObjectId
from bson.json_util import dumps
import json
import string
import secrets
from werkzeug.exceptions import BadRequestKeyError

app = Flask(__name__)

app.secret_key = "hellow_EcoRecycle"
client = MongoClient("mongodb://localhost:27017")
db = client["EcoRecycle"]
users_collection = db["users"]


##########################################################################################################################################################################################
# User Section
@app.route("/")
def index():
    return render_template("users/home.html")


@app.route("/signin")
def signin():
    return render_template("users/signin.html")


@app.route("/get_criteria", methods=["POST"])
def get_criteria():
    try:
        result = producer_collection.find()
        if result:
            return jsonify(
                {"status": "success", "message": "Data found", "data": dumps(result)}
            )
        else:
            return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get_criteria1", methods=["POST"])
def get_criteria1():
    brand = request.form["brand"]
    filter = {"organization_name": brand}
    try:
        result = producer_collection.find_one(filter)
        if result:
            return jsonify(
                {"status": "success", "message": "Data found", "data": dumps(result)}
            )
        else:
            return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/to_find_recycle_centre_page")
def to_find_recycle_centre_page():
    return render_template("users/find_recycle_centre.html")


@app.route("/to_schedule_pick_up_page")
def to_schedule_pick_up_page():
    return render_template("users/schedule_pick_up.html")


@app.route("/to_details_page")
def to_details_page():
    return render_template("users/details.html")


@app.route("/get_filtered_recycle_centre", methods=["POST"])
def get_filtered_recycle_centre():
    try:
        brand = request.form["brand"]
        result = producer_collection.find_one({"organization_name": brand})
        if result:
            result = result["approve_cc"]
            cc_data_list = []
            for key in result:
                cc_data_id = result[key]
                cc_data = collection_centre.find_one({"_id": ObjectId(cc_data_id)})
                if cc_data:
                    cc_data_list.append(cc_data)
                    return jsonify(
                        {
                            "status": "success",
                            "message": "Data found",
                            "data": dumps(cc_data_list),
                        }
                    )
                else:
                    return jsonify({"status": "error", "message": "Data not found"})
        else:
            return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get_cc_data", methods=["POST"])
def get_cc_data():
    try:
        id = request.form["id"]
        result = collection_centre.find_one({"_id": ObjectId(id)})
        if result:
            return jsonify(
                {"status": "success", "message": "Data found", "data": dumps(result)}
            )
        else:
            return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/set_pick_up_data", methods=["POST"])
def set_pick_up_data():
    try:
        data = request.form["data"]
        data = json.loads(data)
        cc_id = data["cc_id"]
        with open("user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            user_id = file_data["_id"]["$oid"]
        data["user_id"] = user_id
        unique_id = generate_alphanumeric(12)
        query = {unique_id: data}
        result = collection_centre.find_one({"_id": ObjectId(cc_id)})
        if "pick_up_requests" in result:
            data1 = result["pick_up_requests"]
            data1[unique_id] = data
            result = collection_centre.update_one(
                {"_id": ObjectId(cc_id)}, {"$set": {"pick_up_requests": data1}}
            )
            if result.modified_count == 1:
                with open("user_data.txt", "r") as file:
                    data = file.read()
                    data = json.loads(data)
                    user_id = data["_id"]["$oid"]
                    result = users_collection.find_one({"_id": ObjectId(user_id)})
                    if "pick_up_requests" in result:
                        data1 = result["pick_up_requests"]
                        data1[unique_id] = cc_id
                        result = users_collection.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {"pick_up_requests": data1}},
                        )
                        return jsonify(
                            {
                                "status": "success",
                                "message": "Pick-up Schedule Successfully",
                            }
                        )
                    else:
                        result["pick_up_requests"] = {unique_id: cc_id}
                        result = users_collection.update_one(
                            {"_id": ObjectId(user_id)}, {"$set": result}
                        )
                        if result.modified_count == 1:
                            return jsonify(
                                {
                                    "status": "success",
                                    "message": "Pick-up Schedule Successfully",
                                }
                            )
                        else:
                            return jsonify(
                                {
                                    "status": "error",
                                    "message": "Unable to process request",
                                }
                            )

        else:
            result["pick_up_requests"] = query
            result = collection_centre.update_one(
                {"_id": ObjectId(cc_id)}, {"$set": result}
            )
            if result.modified_count == 1:
                with open("user_data.txt", "r") as file:
                    data = file.read()
                    data = json.loads(data)
                    user_id = data["_id"]["$oid"]
                    result = users_collection.find_one({"_id": ObjectId(user_id)})
                    if "pick_up_requests" in result:
                        data1 = result["pick_up_requests"]
                        data1[unique_id] = cc_id
                        result = users_collection.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {"pick_up_requests": data1}},
                        )
                        return jsonify(
                            {
                                "status": "success",
                                "message": "Pick-up Schedule Successfully",
                            }
                        )
                    else:
                        result["pick_up_requests"] = {unique_id: cc_id}
                        result = users_collection.update_one(
                            {"_id": ObjectId(user_id)}, {"$set": result}
                        )
                        if result.modified_count == 1:
                            return jsonify(
                                {
                                    "status": "success",
                                    "message": "Pick-up Schedule Successfully",
                                }
                            )
                        else:
                            return jsonify(
                                {
                                    "status": "error",
                                    "message": "Unable to process request",
                                }
                            )
    except Exception as e:
        return jsonify({"message": str(e)})


@app.route("/to_profile_page")
def to_profile_page():
    return render_template("users/profile.html")


@app.route("/to_pick_up_history_page")
def to_pick_up_history_page():
    return render_template("users/history.html")


@app.route("/send_otp", methods=["POST"])
def send_otp():
    mobile_number = "91" + request.form["mobile_number"]
    session["mobile_no"] = mobile_number
    otp = str(random.randint(100000, 999999))
    session["otp"] = otp
    client = vonage.Client(key="74d0f3a9", secret="xc5jQEu8TJAlf81e")
    sms = vonage.Sms(client)
    responseData = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": mobile_number,
            "text": "Hello users, your OTP is" + " " + otp,
        }
    )

    if responseData["messages"][0]["status"] == "0":
        return jsonify({"status": "success", "message": "OTP sent successfully."})
    else:
        return jsonify(
            {
                "status": "error",
                "message": f"Failed to send OTP: {responseData['messages'][0]['error-text']}",
            }
        )


@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    otp = session.get("otp")
    print(otp)
    enter_otp = request.form["enter_otp"]
    print(enter_otp)
    if otp == enter_otp:
        return jsonify({"message": "OTP verified successfully", "status": "correct"})
    else:
        return jsonify({"message": "Incorrect OTP", "status": "incorrect"})


@app.route("/more_details")
def more_details():
    return render_template("users/sign_up.html")


@app.route("/send_data_to_database", methods=["POST"])
def send_data_to_database():
    name = request.form["name"]
    print(name)
    email = request.form["email"]
    address = request.form["address"]
    password = request.form["password"]
    mobile_number = session.get("mobile_no")
    try:
        result = users_collection.insert_one(
            {
                "name": name,
                "email": email,
                "address": address,
                "password": password,
                "mobile_number": mobile_number,
            }
        )
        session["user_data_id"] = str(result.inserted_id)
        return jsonify({"status": "success", "message": str(result.inserted_id)})

    except Exception as e:
        return jsonify({"status": "error", "message": e})


@app.route("/get_pick_up_history", methods=["POST"])
def get_pick_up_history():
    try:
        with open("user_data.txt", "r") as file:
            data = file.read()
            data = json.loads(data)
            user_data_id = data["_id"]["$oid"]
        result = users_collection.find_one({"_id": ObjectId(user_data_id)})
        result = result["pick_up_requests"]
        history_list = []
        for key in result:
            cc_id = result[key]
            unique_id = key
            data = collection_centre.find_one({"_id": ObjectId(cc_id)})
            data = data["pick_up_requests"]
            for item in data:
                if unique_id == item:
                    object = {unique_id: data[item]}
                    history_list.append(object)
        return jsonify(
            {"status": "success", "message": "Data Found", "data": dumps(history_list)}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": e})


@app.route("/home")
def home():
    return render_template("/users/home.html")


@app.route("/search_user_in_database", methods=["POST"])
def search_user_in_database():
    try:
        if "mobile_no" not in request.form:
            return jsonify({"error": "Mobile number not provided"}), 400

        mobile_number = request.form["mobile_no"]
        query = {"mobile_number": "91" + str(mobile_number)}
        result = users_collection.find_one(query)

        if result:
            json_result = json_util.dumps(result)
            return jsonify({"message": "user exist", "status": "success"})
        else:
            return jsonify({"message": "User not found", "status": "error"})
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"})


@app.route("/set_data_in_file", methods=["POST"])
def set_data_in_file():
    try:
        mobile_number = request.form["mobile_no"]
        query = {"mobile_number": "91" + str(mobile_number)}
        result = users_collection.find_one(query)
        json_result = json_util.dumps(result)
        with open("user_data.txt", "w") as file:
            file.write(json_result)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": e})


@app.route("/sign_out", methods=["POST"])
def sign_out():
    try:
        with open("user_data.txt", "w") as file:
            file.write("")
        return jsonify({"status": "success", "message": "Sign out successfully"})
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "We have some technical problme", "code": e}
        )


@app.route("/check_status", methods=["POST"])
def check_status():
    try:
        with open("user_data.txt", "r") as file:
            data = file.read()
        if data:
            data = json.loads(data)
            data = data["_id"]["$oid"]
            result = users_collection.find_one({"_id": ObjectId(data)})
            return jsonify(
                {"status": "found", "message": "user exits", "data": dumps(result)}
            )
        else:
            return jsonify({"status": "not found", "message": "user not found"})
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "we have some technical issue", "code": e}
        )


# User Section
###############################################################################################################################################

# Producer Section

producer_collection = db["producer"]


@app.route("/p_profile")
def p_profile():
    return render_template("producer/profile.html")


@app.route("/p_sign_in")
def p_sign_in():
    return render_template("producer/sign_in_sign_up.html")


@app.route("/p_sign_up")
def p_sign_up():
    return render_template("producer/sign_in_sign_up.html")


@app.route("/p_to_approved_cc_page")
def p_to_approved_cc_page():
    return render_template("producer/available_cc.html")


@app.route("/p_to_list_item_page")
def p_to_list_item_page():
    return render_template("producer/list_item.html")


@app.route("/p_status", methods=["POST"])
def p_status():
    data = ""
    with open("p_user_data.txt", "r") as file:
        data = json.load(file)
    if data:
        dataId = data["_id"]["$oid"]
        result = producer_collection.find_one({"_id": ObjectId(dataId)})
        return jsonify(
            {
                "status": "success",
                "message": "user exists",
                "data": {
                    "organization_name": result.get("organization_name"),
                    "profile_url": result.get("profile_url"),
                },
            }
        )
    else:
        return jsonify({"status": "error", "message": "user not exists"})


@app.route("/p_get_cc", methods=["POST"])
def p_get_cc():
    try:
        result = collection_centre.find()
        if result:
            return jsonify(
                {
                    "status": "success",
                    "message": "Collection Centers Found",
                    "data": dumps(result),
                }
            )
        else:
            return jsonify(
                {"status": "error", "message": "Collection Centers Not Found"}
            )

    except Exception as e:
        jsonify({"message": e})


def p_send_sign_up_data(query):
    try:
        result = users_collection.insert_one(query)
        json_result = json_util.dumps(result)
        session["producer_data_id"] = str(json_result.inserted_id)
        return jsonify({"status": "success", "message": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"status": "error", "message": e})


@app.route("/p_search_user_in_database", methods=["POST"])
def p_search_user_in_database():
    try:
        query = {"email": request.form["email"], "password": request.form["password"]}
        result = producer_collection.find_one({"email": request.form["email"]})
        if result:
            return jsonify(
                {
                    "status": "success",
                    "message": "User already exists with this email id",
                }
            )
        else:
            return jsonify({"status": "error", "message": "User not exist"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/p_send_user_data", methods=["POST"])
def p_send_user_data():
    query = {"email": request.form["email"], "password": request.form["password"]}
    try:
        result = producer_collection.insert_one(query)
        return jsonify({"status": "success", "message": "Sign up successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/p_get_user_data", methods=["POST"])
def p_get_user_data():
    query = {"email": request.form["email"], "password": request.form["password"]}
    result = producer_collection.find_one(query)
    if result:
        with open("p_user_data.txt", "w") as file:
            json_result = json_util.dumps(result)
            file.write(json_result)
        return jsonify({"status": "success", "message": "Sign in successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid Email or Password"})


def generate_alphanumeric(length):
    alphanumeric_characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphanumeric_characters) for _ in range(length))


@app.route("/p_send_user_profile_data", methods=["POST"])
def p_send_user_profile_data():
    data = ""
    dataId = ""
    query = {
        "organization_name": request.form["organization_name"],
        "manager_name": request.form["manager_name"],
        "position": request.form["position"],
        "contact": request.form["contact"],
        "organization_address": request.form["organization_address"],
        "organization_description": request.form["organization_description"],
        "profile_url": request.form["profile_url"],
    }
    with open("p_user_data.txt", "r") as file:
        data = json.load(file)
        dataId = data["_id"]["$oid"]
    filter = {"_id": ObjectId(dataId)}
    update = {"$set": query}
    try:
        result = producer_collection.update_one(filter, update)
        if result.modified_count == 1:
            print("Document updated successfully")
            return jsonify(
                {"status": "success", "message": "Changes made successfully"}
            )
        else:
            print("Document not found or no changes made")
            return jsonify({"status": "error", "message": "Unable to make changes"})
    except Exception as e:
        return jsonify({"status": "error", "message": e})


@app.route("/p_set_listed_product", methods=["POST"])
def p_set_listed_product():
    try:
        unique_id = generate_alphanumeric(12)
        data = {
            "product_category": request.form["product_category"],
            "product_name": request.form["product_name"],
            "product_model": request.form["product_model"],
            "product_specification": request.form["product_specification"],
            "product_baseprice": request.form["product_baseprice"],
            "deductions": request.form["deductions"],
            "product_url": request.form["product_url"],
            "product_instructions": request.form["product_instructions"],
        }
        query = {unique_id: data}
        query1 = {"$set": {"listed_product": query}}
        with open("p_user_data.txt", "r") as file:
            data1 = json.load(file)
        dataId = data1["_id"]["$oid"]
        filter = {"_id": ObjectId(dataId)}
        existing_data = producer_collection.find_one(filter)
        if "listed_product" in existing_data:
            existing_data = existing_data["listed_product"]
            existing_data[unique_id] = data
            query1 = {"$set": {"listed_product": existing_data}}
            result = producer_collection.update_one(filter, query1)
        else:
            print("else")
            result = producer_collection.update_one(filter, query1)
        if result.modified_count == 1:
            print("Document updated successfully")
            return jsonify(
                {"status": "success", "message": "Batch Created successfully"}
            )
        else:
            print("Document not found or no changes made")
            return jsonify({"status": "error", "message": "Unable to save data"})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "An error occurred while processing the request",
            }
        )


@app.route("/p_get_listed_product", methods=["POST"])
def p_get_listed_product():
    with open("p_user_data.txt", "r") as file:
        data1 = json.load(file)
    dataId = data1["_id"]["$oid"]
    filter = {"_id": ObjectId(dataId)}
    existing_data = producer_collection.find_one(filter)
    existing_data = existing_data["listed_product"]
    if existing_data:
        return jsonify(
            {"status": "success", "message": "Products Found", "data": existing_data}
        )
    else:
        return jsonify({"status": "error", "message": "No Product Found"})


@app.route("/p_get_listed_product_info", methods=["POST"])
def p_get_listed_product_info():
    data = ""
    with open("p_user_data.txt", "r") as file:
        data = json.load(file)
    dataId = data["_id"]["$oid"]
    result = producer_collection.find_one(
        {"_id": ObjectId(dataId)}, {"_id": 1, f"listed_product": 1}
    )
    result = result["listed_product"]
    if result:
        return jsonify(
            {"status": "success", "message": "user exists", "data": dumps(result)}
        )
    else:
        return jsonify({"status": "error", "message": "user not exists"})


@app.route("/listed_product_info_page")
def listed_product_info_page():
    return render_template("producer/listed_item_info.html")


@app.route("/p_approve_cc", methods=["POST"])
def p_approve_cc():
    cc_id = request.form["cc_id"]
    try:
        unique_id = generate_alphanumeric(12)
        query = {unique_id: cc_id}
        query1 = {"$set": {"approve_cc": query}}
        with open("p_user_data.txt", "r") as file:
            data1 = json.load(file)
        dataId = data1["_id"]["$oid"]
        filter = {"_id": ObjectId(dataId)}
        existing_data = producer_collection.find_one(filter)
        if existing_data:
            existing_data["approve_cc"] = query
            query1 = {"$set": {"approve_cc": existing_data["approve_cc"]}}
            result = producer_collection.update_one(filter, query1)
        else:
            query1 = {"$set": {"approve_cc": query}}
            result = producer_collection.update_one(filter, query1)
        if result.modified_count == 1:
            print("Document updated successfully")
            return jsonify({"status": "success", "message": "Approved Successfully"})
        else:
            print("Document not found or no changes made")
            return jsonify({"status": "error", "message": "Unable to Approve"})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "An error occurred while processing the request",
            }
        )


@app.route("/p_get_approved_cc", methods=["POST"])
def p_get_approved_cc():
    data = ""
    list = []
    with open("p_user_data.txt", "r") as file:
        data = json.load(file)
    dataId = data["_id"]["$oid"]
    result = producer_collection.find_one({"_id": ObjectId(dataId)})
    if result:
        result = result["approve_cc"]
        for key in result:
            data = collection_centre.find_one({"_id": ObjectId(result[key])})
            list.append(data)
        return jsonify(
            {"status": "success", "message": "Data found", "data": dumps(list)}
        )
    else:
        return jsonify({"status": "error", "message": "Data not found"})


@app.route("/to_manage_batch_page")
def to_manage_batch_page():
    return render_template("producer/manage_batches.html")


# Producer Section
################################################################################################################################################################################


# COLLECTION CENTER SECTION
################################################################################################################################################################################
collection_centre = db["collection_centre"]


@app.route("/c_sign_in")
def c_sign_in():
    return render_template("collection_center/sign_in_sign_up.html")


@app.route("/c_profile")
def c_profile():
    return render_template("collection_center/profile.html")


@app.route("/c_sign_out", methods=["POST"])
def c_sign_out():
    with open("c_user_data.txt", "w") as file:
        file.write("")
        return jsonify({"status": "success", "message": "Sign out successfully"})


@app.route("/c_producer_listed_item_page")
def c_producer_listed_item_page():
    return render_template("collection_center/producer_listed_item.html")


@app.route("/create_batch_page")
def create_batch_page():
    return render_template("collection_center/create_and_manage_batch.html")


@app.route("/c_search_user_in_database", methods=["POST"])
def c_search_user_in_database():
    try:
        query = {"email": request.form["email"], "password": request.form["password"]}
        result = collection_centre.find_one({"email": request.form["email"]})
        if result:
            return jsonify(
                {
                    "status": "success",
                    "message": "User already exists with this email id",
                }
            )
        else:
            return jsonify({"status": "error", "message": "User not exist"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/c_Dashboard")
def c_Dashboard():
    return render_template("collection_center/DashboardRC.html")


@app.route("/fetch_pick_up_request", methods=["POST"])
def fetch_pick_up_request():
    try:
        with open("c_user_data.txt", "r") as file:
            data = json.load(file)
            dataId = data["_id"]["$oid"]
        print(dataId)
        result = collection_centre.find_one({"_id": ObjectId(dataId)})
        print(result)
        if result:
            if "pick_up_requests" in result:
                result = result["pick_up_requests"]
                return jsonify(
                    {"status": "success", "message": "Data found", "data": result}
                )
            else:
                return jsonify({"status": "error", "message": "Data not found"})
        else:
            return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        return jsonify({"message": str(e)})


@app.route("/c_send_user_data", methods=["POST"])
def c_send_user_data():
    query = {"email": request.form["email"], "password": request.form["password"]}
    try:
        result = collection_centre.insert_one(query)
        return jsonify({"status": "success", "message": "Sign up successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/change_status", methods=["POST"])
def change_status():
    try:
        unique_id = request.form["id"]
        status = request.form["status"]
        with open("c_user_data.txt", "r") as file:
            data = json.load(file)
            cc_id = data["_id"]["$oid"]
        result = collection_centre.find_one({"_id": ObjectId(cc_id)})
        if result:
            result = result["pick_up_requests"]
            for item in result:
                if item == unique_id:
                    data = result[item]
                    data["status"] = status
                    result[unique_id] = data
                    result = collection_centre.update_one(
                        {"_id": ObjectId(cc_id)}, {"$set": {"pick_up_requests": result}}
                    )
                    if result.modified_count == 1:
                        return jsonify(
                            {"status": "success", "message": "Status Change"}
                        )
                    else:
                        return jsonify(
                            {"status": "error", "message": "Unable to make changes"}
                        )
        else:
            return jsonify({"status": "error", "message": "Data not Found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/c_get_user_data", methods=["POST"])
def c_get_user_data():
    query = {"email": request.form["email"], "password": request.form["password"]}
    result = collection_centre.find_one(query)
    if result:
        with open("c_user_data.txt", "w") as file:
            json_result = json_util.dumps(result)
            file.write(json_result)
        return jsonify({"status": "success", "message": "Sign in successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid Email or Password"})


@app.route("/c_send_user_profile_data", methods=["POST"])
def c_send_user_profile_data():
    data = ""
    dataId = ""
    query = {
        "organization_name": request.form["organization_name"],
        "address": request.form["address"],
        "description": request.form["description"],
        "operating_hours": request.form["operating_hours"],
        "contact_number": request.form["contact_number"],
        "email": request.form["email"],
        "charges": request.form["charges"],
        "profile_url": request.form["profile_url"],
    }
    with open("c_user_data.txt", "r") as file:
        data = json.load(file)
        dataId = data["_id"]["$oid"]
    filter = {"_id": ObjectId(dataId)}
    update = {"$set": query}
    try:
        result = collection_centre.update_one(filter, update)
        if result.modified_count == 1:
            print("Document updated successfully")
            return jsonify(
                {"status": "success", "message": "Changes made successfully"}
            )
        else:
            print("Document not found or no changes made")
            return jsonify({"status": "error", "message": "Unable to make changes"})
    except Exception as e:
        return jsonify({"status": "error", "message": e})


@app.route("/c_get_profile", methods=["POST"])
def c_get_profile():
    with open("c_user_data.txt", "r") as file:
        data1 = json.load(file)
    dataId = data1["_id"]["$oid"]
    filter = {"_id": ObjectId(dataId)}
    result = collection_centre.find_one(filter)
    if result:
        return jsonify(
            {"status": "success", "message": "Products Found", "data": dumps(result)}
        )
    else:
        return jsonify({"status": "error", "message": "No Product Found"})


@app.route("/get_listed_product_for_cc", methods=["POST"])
def get_listed_product_for_cc():
    try:
        with open("c_user_data.txt", "r") as file:
            data = file.read()
            data = json.loads(data)
            cc_id = data["_id"]["$oid"]
            print(cc_id)
        list_of_producer = []
        flag = 0
        result = producer_collection.find()
        for item in result:
            if "approve_cc" in item:
                producer_data = item
                approved_cc = item["approve_cc"]
                for key in approved_cc:
                    print(approved_cc[key])
                    if approved_cc[key] == cc_id:
                        flag = 1
                        list_of_producer.append(producer_data)
            else:
                print("approve_cc not found in item")
        if flag == 0:
            return jsonify(
                {"status": "error", "message": "Your are not approved by any producer"}
            )
        else:
            return jsonify(
                {
                    "status": "success",
                    "message": "Data found",
                    "data": dumps(list_of_producer),
                }
            )
    except Exception as e:
        return jsonify({"meaasge": str(e)})


@app.route("/c_create_batch", methods=["POST"])
def c_create_batch():
    try:
        print("runnugg")
        unique_id = request.form["unique_id"]
        print(unique_id)
        data = {
            "batch_name": request.form["batch_name"],
            "unique_id": request.form["unique_id"],
            "description": request.form["description"],
            "date": request.form["date"],
            "brand": request.form["brand"],
            "product_name": request.form["product_name"],
            "product_model": request.form["product_model"],
            "product_category": request.form["product_category"],
            "product_specification": request.form["product_specification"],
            "product_baseprice": request.form["product_baseprice"],
            "producer_id": request.form["producer_id"],
        }

        query = {unique_id: data}
        query1 = {"$set": {"batch_created": query}}
        with open("c_user_data.txt", "r") as file:
            data1 = json.load(file)
        dataId = data1["_id"]["$oid"]
        filter = {"_id": ObjectId(dataId)}
        existing_data = collection_centre.find_one(filter)
        if "batch_created" in existing_data:
            existing_data = existing_data["batch_created"]
            existing_data[unique_id] = data
            query1 = {"$set": {"batch_created": existing_data}}
            result = collection_centre.update_one(filter, query1)
        else:
            result = collection_centre.update_one(filter, query1)
        if result.modified_count == 1:
            print("Document updated successfully")
            return jsonify(
                {"status": "success", "message": "Batch Created successfully"}
            )
        else:
            print("Document not found or no changes made")
            return jsonify({"status": "error", "message": "Unable to save data"})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "An error occurred while processing the request",
            }
        )


@app.route("/c_get_batches", methods=["POST"])
def c_get_batches():
    try:
        with open("c_user_data.txt", "r") as file:
            data = file.read()
            data = json.loads(data)
            cc_id = data["_id"]["$oid"]
        filter = {"_id": ObjectId(cc_id)}
        result = collection_centre.find_one(filter)
        print(result)
        if "batch_created" in result:
            batches = result["batch_created"]
            return jsonify(
                {"status": "success", "message": "Data Found", "data": dumps(batches)}
            )
        else:
            return jsonify({"status": "error", "message": "Data Not Found"})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": str(e)})


@app.route("/c_get_items_for_batch", methods=["POST"])
def c_get_items_for_batch():
    try:
        with open("c_user_data.txt", "r") as file:
            data = file.read()
            data = json.loads(data)
            cc_id = data["_id"]["$oid"]
        filter = {"_id": ObjectId(cc_id)}
        result = collection_centre.find_one(filter)
        if "pick_up_requests" in result:
            result = result["pick_up_requests"]
            return jsonify(
                {"status": "success", "message": "Data Found", "data": dumps(result)}
            )
        else:
            return jsonify({"status": "error", "message": "Data Not Found"})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": str(e)})


@app.route("/c_insert_item_to_batch", methods=["POST"])
def c_insert_item_to_batch():
    try:
        batch_id = request.form["batch_id"]
        item_id = request.form["item_id"]
        user_id = request.form["user_id"]
        print(batch_id)

        with open("c_user_data.txt", "r") as file:
            data = json.load(file)
            cc_id = data["_id"]["$oid"]
        filter = {"_id": ObjectId(cc_id)}
        result = collection_centre.find_one(
            filter, {"_id": 1, f"batch_created.{batch_id}": 1}
        )
        if result is None:
            print("No document found with the provided _id")
            return jsonify({"message": "No document found with the provided _id"})

        batch_data = result.get("batch_created", {}).get(batch_id)
        if batch_data is None:
            print("Batch ID does not exist")
            return jsonify({"message": "Such Batch doesn't exist"})
        items = batch_data.get("items", {})
        items[item_id] = user_id
        result = collection_centre.update_one(
            filter, {"$set": {f"batch_created.{batch_id}.items": items}}
        )
        if result.modified_count == 1:
            print(result.modified_count)
            print("Item successfully added to the batch")
            return jsonify(
                {"status": "success", "message": "Item successfully added to the batch"}
            )
        else:
            print(
                "No document was modified, possible issue with the batch_id or user_id"
            )
            return jsonify(
                {
                    "status": "error",
                    "message": "Item Already added to the selcted batch",
                }
            )
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": str(e)})

    ################################################################################################################################################################################


@app.route("/recent_batches")
def recent_batches():
    return render_template("collection_center/batches.html")


@app.route("/manage_batches")
def request_for_pick_up():
    return render_template("collection_center/manage_batches.html")


# COLLECTION CENTER SECTION End HERE


##############################################################################################################################
# Batch Managment start here
#######################################################################################################################
batches = db["batches"]


@app.route("/c_send_request", methods=["POST"])
def c_send_request():
    try:
        data = request.form["data"]
        data = json.loads(data)
        print(data)
        with open("c_user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            cc_id = file_data["_id"]["$oid"]
        data["sender_id"] = cc_id
        batch_id = data["unique_id"]
        for_batch = batches.insert_one(data)
        if for_batch.inserted_id:
            result = collection_centre.find_one(
                {"_id": ObjectId(cc_id)}, {"_id": 1, f"batch_created.{batch_id}": 1}
            )
            result = result["batch_created"][batch_id]
            result["storing_id"] = for_batch.inserted_id
            for_cc = collection_centre.update_one(
                {"_id": ObjectId(cc_id)},
                {"$set": {f"batch_created.{batch_id}": result}},
            )
            if for_cc.modified_count == 1:
                return jsonify(
                    {"status": "success", "message": "Request send successfully"}
                )
            else:
                return jsonify({"status": "error", "message": "Request send failed"})
    except Exception as e:
        print(str(e))
        return jsonify({"message", str(e)})


@app.route("/c_all_batches", methods=["POST"])
def c_all_batches():
    try:
        list_of_batches = []
        with open("c_user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            cc_id = file_data["_id"]["$oid"]
            result = batches.find({"sender_id": cc_id})
            if result:
                for doc in result:
                    list_of_batches.append(doc)
                return jsonify(
                    {
                        "status": "success",
                        "message": "Data Found",
                        "data": dumps(list_of_batches),
                    }
                )
            else:
                print("No Batche found")
                return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)})


@app.route("/p_fetch_request", methods=["POST"])
def p_fetch_request():
    try:
        list_of_batches = []
        with open("p_user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            p_id = file_data["_id"]["$oid"]
            result = batches.find({"producer_id": p_id})
            if result:
                for doc in result:
                    list_of_batches.append(doc)
                return jsonify(
                    {
                        "status": "success",
                        "message": "Data Found",
                        "data": dumps(list_of_batches),
                    }
                )
            else:
                print("No Batche found")
                return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)})


@app.route("/p_set_status_to_approve", methods=["POST"])
def p_set_status_to_approve():
    try:
        doc_id = request.form["doc_id"]
        result = batches.update_one(
            {"_id": ObjectId(doc_id)}, {"$set": {"status": "Approved"}}
        )
        if result.modified_count == 1:
            return jsonify(
                {"status": "success", "message": "Status updated successfully"}
            )
        else:
            return jsonify({"status": "error", "message": "Failed to update status"})
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)})


@app.route("/p_all_batches", methods=["POST"])
def p_all_batches():
    try:
        list_of_batches = []
        with open("p_user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            p_id = file_data["_id"]["$oid"]
            result = batches.find({"producer_id": p_id})
            if result:
                for doc in result:
                    list_of_batches.append(doc)
                return jsonify(
                    {
                        "status": "success",
                        "message": "Data Found",
                        "data": dumps(list_of_batches),
                    }
                )
            else:
                print("No Batche found")
                return jsonify({"status": "error", "message": "Data not found"})
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)})


@app.route("/c_change_status", methods=["POST"])
def c_change_status():
    try:
        batch_id = request.form["batch_id"]
        value = request.form["value"]
        with open("c_user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            cc_id = file_data["_id"]["$oid"]
            result = batches.update_one(
                {"sender_id": cc_id, "unique_id": batch_id},
                {"$set": {"batch_status": value}},
            )
            if result.modified_count == 1:
                return jsonify(
                    {"status": "success", "message": "Status Update Successfully"}
                )
            else:
                return jsonify(
                    {"status": "error", "message": "Unable to Status Update "}
                )
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)})


@app.route("/p_change_status", methods=["POST"])
def p_change_status():
    try:
        batch_id = request.form["batch_id"]
        value = request.form["value"]
        with open("p_user_data.txt", "r") as file:
            file_data = file.read()
            file_data = json.loads(file_data)
            cc_id = file_data["_id"]["$oid"]
            result = batches.update_one(
                {"producer_id": cc_id, "unique_id": batch_id},
                {"$set": {"batch_status": value}},
            )
            if result.modified_count == 1:
                return jsonify(
                    {"status": "success", "message": "Status Update Successfully"}
                )
            else:
                return jsonify(
                    {"status": "error", "message": "Unable to Status Update "}
                )
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)})


########################################################################################################################

if __name__ == "__main__":
    app.run(debug=True)
