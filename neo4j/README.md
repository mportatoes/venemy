## Neo4j Setup
Download Neo4j from [here](https://neo4j.com/download/)

## Moving Your Files to the Right Location
Each database instance will have its own folder for files. You'll need to locate this directory and place your .csv's. Easiest way to do this is to select the down arrow next to "Open Folder" and choose "Import". This will open up the corresponding folder.

## Loading CSV Data Manually
### Loading Seed Data
    LOAD CSV WITH HEADERS FROM "file:///mmason.csv" as row
    MERGE (person:Person {id:row.venmo_id})
    ON CREATE SET person.username=row.username,person.display_name=row.display_name,person.friends_count=row.friends_count,person.date_joined=row.date_joined,person.phone=row.phone,person.email=person.email

### Loading Friend Data
    LOAD CSV WITH HEADERS FROM "file:///mmason_friends.csv" as row
    MATCH (p:Person {username:row.fvalue})
    MERGE (n:Person {username:row.username})
    ON CREATE SET n.id=row.venmo_id,n.display_name=row.display_name,n.date_joined=row.date_joined,n.phone=row.phone,n.email=row.email
    CREATE (n)-[r:friends_with]->(p)

### Loading Transaction Data
    LOAD CSV WITH HEADERS FROM "file:///mmason_trans.csv" as row
    MERGE (payor:Person {username:row.payor})
    ON CREATE SET payor.username=row.payor
    MERGE (payee:Person {username:row.payee})
    ON CREATE SET payee.username = row.payee
    CREATE (payor)-[d:paid {trans:row.item, id:row.id,time:row.date_updated}]->(payee)
    
## Running Test Queries
### Show Everything
    MATCH (n) RETURN n
### Show Friends in Common (if multiple people are loaded)
    Match (p:Person)-[:friends_with]->(q)<-[:friends_with]-(f:Person) RETURN p,q,f
### Show highest interaction transactions
    MATCH (p:Person)-[d:paid]->(q:Person) RETURN q.username,count(*) as c ORDER BY c DESC
### Show most common purchases
    MATCH (p:Person)-[d:paid]->(q:Person) RETURN q.username,d.trans,count(*) as c ORDER BY c DESC
### Show All Transactions
    MATCH (p:Person)-[d:paid]->(q:Person) RETURN *
### Show All Transactions Containing a Football
    MATCH (p:Person)-[d:paid]->(q:Person) WHERE d.trans =~'.*🏈.*' RETURN p,q
### Show Friends in Common (if using the crawl feature)
    MATCH (person)-[:friends_with]-(friend) WITH friend, count(*) AS friend_count WHERE friend_count > 1 RETURN friend,friend_count
