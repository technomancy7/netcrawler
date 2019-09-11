# websearcher
Collection of utilities for searching the internets.

The idea is, one module containing various utilities and classes for getting information on various things from around the internet as simply as possible.
Most classes are WIP and are subject to change and expansion, I hope to add alot of utility functions to make getting important information quicker but still exposing the raw data.

## DuckDuckGo search

```py
from websearcher import *

#Takes optional constructor arg to define the user-agent that the site sees.
ddg = DuckDuckGo()
data = ddg.search('python')
#returns a dict of search results, dict contains keys for snippets, urls, titles

data = ddg.get('steve buscemi')
#returns a dict of information about a person, game, movie etc using DDG's Instant Answers API
```

## Startpage Search

```py
from websearcher import *

sp = Startpage()

pages = sp.search('python')
#returns a list of results from Startpage search engine
```

## Wikimedia

```py
from websearcher import *

wiki = Wiki()
description = wiki.identify('python')
#shows a description of an entity

summaries = wiki.summarieze('python')
#shows a summary of topics from wikimedias OpenSearch API

pages = wiki.query('python')
#searches wikipedia for pags, returns a list of found pages
```

## SCP

```py
from websearcher import *
print(SCPSite.search('001'))
#returns the raw data of the searched SCP
```

## ReverseImageSearch

```py
from websearcher import *
print(ReverseImageSearch().basic('an-image-URL'))
#returns what is in the image, e.i. a persons name 
```

## Gamefaqs

```py
from websearcher import *

#games searched are cached for current session to ease load on the site
gf = Gamefaqs()

deusex = gf.search('deus ex') #takes an optional arg to limit search by console
#returns a Game object 

deusex.news() #gets current news on the game
deusex.description() #shows the description of the game as it is on gamefaqs
deusex.details() #gets the information
deusex.trivia() #shows some trivia, is not always the same

#other pages and features such as cheats, faq links, images etc planned

```

## Pokeapi

```py
from websearcher import *
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
