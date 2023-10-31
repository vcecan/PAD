Laboratory work for PAD UTM 4th year

### 1:open terminal and run :
docker-compose up --build -d --scale app=3

### 2 Initiate replica set
docker exec -it mongo.one.db mongosh --eval "rs.initiate({_id:'dbrs', members: [{_id:0, host: 'mongo.one.db'},{_id:1, host: 'mongo.two.db'},{_id:2, host: 'mongo.three.db'}]})"

### evaluate the status 
docker exec -it mongo.one.db mongosh --eval "rs.status()"   



