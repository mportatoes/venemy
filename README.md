# Venemy
An intelligence tool for Venmo. Presented at the Layer8 2019 conference. Use wisely - not responsible for any misuse.

# Venemy - Authenticated
The authenticated module allows for much more data to be collected. This module requires an API token (provided to all accounts - no additional signups). Look at the Request/Response headers and you will see an api_access_token in the cookie. Put this value into the script for the variable of the same name and run. Note that the token expires every 30 minutes. You can also script account creation - a valid API token is sent in the Reponse header before the account is verified. You can use the token for 30 minutes before having to create another fake account.

Venemy works best when OSINT has been performed and you've identified the person's profile/username. From there, it's easy to extend the tool's functionality. While there is a search API endpoint, I would recommend confirming the profile manually before running anything. You can also use the brute-force module in the unauthenticated script if you know the person's name or username.

## Usage:
#### Grab basic information from a user from the /user endpoint
    python3 venemy_auth.py --user UserName 

#### Grab the list of friends from the /user/[id]/friends API endpoint
    python3 venemy_auth.py --friends UserName

#### Grab the list of transactions from the /user/[id]/feed API endpoint
    python3 venemy_auth.py --trans UserName

#### Grab all the things - info, friends, transactions
    python3 venemy_auth.py --all UserName

#### Friend of a friend - provide a username. For each friend in that friend list (from the friend endpoint), it will grab their friend's list e.g. 2nd degree of separation)
    python3 venemy_auth.py --crawl UserName

# Venemy - Unauthenticated
If wanting to avoid creating an account, there's an option to use a few of the public API endpoints and some HTML scraping. Note that this module will not return someone's list of friends and only the last five transactions.

## Usage:
#### Brute-force for a profile - will try several variations of the person's name or suggested username (e.g. if they use they same username for multiple account/sites)
    python3 venemy_unauth.py --brute-force UserName or Person's name

#### Grab very basic information for a user
    python3 venemy_unauth.py --user UserName

#### Grab the list of transactions from the public site
    python3 venemy_unauth.py --trans UserName

# Reference:
[API Endpoints Guide](/reference/api_endpoints.md)

[Where's that API token again?](/reference/api_token)

[Adding pictures to your Neo4j nodes](/reference/neo4j_node_pictures.md)

[Layer8 presentation](/reference/venemy_layer8.pdf)
