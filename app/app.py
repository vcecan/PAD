from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import threading

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
    client = MongoClient(host='test_mongodb',
                        port=27017,
                        username='root',
                        password='pass',
                        authSource="admin")
    db = client["animal_db"]
    return db

@app.route('/animals', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_animals():
    db = get_db()
    try:
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



    except Exception as e:
        return str(e)
    



if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)