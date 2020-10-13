# Venemy
An intelligence tool for Venmo. Presented at Bsides Charleston 2019, Avengercon 2019, and Layer8 2019. Use wisely/be an infosec hero - not responsible for any misuse.

# Update 10/12/2020
It's been awhile since I've updated this and things have changed over at Venmo. This is *great*, actually from privacy and security perspectives. They've taken steps (albeit minor) to improve the security of their API and provided more transparency on user settings for making things private. Most of the API endpoints now require authentication. However, anyone with an account can get an API token and gain access to their API endpoints where they can gather all the things. I've updated this repo to account for the new oAuth process and accessing the updated API endpoints. Changes:
  - You can gain your API credentials directly from the script with the -a (or --auth) flag
  - Updated collected fields based on the API endpoints
  - Authenticated and Unauthenticated code merged into one
  - Full credit for the authentication code goes to [mmohades](https://github.com/mmohades/Venmo)

# Venemy - Authenticated
The authenticated module allows for much more data to be collected. This module requires an API token (provided to all accounts - no additional signups). Use the `--auth` flag to invoke this process and get your credentials. Once you've obtained the device-id and bearer token, update `venemy_auth.py` accordingly (see comments in code).

Venemy works best when OSINT has been performed, you've identified the person's profile/username, and you've completed the authentication process. From there, it's easy to extend the tool's functionality. While there is a search API endpoint, I would recommend confirming the profile manually before running anything.

## Usage:
#### Grab basic information from a user from the /user endpoint
    python venemy.py --user username

#### Grab the list of friends from the /user/[id]/friends API endpoint
    python venemy.py --friends username

#### Grab the list of transactions from the /user/[id]/feed API endpoint
    python venemy.py --trans username

#### Grab all the things - info, friends, transactions, and crawl 1 level
    python venemy.py --all username

#### Friend of a friend - provide a username. For each friend in that friend list (from the friend endpoint), it will grab their friend's list e.g. 2nd degree of separation)
    python venemy.py --crawl username
    
#### Add the --pic flag to the options above to download profile pictures
```python venemy_auth.py --friends username --pic```

# Venemy - Unauthenticated
If wanting to avoid creating an account, there's an option to use some HTML scraping.

## Usage:
#### Check a single username
    python venemy.py --noauth UserName

#### Brute-force for a profile - will try several variations of the person's name or suggested username (e.g. if they use they same username for multiple account/sites)
    python venemy.py --brute-force Person's name

# Reference:
[API Endpoints Guide](/reference/api_endpoints.md)

[Where's that API token again?](/reference/api_token)

[Adding pictures to your Neo4j nodes](/reference/neo4j_node_pictures.md)

[Layer8 presentation](/reference/venemy_layer8.pdf)
