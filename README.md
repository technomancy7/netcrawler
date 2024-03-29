# netcrawler
Collection of utilities for searching the internets.

The idea is, one module containing various utilities and classes for getting information on various things from around the internet as simply as possible.
Most classes are WIP and are subject to change and expansion, I hope to add alot of utility functions to make getting important information quicker but still exposing the raw data.
Each site is also subject to its own rules and terms of service. Abusing the calls or spamming the sites or harvesting large amounts of data could get you blocked depending on the sites terms. I take no responsibility for that. Just use common sense and be sensible about it.

## DuckDuckGo search
DuckDuckGo is an alternate search engine focused on privacy.
```py
from netcrawler import *

#Takes optional constructor arg to define the user-agent that the site sees.
ddg = DuckDuckGo()
data = ddg.search('python')
#returns a list of search results, each entry is a dict contains keys for description, url, title

data = ddg.get('steve buscemi')
#returns a dict of information about a person, game, movie etc using DDG's Instant Answers API
```

## Startpage Search
Startpage is another search engine.
```py
from netcrawler import *

sp = Startpage()

pages = sp.search('python')
#returns a list of search results, each entry is a dict contains keys for description, url, title

images = sp.images('steve buscemi')
# returns a list of dict entries, same format as normal search, but the urls are images pulled from Image Search
```

## IMGUR search
IMGUR is a popular image hosting service.
```py
from netcrawler import *

#Takes required constructor arg to provide your own app id, obtained from registering on the site.
img = IMGUR('your-app-id')

data = img.search('steve buscemi')
#returns a dict of search results

data = img.getRandom('christopher walken')
#returns a random image

data = img.gallery('steve buscemi')
#returns a dict of a specific gallery on imgur

data = img.reddit('aww')
#returns a dict of images pulled from reddit

data = img.randomReddit('aww')
#returns a random image

img.upload('/path/to/image')
#uploads an image to your account
```

## Uguu file upload
```
Uguu.upload('/path/to/file')
#returns a URL to the uploaded file
```

## Wolfram|Alpha query
A knowledge engine that contains answers to many things.
```py
from netcrawler import *

#Takes required constructor arg to provide your own app id, obtained from registering on the site.
wf = Wolfram('your-app-id')
print(wf.send('population of uk'))
#returns a plaintext qeury from wolfram alpha

img = wf.image('population of uk'))
#returns a raw image of data from wolfram

```

## Wikimedia
Utilities for interfacing with the Wiki services.
```py
from netcrawler import *

wiki = Wiki()
description = wiki.identify('python')
#shows a description of an entity

summaries = wiki.summarize('python')
#shows a summary of topics from wikimedias OpenSearch API

pages = wiki.query('python')
#searches wikipedia for term, returns a list of found pages
```

## SCP
Quick access to the SCP Foundation Wiki.
```py
from netcrawler import *
print(SCPSite.search('001'))
#returns the raw data of the searched SCP
```

## ReverseImageSearch
Calls to Googles Reverse Image Search
```py
from netcrawler import *
print(ReverseImageSearch().basic('an-image-URL'))
#returns what is in the image, e.i. a persons name

#Due to how google handles the service, theres no way to call this directly for files on your hard drive.
#A workaround for now would be using the Uguu class in this module to upload the file, get the URL from there, and use that for this.
```

## Gamefaqs
Various access to gamefaq's services.
```py
from netcrawler import *

#games searched are cached for current session to ease load on the site
#every call in each game is also cached
gf = Gamefaqs()

deusex = gf.search('deus ex') #takes an optional arg to limit search by console
#returns a Game object 

deusex.news() #gets current news on the game
deusex.description() #shows the description of the game as it is on gamefaqs
deusex.details() #gets the information
deusex.trivia() #shows some trivia, is not always the same
deusex.images() #returns a dict of images, with keys for `box` which is the games box arg, and `screen` which is screenshots
deusex.cheats() #returns a dict of cheats, with keys for author and text
faq = deusex.faqs() #returns a Faqs object, which has its own methods

faq.text() #returns the raw text body from the faqs page
faq.find('0.1 Controls') #finds the line containing the text and the following lines until the next break
faq.find('Augmentation', 5) #finds the first mention of the word and returns that line and the following 5 lines
faq.find('Ocean Lab', 'Area 51') #finds the first mention of the word, and every line after until the second arg is found
faq.author #string of the author's name
faq.author_url #direct profile link to the author

```

## Pokemon API
Wrapper for the Pokeapi service, which hosts data for everything you could possibly need to know about pokemon.
This is probably the most work-in-progress class. The API is very extensive and has alot of information, so for now i just wrapped the most useful features that I would use personally.

```py
from netcrawler import *
#Takes optional arg for cache location, used for downloading sprites
dex = Pokedex()

dex.get('pokemon', 'charmander')
#Raw function for getting the json data of a thing, first arg is the type, second is the search term

dex.getTypes('charmander')
#utility to return a list of pokemons types quickly

dex.getSprite('charmander')
#downloads a pokemons sprite to the image cache

dex.typeEffectiveness('fire')
#returns a dict of type effectiveness charts

charmander = dex.fetchPokemon('charmander')
#returns a POKEMON object

charmander.name #charmander
species = charmander.species #a Species object

charmander.text() #shows the pokedex flavour text, takes options keyword args for language and game name to find
charmander.evolesFrom() #returns a POKEMON object of this pokemons pre-evolved form
charmander.sprite() #quick utility to download the sprite of this function
charmander.spriteURL() #returns the URL of the sprite on the API server
charmander.getResists() #returns types that this pokemon resists fully
charmander.getDefends() #returns types that this pokemon takes half damage from
charmander.getWeakness() #returns types that this pokemon takes supereffective damage from
```
