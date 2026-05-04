import os
import boto3
from flask import Flask, jsonify, request

app = Flask(__name__)

# AWS Region
REGION = os.environ.get("AWS_REGION", "ap-south-2")   # 🔴 KEEP or change if needed

# DynamoDB Setup
dynamodb = boto3.resource("dynamodb", region_name=REGION)
courses_table = dynamodb.Table("uma-course-table")     # 🔴 CHANGE: your DynamoDB table name


# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "course-service"   # 🔴 CHANGE: same as above
    }), 200


# ---------------------------
# CREATE COURSE (POST)
# ---------------------------
@app.route("/courses", methods=["POST"])
def create_course():
    try:
        data = request.get_json()

        # validation
        if not data or "id" not in data or "title" not in data:
            return jsonify({"error": "Both 'id' and 'title' are required"}), 400

        item = {
            "id": data["id"],          # 🔴 MAKE SURE this matches your table PK
            "title": data["title"]
        }

        courses_table.put_item(Item=item)

        return jsonify({
            "message": "Course created successfully",
            "course": item
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# GET SINGLE COURSE
# ---------------------------
@app.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):
    resp = courses_table.get_item(Key={"id": course_id})   # 🔴 MUST match your PK
    item = resp.get("Item")

    if not item:
        return jsonify({"error": "Course not found"}), 404

    return jsonify(item), 200


# ---------------------------
# LIST COURSES
# ---------------------------
@app.route("/courses", methods=["GET"])
def list_courses():
    resp = courses_table.scan(Limit=50)
    return jsonify(resp.get("Items", [])), 200


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=False)
