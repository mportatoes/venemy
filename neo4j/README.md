## Neo4j Setup
Download Neo4j from [here](https://neo4j.com/download/)

## Moving Your Files to the Right Location
Each database instance will have its own folder for files. You'll need to locate this directory and place your .csv's. Easiest way to do this is to select the down arrow next to "Open Folder" and choose "Import". This will open up the corresponding folder.

## Loading CSV Data Manually
### Loading Seed Data
    LOAD CSV WITH HEADERS FROM "file:///username.csv" as row
    MERGE (person:Person {id:row.user})
    ON CREATE SET person.ext_id=row.external_id, person.username=row.username, person.name=row.name, person.date_created=row.date_created, person.biz=row.is_business, person.num_friends=person.num_friends, person.pic_url=row.picture_url

### Loading Friend Data
    LOAD CSV WITH HEADERS FROM "file:///username_friends.csv" as row
    MERGE (friend:Friend {id:row.user_id})
    ON CREATE SET friend.ext_id=row.external_id,friend.username=row.username,friend.name=row.name,friend.date_created=row.date_created,friend.biz=row.is_business,friend.num_friends=friend.num_friends,friend.pic_url=row.picture_url
    MERGE (person:Person {id:row.user})
    CREATE (person)-[r:friends_with]->(friend)

### Loading Transaction Data
    LOAD CSV WITH HEADERS FROM "file:///username_trans.csv" as row
    MERGE (actor:Payor {id:row.actor_id})
    ON CREATE SET actor.name=row.actor_username
    MERGE (target:Payee {id:row.target_id})
    ON CREATE SET target.name = row.target_username
    CREATE (actor)-[d:deals {trans:row.msg}]->(target)
    
## Running Test Queries
### Show Everything
    MATCH (n) RETURN n
### Show All Targets and Friends
    MATCH (person)-[:friends_with]->(friend) RETURN person,friend
### Show All Transactions
    MATCH (actor)-[d:deals]-(target) RETURN *
### Show Friends in Common (if using the crawl feature)
    MATCH (person)-[:friends_with]-(friend) WITH friend, count(*) AS friend_count WHERE friend_count > 1 RETURN friend,friend_count
