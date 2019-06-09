## Adding Pictures To Your Neo4j Nodes
Follow graphadvantage's instructions [here](https://github.com/graphadvantage/neo4j-browser-images) for installing the application in neo4j

For whatever reason, I couldn't get this to work directly within the neo4j browser but you can go to the package you downloaded and use the index.html file to act as an overlay. With your neo4j database up and running:
1. Navigate to C:\Users\your_username\.Neo4jDesktop\graphApps\neo4j-browser-image-enabled\dist
2. Click index.html to open in Chrome or Firefox
3. Provide your credentials to connect to your current database
4. You'll be providing a full filepath so can put your pictures wherever you want. For this demo, we'll stick them in: C:\Users\your_username\.Neo4jDesktop\graphApps\neo4j-browser-image-enabled\dist\assets\images
5. Provide a query to associate the pictures with the nodes:

       MATCH (n:MyImageNode)
       SET n.image_url = "file:///C:/Users/your_username/.Neo4jDesktop/graphApps/neo4j-browser-image-enabled/dist/assets/images/"+n.id+".jpg"
       RETURN n
       ### In this scenario, we are assuming we have an n.id=john and a file named john.jpg in our folder. You can match on anything, as long as the file is named accordingly
