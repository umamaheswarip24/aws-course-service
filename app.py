import os
import boto3
from flask import Flask, jsonify, request
 
client = boto3.client('sts')
print(client.get_caller_identity())

app = Flask(__name__)

REGION = os.environ.get("AWS_REGION", "ap-south-2")
 
dynamodb      = boto3.resource("dynamodb", region_name=REGION)
courses_table = dynamodb.Table("course-soloman")
 
 
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "course-service"}), 200
 
 
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
            "id": data["id"],
            "title": data["title"]
        }

        courses_table.put_item(Item=item)

        return jsonify({
            "message": "Course created successfully",
            "course": item
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
 
@app.route("/courses/<course_code>", methods=["GET"])
def get_course(course_code):
    resp = courses_table.get_item(Key={"id": course_code})
    item = resp.get("Item")
    if not item:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(item), 200
 
 
@app.route("/courses", methods=["GET"])
def list_courses():
    resp = courses_table.scan(Limit=50)
    return jsonify(resp.get("Items", [])), 200
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=False)
