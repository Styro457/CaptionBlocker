# TODO: Verify JSON queries in a more python way
# TODO: Implement this:
# https://flask-verify.readthedocs.io/en/latest/tutorial/json_verify_tutorial.html
"""Flask API to make GET and POST requests to a MariaDB server"""
import base64
import json
import sys
import uuid
from io import BytesIO

import mariadb
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from PIL import Image

app = Flask(__name__)
cors = CORS(app)


@app.route("/videos", methods=["GET"])
@cross_origin()
def get_block():
    """Handle GET Requests"""
    if request.method == "GET":
        video_id = request.args["video_id"]
        return select(video_id)
    return "ERROR"


@app.route("/videos", methods=["POST"])
@cross_origin()
def post_block():
    """Handle POST Requests"""
    if request.method == "POST":
        if "data" in request.json.keys():
            return save_image(request)
        else:
            return insert(request)
    return "ERROR"


def base64_to_image(base64_string):
    """ Convert base64 from API POST request to (image) bytes, then return """
    # Source: https://codebeautify.org/blog/how-to-convert-base64-to-image-using-python/
    # Remove the data URI prefix if present
    if "data:image" in base64_string:
        base64_string = base64_string.split(",")[1]

    # Decode the Base64 string into bytes
    image_bytes = base64.b64decode(base64_string)
    return image_bytes


def create_image_from_bytes(image_bytes):
    """ Convert (image) bytes to an image, then return """
    # Source: https://codebeautify.org/blog/how-to-convert-base64-to-image-using-python/
    # Create a BytesIO object to handle the image data
    image_stream = BytesIO(image_bytes)

    # Open the image using Pillow (PIL)
    image = Image.open(image_stream)
    return image


def detect_captions(file_name):
    """ Detect area of image with captions """
    # Source: https://stackoverflow.com/questions/37771263/detect-text-area-in-an-image-using-python-and-opencv
    import cv2

    # Load image, grayscale, Gaussian blur, adaptive threshold
    print(file_name)
    image = cv2.imread(file_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 30)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    iH, iW, c = image.shape
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 10000:
            x, y, w, h = cv2.boundingRect(c)
            if (y > iH / 2):
                print("Image info: ")
                print(f"iW: {iW}")
                print(f"iH: {iH}")
                print("Rectangle info:")
                print(f"x: {x}")
                print(f"y: {y}")
                print(f"w: {w}")
                print(f"h: {h}")
                return iW, iH, x, y, w, h
            # cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 3)
            # ROI = image[y:y+h, x:x+w]
            # cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)
            # ROI_number += 1
    return [iW, iH, 0, 0, 0, 0]
    # cv2.imshow('thresh', thresh)
    # cv2.imshow('dilate', dilate)
    # cv2.imshow('image', image)
    # cv2.waitKey()


def save_image(req_data):
    """ Save image from POST request to a file """
    # Source: https://codebeautify.org/blog/how-to-convert-base64-to-image-using-python/
    print("Saving request...")
    # Replace this with your Base64 string
    base64_string = req_data.json["data"]

    # Convert Base64 to image bytes
    image_bytes = base64_to_image(base64_string)

    # Create an image from bytes
    img = create_image_from_bytes(image_bytes)

    # Display or save the image as needed
    # Generate uuid for file name
    file_dir = "./img"
    file_name = str(uuid.uuid4())
    file_extension = "jpg"
    file = f"{file_dir}/{file_name}.{file_extension}"
    # img.show()  # Optional
    img.save(file)

    # Insert data
    video_id = req_data.json["video_id"]
    x_res, y_res, x_cord, y_cord, length, height = detect_captions(file)
    if (length == 0 or height == 0):
        print("No caption found in screenshot")
        return Response("{Captions not detected in image.}", status=201, mimetype='application/json')
    screenshot_dict = {"video_id": video_id, "x_res": x_res, "y_res": y_res, "x_cord": x_cord,
                       "y_cord": y_cord, "length": length, "height": height}
    # screenshot_json = json.dumps(screenshot_dict)
    # Convert JSON formatted str into JSON type (to avoid type error)
    # screenshot_json = json.loads(str(screenshot_dict))
    insert(screenshot_dict)
    # return 200
    return Response("{Captions found, image saved, data inserted.}", status=200, mimetype='application/json')
    print("Request saved...")


def insert(request_data):
    """Insert data using SQL query to MariaDB server"""
    conn, cursor = connect_to_mariadb()
    # --- Example: Select Data ---
    print("\nInserting data...")

    # Check if the JSON has all components, catch KeyError
    try:
        website = "https://youtube.com"
        if type(request_data) is dict:
            video_id = request_data["video_id"]
            x_cord = request_data["x_cord"]
            y_cord = request_data["y_cord"]
            length = request_data["length"]
            height = request_data["height"]
            x_res = request_data["x_res"]
            y_res = request_data["y_res"]
        else:
            video_id = request_data.json["video_id"]
            x_cord = request_data.json["x_cord"]
            y_cord = request_data.json["y_cord"]
            length = request_data.json["length"]
            height = request_data.json["height"]
            x_res = request_data.json["x_res"]
            y_res = request_data.json["y_res"]
    except KeyError:
        print("JSON request was improperly formatted.")
        return "JSON request was improperly formatted.", 201

    insert_query = f"""INSERT INTO VIDEOS
    (website, video_id, x_cord, y_cord, length, height, x_res, y_res)
    VALUES
    ('{website}', '{video_id}', {x_cord}, {y_cord}, {length}, {height}, {x_res}, {y_res});"""

    # Note the comma for single parameter tuple
    cursor.execute(insert_query)
    conn.commit()

    cursor.connection.close()
    return "DONE", 200


def select(video_id):
    """Make SQL query to get needed data based on YouTube Video ID"""
    _, cursor = connect_to_mariadb()
    # --- Example: Select Data ---
    print("\nSelecting data...")
    select_query = f"""SELECT website, video_id, x_cord, y_cord,
    length, height, x_res, y_res FROM VIDEOS WHERE video_id='{video_id}'"""

    # Note the comma for single parameter tuple
    cursor.execute(select_query)

    # Jsonify the results somehow
    # Source: https://stackoverflow.com/questions/3286525/return-sql-table-as-json-in-python
    r = [
        dict((cursor.description[i][0], value) for i, value in enumerate(row))
        for row in cursor.fetchall()
    ]
    if r == []:
        return Response("{No data for given URL.}", status=201, mimetype='application/json')
    cursor.connection.close()
    # return json.dumps(r[0] if r else None), 200
    # Return last row, by using -1
    return json.dumps(r[-1] if r else None), 200


def connect_to_mariadb():
    """Make connection to MariaDB server, return connection and cursor"""
    # Connect to Mariadb
    # Source:https://mariadb.com/docs/connectors/connectors-quickstart-guides/connector-python-guide
    try:
        conn = mariadb.connect(
            user="root",
            password="pass",
            host="127.0.0.1",
            port=3306,
            database="caption_capper",
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cursor = conn.cursor()
    return conn, cursor


if __name__ == "__main__":
    app.run(debug=True)
