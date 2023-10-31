from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from pymongo.errors import ServerSelectionTimeoutError
import subprocess

app = Flask(__name__)

def clear_cache():
    # Use a shell command to remove cached files from the /var/cache/nginx directory
    try:
        subprocess.run(["rm", "-rf", "/var/cache/nginx"])
    except Exception as e:
        # Handle any exceptions that may occur while clearing the cache
        print(f"Error clearing cache: {str(e)}")

@app.route('/')
def ping_server():
    return "Welcome to the world of animals."



def get_db():
    try:
        # Create a MongoClient to connect to the replica set
        client = MongoClient("mongodb://mongo.one.db:27017,mongo.two.db:27017,mongo.three.db:27017/?replicaSet=dbrs")

        # Access a specific database (or create it if it doesn't exist)
        db = client["your_database_name"]

        # Create a capped collection (this will create the database)
        if "your_capped_collection_name" not in db.list_collection_names():
            db.create_collection("your_capped_collection_name", capped=True, size=100000)

        # Create a TTL collection (this will create the database)
        if "your_ttl_collection_name" not in db.list_collection_names():
            db.create_collection("your_ttl_collection_name")

            # Create a TTL index on a field named "expireAt" (for automatic document expiration)
            db["your_ttl_collection_name"].create_index([("expireAt", ASCENDING)], expireAfterSeconds=0)

        return db

    except ServerSelectionTimeoutError as e:
        # Handle any connection errors
        raise Exception("Failed to connect to the MongoDB replica set") from e




@app.route('/animals', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_animals():
    try:
        db = get_db()
        query_params = request.args.to_dict()
        if request.method == 'GET':
            if "_id" in query_params:
                animal = db.animal_tb.find_one({"_id": ObjectId(query_params["_id"])})
                if animal:
                    # Convert ObjectId to a string for JSON serialization
                    animal["_id"] = str(animal["_id"])
                    return jsonify(animal)
                else:
                    return jsonify({"error": "No animals found with the specified _id"}, 404)

            if not query_params:
                # If there are no query parameters, return all animals
                animals = list(db.animal_tb.find())
                if animals:
                    for animal in animals:
                        # Convert ObjectId to a string for JSON serialization
                        animal["_id"] = str(animal["_id"])
                    return jsonify({"animals": animals})
                else:
                    return jsonify({"error": "No animals found"}, 404)

        # Handle POST, PUT, and DELETE requests...
        if request.method == 'POST':
            # Create a new animal
            data = request.json
            db.animal_tb.insert_one(data)
            return "Animal added successfully"
            clear_cache()

        if request.method == 'PUT':
            # Check if "_id" is in the query parameters
            if "_id" in query_params:
                # Use ObjectId to search by "_id" field
                animal_id = query_params["_id"]
                data = request.json
                result = db.animal_tb.update_one({"_id": ObjectId(animal_id)}, {"$set": data})
                if result.modified_count > 0:
                    return "Animal updated successfully."
                    clear_cache()
                else:
                    return jsonify({"error": "No animals found with the specified _id for update"}, 404)

        if request.method == 'DELETE':
            # Check if "_id" is in the query parameters
            if "_id" in query_params:
                # Use ObjectId to search by "_id" field
                animal_id = query_params["_id"]
                result = db.animal_tb.delete_one({"_id": ObjectId(animal_id)})
                if result.deleted_count > 0:
                    clear_cache()
                    return "Animal deleted successfully."
                else:
                    return jsonify({"error": "No animals found with the specified _id for delete"}, 404)

    except ServerSelectionTimeoutError as e:
        return jsonify({"error": "Failed to connect to the MongoDB cluster"}, 500)

    except Exception as e:
        return jsonify({"error": str(e)}, 500)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
