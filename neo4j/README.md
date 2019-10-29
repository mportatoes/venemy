## Neo4j Setup
Download Neo4j from [here](https://neo4j.com/download/)

## Moving Your Files to the Right Location
Each database instance will have its own folder for files. You'll need to locate this directory and place your .csv's. Easiest way to do this is to select the down arrow next to "Open Folder" and choose "Import". This will open up the corresponding folder.

## Loading CSV Data Manually
### Loading Seed Data
    LOAD CSV WITH HEADERS FROM "file:///XXXXXX.csv" as row
    MERGE (person:Person {id:row.user})
    ON CREATE SET person.ext_id=row.external_id,person.username=row.username,person.name=row.name,person.date_created=row.date_created,person.biz=row.is_business,person.num_friends=person.num_friends,person.pic_url=row.picture_url

### Loading Friend Data
    LOAD CSV WITH HEADERS FROM "file:///XXXXXX_friends.csv" as row
    MATCH (p:Person {id:"XXXXXX"}) //This can be a variable
    MERGE (person:Person {id:row.user_id})
    ON CREATE SET person.ext_id=row.external_id,person.username=row.username,person.name=row.name,person.date_created=row.date_created,person.biz=row.is_business,person.num_friends=person.num_friends,person.pic_url=row.picture_url
    CREATE (p)-[r:friends_with]->(person)

### Loading Transaction Data
    LOAD CSV WITH HEADERS FROM "file:///35247548_trans.csv" as row
    MERGE (payor:Person {id:row.actor_id})
    ON CREATE SET payor.name=row.actor_username
    MERGE (payee:Person {id:row.target_id})
    ON CREATE SET payee.name = row.target_username
    CREATE (payor)-[d:paid {trans:row.msg, id:row.story_id,time:row.updated_time}]->(payee)
    
## Running Test Queries
### Show Everything
    MATCH (n) RETURN n
### Show Friends in Common
    Match (p:Person)-[:friends_with]->(q)<-[:friends_with]-(f:Person) RETURN p,q,f
### Show All Transactions
    MATCH (p:Person)-[d:paid]->(q:Person) 
### Show All Transactions Containing a Football
    MATCH (p:Person)-[d:paid]->(q:Person) WHERE d.trans =~'.*🏈.*' RETURN p,q
### Show Friends in Common (if using the crawl feature)
    MATCH (person)-[:friends_with]-(friend) WITH friend, count(*) AS friend_count WHERE friend_count > 1 RETURN friend,friend_count
