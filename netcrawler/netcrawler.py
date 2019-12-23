import requests
from bs4 import BeautifulSoup
import json
from os import path, system
import urllib.parse
from random import choice
from html import unescape
from collections import Counter
from urllib import parse

USERAGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"

try:
	from youtube_dl import YoutubeDL
	YTDL_ENABLED = True
except:
	YTDL_ENABLED = False
	
try:
	import aiohttp
	AIO_ENABLED = True
except:
	AIO_ENABLED = False
	
class NetcrawlerError(Exception):
	pass
	
class LinkCrawler:
	def __init__(self, *, parser='html5lib', useragent=USERAGENT):
		self.parser = parser
		self.cache = {}
		
		self.parsers = {
			'youtube.com': self._youtubeUnfurler,
			'imgur.com': self._imgurUnfurler,
			'gist.github.com': self._gistUnfurler,
			'stackoverflow.com': self._stackUnfurler,
			'duckduckgo.com': self._ddgUnfurler,
			'startpage.com': self._spUnfurler
		}
		
		self.payload = {
			'User-Agent': useragent
		}	

	def _ddgUnfurler(self, data):
		search = ""
		for item in data.query.split("&"):
			if item.startswith("q="):
				search = item.replace('q=', '')

		if search:
			return DuckDuckGo().search(search)
	
	def _spUnfurler(self, data):
		search = ""
		for item in data.query.split("&"):
			if item.startswith("query="):
				search = item.replace('query=', '')

		if search:
			return Startpage().search(search)

	def _stackUnfurler(self, data):
		try:
			_id = data.path.split("/")[2]
			site = data.netloc.split(".")[0]
			url = f"https://api.stackexchange.com/2.2/questions/{_id}?order=desc&sort=activity&site={site}"
			raw = requests.get(url, headers=self.payload, allow_redirects=True).json()
			return raw
		except Exception as e:
			print(e)
	
	def _youtubeUnfurler(self, data):
		if not YTDL_ENABLED:
			return {'error': 'Missing library! Youtube_DL is required to extract youtube information.'}
		
		if data.path == "/watch" and data.query:
			url = parse.urlunsplit(data)
			ytdlopts = {
				'format': 'bestaudio/best',
				'outtmpl': 'factory/%(extractor)s-%(id)s.%(ext)s',
				'restrictfilenames': True,
				'noplaylist': True,
				'nocheckcertificate': True,
				'ignoreerrors': False,
				'logtostderr': False,
				'quiet': True,
				'no_warnings': True,
				'default_search': 'ytsearch7',
				'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
			}
			
			with YoutubeDL(ytdlopts) as ydl:
				data = ydl.extract_info(url, download=False)
				filtered = {'author': data['uploader'], 'author_url': data['uploader_url'], 'title': data['title'], 'description': data['description'], 'image': data['thumbnail'], 'stream': data['url']}
				return filtered
		else:
			return {'title': 'YouTube Home'}
	
	def _imgurUnfurler(self, data):
		url = parse.urlunsplit(data)
		print(url)
		s = self.inspect(url)
		
		ret = {'title': s.title.text.strip()}
		if s.find('p') and s.find('p').text:
			ret['p'] = s.find('p').text.strip()
		
		if s.find('link') and s.find('link', rel='image_src'):
			ret['image'] = s.find('link', rel='image_src').get('href')
			
		return ret

	def _gistUnfurler(self, data):
		try:
			api = "https://api.github.com/gists/:id"
			api = api.replace(":id", data.path.split("/")[2])
			data = requests.get(api).json()
			gist = data['files'][list(data['files'].keys())[0]]
			return gist
		except Exception as e:
			print(e)
			
	def _genericUnfurler(self, data):
		url = parse.urlunsplit(data)
		s = self.inspect(url)
		
		ret = {'title': s.title.text.strip()}
		if s.find('p') and s.find('p').text:
			ret['p'] = s.find('p').text.strip()
			
		if s.find('span') and s.find('span').text:
			ret['span'] = s.find('span').text.strip()
			
		if s.find('img') and s.find('img').get('src'):
			ret['image'] = f"{url}{s.find('img').get('src')}"
			
		return ret
	
	def inspect(self, url):
		self.raw = requests.get(url, headers=self.payload, allow_redirects=True)
		self.parsed = BeautifulSoup(self.raw.text, self.parser)		
		return self.parsed
	
	def unfurl(self, link):	
		url = parse.urlsplit(link)
		loc = url.netloc.replace("www.", '')
		if self.cache.get(loc, None):
			return self.cache[loc]
	
		if len( url.path.split(".") ) > 1 and url.path.split(".")[1] in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
			return {'image': link}

		meth = self.parsers.get(loc, self._genericUnfurler)
		resp = meth(url)
		#if not resp:
			#resp = self._genericUnfurler(url)
		self.cache[loc] = resp
		return resp

class AsyncLinkCrawler(LinkCrawler):
	def __init__(self, *, parser='html5lib', useragent=USERAGENT):

		if AIO_ENABLED:
			self._async = _async
			raise NetcrawlerError("Asyncio networking not available. `aiohttp` library is missing.")
			return
			
		super().__init__(parser=parser, useragent=useragent)
		
		self.parsers = {
			'imgur.com': self._imgurUnfurler_a,
			'gist.github.com': self._gistUnfurler_a,
			'stackoverflow.com': self._stackUnfurler_a,
			'duckduckgo.com': self._ddgUnfurler_a,
			'startpage.com': self._spUnfurler_a
		}
		
	async def _ddgUnfurler_a(self, data):
		search = ""
		for item in data.query.split("&"):
			if item.startswith("q="):
				search = item.replace('q=', '')

		if search:
			return await DuckDuckGoAsync().search(search)
	
	async def _spUnfurler_a(self, data):
		search = ""
		for item in data.query.split("&"):
			if item.startswith("query="):
				search = item.replace('query=', '')

		if search:
			return await StartpageAsync().search(search)

	async def _stackUnfurler_a(self, data):
		try:
			_id = data.path.split("/")[2]
			site = data.netloc.split(".")[0]
			url = f"https://api.stackexchange.com/2.2/questions/{_id}?order=desc&sort=activity&site={site}"
			raw = requests.get(url, headers=self.payload, allow_redirects=True).json()
			return raw
		except Exception as e:
			print(e)
	
	async def _imgurUnfurler_a(self, data):
		url = parse.urlunsplit(data)
		s = await self.inspect(url)
		
		ret = {'title': s.title.text.strip()}
		if s.find('p') and s.find('p').text:
			ret['p'] = s.find('p').text.strip()
		
		if s.find('link') and s.find('link', rel='image_src'):
			ret['image'] = s.find('link', rel='image_src').get('href')
			
		return ret

	async def _gistUnfurler_a(self, data):
		try:
			api = "https://api.github.com/gists/:id"
			api = api.replace(":id", data.path.split("/")[2])
			#data = requests.get(api).json()
			async with aiohttp.ClientSession() as session:
				async with session.get(api) as r:
					data = await r.json()
					gist = data['files'][list(data['files'].keys())[0]]
					return gist
		except Exception as e:
			print(e)
			
	async def _genericUnfurler(self, data):
		url = parse.urlunsplit(data)
		s = await self.inspect(url)
		
		ret = {'title': s.title.text.strip()}
		if s.find('p') and s.find('p').text:
			ret['p'] = s.find('p').text.strip()
			
		if s.find('span') and s.find('span').text:
			ret['span'] = s.find('span').text.strip()
			
		if s.find('img') and s.find('img').get('src'):
			ret['image'] = f"{url}{s.find('img').get('src')}"
			
		return ret
	
	async def inspect(self, url):
		#self.raw = requests.get(url, headers=self.payload, allow_redirects=True)
		async with aiohttp.ClientSession() as session:
			async with session.get(url, headers=self.payload) as r:
				resp = await r.text()
				self.parsed = BeautifulSoup(resp, self.parser)		
				return self.parsed
	
	async def unfurl(self, link):	
		url = parse.urlsplit(link)
		loc = url.netloc.replace("www.", '')
		if self.cache.get(loc, None):
			return self.cache[loc]
	
		if len( url.path.split(".") ) > 1 and url.path.split(".")[1] in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
			return {'image': link}

		meth = self.parsers.get(loc, self._genericUnfurler)
		resp = await meth(url)
		#if not resp:
			#resp = await self._genericUnfurler(url)
		self.cache[loc] = resp
		return resp
		
class AtomReader:
	@staticmethod
	def parse(url):			
		data = requests.get(url).text
		#root = ET.fromstring(data)
		root = BeautifulSoup(data, 'xml')
		return Atom(root)
		
	@staticmethod
	async def async_parse(url):
		async with aiohttp.ClientSession() as session:
			async with session.get(api) as r:
				data = await r.text()
				root = BeautifulSoup(data, 'xml')
				return Atom(root)

class Atom:
	def __init__(self, data):
		self.data = data
				
class GoogleTrends:
	@staticmethod
	def get():
		url = "https://trends.google.com/trends/hottrends/atom/feed?pn=p1"
		return AtomReader.parse(url)		

class Blogger:
	def __init__(self, key, blog=None):
		self.key = key
		self.blog = blog
	
	def check(self, url=None):
		if not url and not self.blog:
			raise ValueError("No value for URL supplied. Must either be passed as a constructor for the Blogger class, or a paramater to get*.")
		
		return url or self.blog
	def get(self, url=None):
		url = self.check(url)
		return requests.get(f"https://www.googleapis.com/blogger/v3/blogs/byurl?key={self.key}&url={url}").json()	
	
	def getPosts(self, url=None):
		url = self.check(url)
		d = self.get(url)['posts']['selfLink']
		return requests.get(f"{d}?key={self.key}").json()	
		
	async def async_get(self, url=None):
		url = self.check(url)
		async with aiohttp.ClientSession() as session:
			async with session.get(f"https://www.googleapis.com/blogger/v3/blogs/byurl?key={self.key}&url={url}") as r:
				data = await r.json()
				return data
				
	async def async_getPosts(self, url=None):
		url = self.check(url)
		evt = await self.async_get(url)
		d = evt['posts']['selfLink']
		async with aiohttp.ClientSession() as session:
			async with session.get(f"{d}?key={self.key}") as r:
				data = await r.json()
				return data

class IGDB:
	def __init__(self, token):
		self.payload = {
		'user-key': f'{token}'
		}
		self.url = "https://api-v3.igdb.com/"
		#https://api-docs.igdb.com/?shell#game
		
	def games(self):
		payload = {}
		payload.update(self.payload)
		
		resp = requests.post(f"{self.url}games", headers=payload, data='fields age_ratings,aggregated_rating,aggregated_rating_count,alternative_names,artworks,bundles,category,collection,cover,created_at,dlcs,expansions,external_games,first_release_date,follows,franchise,franchises,game_engines,game_modes,genres,hypes,involved_companies,keywords,multiplayer_modes,name,parent_game,platforms,player_perspectives,popularity,pulse_count,rating,rating_count,release_dates,screenshots,similar_games,slug,standalone_expansions,status,storyline,summary,tags,themes,time_to_beat,total_rating,total_rating_count,updated_at,url,version_parent,version_title,videos,websites; search "deus ex";').text
		return json.loads(resp)	
		
	def engines(self):
		payload = {}
		payload.update(self.payload)
		
		resp = requests.post(f"{self.url}game_engines", headers=payload, data='fields companies,created_at,description,logo,name,platforms,slug,updated_at,url; search "unreal";').text
		print(resp)
		return json.loads(resp)	

class IMGUR:
	def __init__(self, client_id):
		self.payload = {
		'Authorization': f'Client-ID {client_id}'
		}
		
		self.search_url = "https://api.imgur.com/3/gallery/search/time/all/?q="
		self.gallery_url = "https://api.imgur.com/3/gallery/t/$TERM$/time/all/"
		self.reddit_url = "https://api.imgur.com/3/gallery/r/$TERM$/time/all/"	
	
		self.upload_url = "https://api.imgur.com/3/upload"
		
	def upload(self, path):
		with open(path, 'rb') as img:
			resp = requests.post(f"{self.upload_url}", headers=self.payload, files={'image': img}).text
			return json.loads(resp)
		
	def search(self, term):
		resp = requests.get(f"{self.search_url}{term}", headers=self.payload).text
		return json.loads(resp)

	def getRandom(self, term):
		items = self.search(term)
		return choice(items['data'])
		
	def gallery(self, term):
		resp = requests.get(f"{self.gallery_url.replace('$TERM$', term)}", headers=self.payload).text
		return json.loads(resp)

	def reddit(self, term):
		resp = requests.get(f"{self.reddit_url.replace('$TERM$', term)}", headers=self.payload).text
		return json.loads(resp)

	def redditRandom(self, term):
		items = self.reddit(term)
		return choice(items['data'])

class HeadlineSmasher:
	def __init__(self, *, useragent=USERAGENT):
		self.url = 'https://www.headlinesmasher.com/headlines/random'
		self.payload = {
			'User-Agent': useragent
		}
		self._async = _async
		
	def getRandom(self):
		self.raw = requests.get(self.url, headers=self.payload, allow_redirects=True)
		parsed = BeautifulSoup(self.raw.text, 'html5lib')		
		
		out = {}
		for item in parsed.find_all('meta'):
			if item.get('property') in ['og:title', 'og:url', 'og:description']:
				out[item.get('property').split(":")[1]] = item.get('content')
				
		return out
	
class Uguu:
	@staticmethod
	def upload(filepath):
		with open(filepath, 'rb') as img:
			resp = requests.post(f"https://uguu.se/api.php?d=upload-tool", files={'file': img, 'name':"upload"}).text
			return resp
	
class Wolfram:
	def __init__(self, app_id):
		self.appid = app_id
		self.conv_id = ""
		
		self.url = "http://api.wolframalpha.com/v1/conversation.jsp?"
		self.simple_url = "http://api.wolframalpha.com/v1/simple?"
		
	def image(self, message):
		args = f"appid={self.appid}"
		args += f"&i={urllib.parse.quote(message)}"
		return requests.get(self.simple_url+args).content
	
	def send(self, message):
		args = f"appid={self.appid}"
		
		if self.conv_id != "":
			args += f"&conversationid={self.conv_id}"
			
		args += f"&i={urllib.parse.quote(message)}"
		
		r = requests.get(self.url+args).text
		msg = json.loads(r)
		if msg.get('error'):
			return msg['error']
		
		if self.conv_id == "":
			self.conv_id = msg['conversationID']
			
		return msg['result']

class Youtube:
	def __init__(self, useragent=USERAGENT):
		print("NOT YET FUNCTIONAL")
		self.useragent = useragent
		self.cache = {}
		
	def search(self, search_term):
		if self.cache.get(search_term.lower(), None):
			return self.cache[search_term.lower()]
		
		payload = {
		'User-Agent':self.useragent
		}
		
		final_data = {'urls':[], 'descriptions':[], 'titles':[]}
		url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_term)}&page=&utm_source=opensearch"

		r = requests.get(url, headers=payload, allow_redirects=True).text
		s = BeautifulSoup(r, 'html.parser')
		results = s.find_all(['div'])

		for item in results:
			#print(item.get('class'))
			if item.get('class'):
				#print(item.get('class'))
				if "yt-lockup-content" in item.get('class'):
					#print(item)
					final_data['titles'].append(item.find('a').text.strip())
					final_data['descriptions'].append(item.get('span').text.strip())
					final_data['urls'].append(item.find('a').get('href'))
					
		sorted_data = []
		for i in range(0, len(final_data['urls'])):
			bundle_url = final_data['urls'][i]
			bundle_desc = final_data['descriptions'][i]
			bundle_title = final_data['titles'][i]
			sorted_data.append({'url': bundle_url, 'description': bundle_desc, 'title': bundle_title})
		
		self.cache[search_term.lower()] = sorted_data 
		return sorted_data		
	
class Startpage:
	def __init__(self, *, _async=False, useragent=USERAGENT):
		self.useragent = useragent
		self.cache = {}
		self.image_cache = {}
		
	def basic(self, search_term):
		return self.search(search_term)[0]['description']
	
	def basicURL(self, search_term):
		return self.search(search_term)[0]['url']
	
	def images(self, search_term):
		if self.image_cache.get(search_term.lower(), None):
			return self.image_cache[search_term.lower()]
		payload = {
		'User-Agent':self.useragent
		}

		url = f"https://www.startpage.com/do/search?lui=english&language=english&cat=pics&query={urllib.parse.quote(search_term)}"
		
		data = []
		r = requests.get(url, headers=payload).text
		s = BeautifulSoup(r, 'html.parser')
		results = s.find_all(['div'])
		for item in results:
			if item.get('class'):
				if "image-container" in item.get('class'):
					js = json.loads(item.get('data-img-metadata'))
					data.append({'title': js['title'] , 'description': js['description'], 'url': js['clickUrl']})
		
		self.image_cache[search_term.lower()] = data
		return data
	
	def search(self, search_term):
		if self.cache.get(search_term.lower(), None):
			return self.cache[search_term.lower()]
		
		payload = {
		'User-Agent':self.useragent
		}
		final_data = {'urls':[], 'descriptions':[], 'titles':[]}
		url = f"https://www.startpage.com/do/search?lui=english&language=english&cat=web&query={urllib.parse.quote(search_term)}"
		r = requests.get(url, headers=payload).text
		s = BeautifulSoup(r, 'html.parser')
		results = s.find_all(['div'])

		for item in results:
			if item.get('class'):
				if "w-gl__result" in item.get('class'):
					final_data['titles'].append(item.find('h3').text.strip())
					final_data['descriptions'].append(item.find('p').text.strip().split("\n\n")[0])
					final_data['urls'].append(item.find('a').get('href'))
					
		sorted_data = []
		for i in range(0, len(final_data['urls'])):
			bundle_url = final_data['urls'][i]
			bundle_desc = final_data['descriptions'][i]
			bundle_title = final_data['titles'][i]
			sorted_data.append({'url': bundle_url, 'description': bundle_desc, 'title': bundle_title})
		
		self.cache[search_term.lower()] = sorted_data 
		return sorted_data
	
class Pokedex:
	def __init__(self, *, image_cache = "cache"):
		self.cache = {'pokemon': {}, 'type': {}, 'pokemon-species': {}}
		self.base_url = "https://pokeapi.co/api/v2/"
		self.image_cache = image_cache
		if not path.isdir(self.image_cache):
			system(f"mkdir {self.image_cache}")
			
	def get(self, _type, _search):
		try:
			return self.cache[_type.lower()][_search.lower()]
		except KeyError:
			new_url = f"{self.base_url}{_type.lower()}/{_search.lower()}/"
			res = requests.get(new_url).text
			try:
				self.cache[_type.lower()][_search.lower()] = json.loads(res)
				return json.loads(res)
			except Exception as e:
				return {'name': f"ERROR: {type(e)}", 'error': e}
	
	def getTypes(self, pokemon):
		if type(pokemon) == str:
			pokemon = self.pokemon(pokemon)
		
		s = []
		for item in pokemon['types']:
			s.append(item['type']['name'])
			
		return s
	
	def getSprite(self, pokemon):
		if type(pokemon) == str:
			pokemon = self.pokemon(pokemon)
			
		if not self.image_cache:
			print("No image cache is defined, can't save images.")
			return
		
		if path.isfile(self.image_cache+pokemon['name'].lower()+'.gif'):
			pass
		else:
			image_url = pokemon['sprites']['front_default']
			with open(self.image_cache+pokemon['name'].lower(), "wb") as file:
				response = requests.get(image_url)
				file.write(response.content)
				
	def fetchType(self, type_name):
		return self.get('type', type_name)
	
	def typeEffectiveness(self, type_name):
		typeobj = self.get('type', type_name)
		
		effChart = {
			'double_damage_to': [],
			'double_damage_from': [],
			'half_damage_from': [],
			'half_damage_to': [],
			'no_damage_to': [],
			'no_damage_from': []
			}
		
		try:
			test = typeobj['damage_relations']['double_damage_to']
		except Exception as e:
			return {'name': type(e), 'error': e, 'dump': typeobj}
		
		for item in typeobj['damage_relations']['double_damage_to']:
			effChart['double_damage_to'].append(item['name'])

		for item in typeobj['damage_relations']['double_damage_from']:
			effChart['double_damage_from'].append(item['name'])
			
		for item in typeobj['damage_relations']['half_damage_from']:
			effChart['half_damage_from'].append(item['name'])
			
		for item in typeobj['damage_relations']['half_damage_to']:
			effChart['half_damage_to'].append(item['name'])

		for item in typeobj['damage_relations']['no_damage_to']:
			effChart['no_damage_to'].append(item['name'])
			
		for item in typeobj['damage_relations']['no_damage_from']:
			effChart['no_damage_from'].append(item['name'])			

		return effChart
	
	def fetchPokemon(self, pokemon_name):
		return Pokemon(self, self.get('pokemon', pokemon_name))
	
	def fetchSpecies(self, pokemon_name):
		return PokemonSpecies(self, self.get('pokemon-species', pokemon_name))

class PokemonSpecies:
	def __init__(self, dex, data):
		self.dex = dex
		self.data = data
		for item in self.data:
			setattr(self, item, self.data[item])
	
	def text(self, *, language='en', version=''):
		entries = self.flavor_text_entries
		results = []
		for item in entries:
			if item['language']['name'] == language:
				if version:
					if item['version']['name'] == version:
						results.append(item)
				else:
					results.append(item)
		
		return results
	
	def ftext(self, *, language='en', version=''):
		entries = self.flavor_text_entries
		results = []
		for item in entries:
			if item['language']['name'] == language:
				if version:
					if item['version']['name'] == version:
						results.append(item)
				else:
					results.append(item)
		
		return results[0]['flavor_text']
	
class Pokemon:
	def __init__(self, dex, data):
		self.dex = dex
		self.data = data
		for item in self.data:
			setattr(self, item, self.data[item])
	
		if self.species:
			self.species = self.dex.fetchSpecies(self.species['name'])
			
		self.types_list = []
		for item in self.types:
			self.types_list.append(item['type']['name'])
			
	def text(self):
		return self.species.ftext()
	
	def evolvesFrom(self):
		if self.species.evolves_from_species:
			return self.dex.fetchPokemon(self.species.evolves_from_species['name'])
	
	def sprite(self):
		self.dex.getSprite(self.name)
		
	#def species(self):
		#self.dex.fetchSpecies(self.species['name'])
		
	def spriteURL(self):
		return self.sprites['front_default']
	
	def getResists(self):
		res = []
		for item in self.types:
			for t in self.dex.typeEffectiveness(item['type']['name'])['no_damage_from']:
				res.append(t)
		return res
	
	def getDefends(self):
		res = []
		for item in self.types:
			for t in self.dex.typeEffectiveness(item['type']['name'])['half_damage_from']:
				res.append(t)
		return res	
	
	def getWeakness(self):
		res = []
		for item in self.types:
			for t in self.dex.typeEffectiveness(item['type']['name'])['double_damage_from']:
				res.append(t)
		return res		

class Wiki:
	def __init__(self):
		self.wikidata = "https://www.wikidata.org/w/api.php?"
		self.wikipedia = "https://en.wikipedia.org/w/api.php?"
		self.wikipedia_site = "https://en.wikipedia.org/wiki/"
		
	#Raw API call to retrieve entity information
	def data(self, search):
		res = json.loads(requests.get(f"{self.wikidata}action=wbsearchentities&format=json&search={urllib.parse.quote(search)}&language=en").text)
		try:
			_id = res['search'][0]['id']
			return self.dataId(_id)
		except IndexError:
			return None
		except KeyError:
			return None
	
	#Helper wrapper to get the description of any object input.
	def identify(self, obj):
		data = self.data(obj)
		for item in data['entities']:
			return data['entities'][item]['descriptions']['en']['value']
		
	#Same as .data but uses entity ID instead of searching by name
	def dataId(self, entityId):
		return json.loads(requests.get(f"{self.wikidata}action=wbgetentities&format=json&ids={entityId}").text)
	
	#Raw API call for opensearch protocol
	#Reformats the returned data because the way the API lays out the json is a bit strange
	def openSearch(self, value):
		data = json.loads(requests.get(f"{self.wikipedia}action=opensearch&search={value}").text)
		forms = {}
		ind = 0
		for item in data[1]:
			forms[item.lower()] = {'value':data[2][ind], 'url':data[3][ind]}
			ind += 1
		return forms
	
	#Helper wrapper for .openSearch to quickly get a summary of things.
	def summarize(self, value):
		en = self.openSearch(value)
		print(en)
		try:
			return en[value.lower()]	
		except KeyError:
			if len(en) > 0:
				return en[choice(list(en.keys()))]
			return {'error': 'Invalid search.'}
	
	#Queries wikipedia, returning a list of page summaries.
	def query(self, search, markdown = True):
		ret = []
		data = json.loads(requests.get(f"{self.wikipedia}action=query&prop=extracts&format=json&exintro=&titles={search}").text)
		for item in data['query']['pages']:
			cleaned = data['query']['pages'][item]['extract']
			#if markdown:
				#cleaned = md(cleaned)
			ret.append({'title': data['query']['pages'][item]['title'], 'text': cleaned})
		
		return ret
	
	def page(self, name):
		if not name.startswith("http"):
			url = self.wikipedia_site+name
		else:
			url = name
		
		#print(url)
		s = BeautifulSoup(requests.get(url, allow_redirects=True).text, 'html5lib')
		def get_disamb(tag):
			#print(tag.get('id'))
			return tag.has_attr('id') and tag.get('id') == 'disambigbox'
			
		dis = s.find_all(get_disamb)
		
		if dis:
			#print("DISAMBIGUOUS")
			a = s.find_all('li')
			full = []
			for item in a:
				if item.find('a') and item.find('a').get('href') and '/wiki/' in item.find('a').get('href') and ":" not in item.find('a').get('href') and item.find('a').get('href') != '/wiki/Main_Page':
					if item.get('class') and 'selected' in item.get('class'):
						break
						
					full.append(item.text)
			
			return {'disambig': full}
			
		results = s.find_all(['h2', 'p'])
		
		types = {}
		cur = 'Summary'
		cur_data = []
		for item in results:
			if item.text != "Contents" and item.text != "Navigation menu" and item != None and item.text != None:
				if item.name == "h2":
					types[cur] = cur_data
					cur_data = []
					cur = item.text.replace('[edit]', '')
				else:
					body = item.text.replace('[edit]', '')
					for i in range(0, 25):
						body = body.replace(f"[{i}]", '')
					cur_data.append(body)
					
		return types
	
class DuckDuckGo:
	def __init__(self, *, _async=False, useragent=USERAGENT):
		self.useragent = useragent
		self.cache = {}
		
	def get(self, search_term):
		res = requests.get(f"https://api.duckduckgo.com/?q={search_term}&no_redirect=1&format=json&pretty=1&t=Python-library").text
		data = json.loads(res)
		return data
	
	def basic(self, search_term):
		return self.search(search_term)[0]['description']
	
	def basicURL(self, search_term):
		return self.search(search_term)[0]['url']
	
	def search(self, search_term):
		if self.cache.get(search_term.lower(), None):
			return self.cache[search_term.lower()]
		
		payload = {
		'User-Agent':self.useragent
		}
		final_data = {'titles':[], 'snippets':[], 'urls': [], 'extras': {'snippets': [], 'urls': []}}
		url = f"https://duckduckgo.com/html?q={search_term}&t=ffab&atb=v162-6__&ia=web&iax=qa"
		r = requests.get(url, headers=payload).text
		s = BeautifulSoup(r, 'html.parser')
		divs = s.find_all(['div', 'a'])
		
		for item in divs:
			if item.get('class'):
				if "result__a" in item.get('class'):
					final_data['titles'].append(item.text.strip())
					
				if "result__snippet" in item.get('class'):
					final_data['snippets'].append(item.text.strip())
					
				if "result__url" in item.get('class'):
					final_data['urls'].append(item.text.strip())
					
				if "result__extras" in item.get('class'):
					final_data['extras']['snippets'].append(item.text.strip())
					
				if "result__extras__url" in item.get('class'):
					final_data['extras']['urls'].append(item.text.strip())
		
		
		sorted_data = []
		for i in range(0, len(final_data['urls'])):
			bundle_url = final_data['urls'][i]
			bundle_desc = final_data['snippets'][i]
			bundle_title = final_data['titles'][i]
			sorted_data.append({'url': bundle_url, 'description': bundle_desc, 'title': bundle_title})
		self.cache[search_term.lower()] = sorted_data 
		
		return sorted_data

class SCPSite:
	@staticmethod
	def search(term):
		base_url = f"http://www.scp-wiki.net/search:site/q/{term}"
		page = BeautifulSoup(requests.get(base_url).text, 'html5lib')
		result = None
		for div in page.find_all('div'):
			if div.get('class') and div.get('class')[0] == "search-results":
				result = div
		
		if not result:
			return None
		else:
			first = result.find_all('a')[0]
			return SCP(first.get('href'))
		
	@staticmethod		
	def fromURL(ext):
		base_url = f"http://www.scp-wiki.net/{ext}"
		return SCP(base_url)

class SCP:
	def __init__(self, url):
		self.url = url
		self.contents = []
		self.image = ""

		page = BeautifulSoup(requests.get(url).text, 'html5lib')
		self.title = page.find('head').find('title').text
		for div in page.find_all('div'):
			if div.get('id') and div.get('id') == "page-content":
				self.data = div
				
			if div.get('class') and div.get('class')[0] == "scp-image-block":
				self.image = div.find('img').get('src')

		for item in self.data.text.split('\n'):
			if item.strip():
				self.contents.append(item)
		
class ReverseImageSearch:
	def __init__(self, useragent=USERAGENT):
		self.useragent = useragent
	
	def get(self, img_url, count=0):
		url = "https://www.google.com/searchbyimage?hl=en-US&image_url="
		headers = {
		    'User-Agent': self.useragent,
		}

		return requests.get(f"{url}{img_url}&start={count}", headers=headers, allow_redirects=True).text

	def similar(self, img_url):
		q = self.get(img_url)
		soup = BeautifulSoup(q, 'html.parser')

		results = []

		for similar in soup.findAll('div', attrs={'rg_meta'}):
			results.append(json.loads(similar.get_text())['ou'])

		return results

	def basic(self, img_url):
		q = self.get(img_url)
		soup = BeautifulSoup(q, 'html.parser')
		for item in soup.findAll('a', attrs={'class':'fKDtNb'}):
			result = item.get_text()
		return result

	def related(self, img_url):
		count = 0
		keep_searching = True
		while keep_searching:
			q = self.get(img_url, count)
			soup = BeautifulSoup(q, 'html.parser')

			results = {
				'links': [],
				'descriptions': [],
			}
			for div in soup.findAll('div', attrs={'class':'rc'}):
				sLink = div.find('a')
				results['links'].append(sLink['href'])

			for desc in soup.findAll('span', attrs={'class':'st'}):
				results['descriptions'].append(desc.get_text())

			for link, description in zip(results["links"], results["descriptions"]):
				ret = {
					"link": link,
					"description": description
				}
				yield ret
			count += 10
			check_end_cur = soup.find("td", attrs={"class": "cur"})
			try:
				test = check_end_cur.next_sibling.td
			except AttributeError:
				keep_searching = False

class Gamefaqs:
	"""Gamefaqs.search("name") -> web scrape 
	view-source:https://gamefaqs.gamespot.com/search?game=deus+ex
	-> returns the url ID which is then passed to the parser class for a Game page"""
	def __init__(self, *, useragent=USERAGENT):
		self.base_url = "https://gamefaqs.gamespot.com/search?game="
		self.headers = {
		'User-Agent':useragent
		}
		self.cache = {}
		
	def search(self, game, *, console=""):
		if self.cache.get(game):
			print("Pulling from cache...")
			return self.cache[game]
		
		url = f"{self.base_url}{game.replace(' ', '+')}"
		
		searchpage = BeautifulSoup(requests.get(url, headers=self.headers).text, 'html5lib')
		ls = searchpage.find_all('div')

		for item in ls:
			if item.get('class'):
				if item.get('class')[0] == "sr_product_name":
					nurl = item.a.get('href')
					if console:
						if console == nurl.split("/")[1]:
							gobj = Game(nurl, self.headers)
							self.cache[game] = gobj
							return gobj
					else:
						gobj = Game(nurl, self.headers)
						self.cache[game] = gobj
						return gobj
					
		raise Exception("No game was found.")
		
class Game:
	def __init__(self, gamepage_url, headers):
		self.url = f"https://gamefaqs.gamespot.com{gamepage_url}"
		self.headers = headers

		self.html = BeautifulSoup(requests.get(self.url, headers=self.headers).text, 'html5lib')
		self.cache = {}
		self.cheatsurl = f"{self.url}/cheats"
		self.faqsurl = f"{self.url}/faqs"
		self.reviewsurl = f"{self.url}/reviews"
		self.imagesurl = f"{self.url}/images"
		self.answersurl = f"{self.url}/answers"
		self.videosurl = f"{self.url}/videos"
		
		self.title = self.html.find('title').text

	def news(self):
		if self.cache.get('news'):
			return self.cache['news']
		
		ls = self.html.find_all()
		searching = False
		found = []
		for item in ls:
			
			if item.get('class'):
				if item.get('class')[0] == "head":
					searching = False
					
				if searching:
					if item.get('class')[0] != 'name' and item.get('class')[0] != 'body' and item.get('class')[0] != 'pod' and item.get('class')[0] != 'sub':
						found.append(item)
					
				if item.text == "Game News":
					searching = True
		msg = ""
		for item in found:
			msg += f"{item.text.split('Updated')[0]}\n"
		
		self.cache['news'] = msg
		return msg
	
	def description(self):
		if self.cache.get('description'):
			return self.cache['description']
		
		ls = self.html.find_all('div')

		for item in ls:
			if item.get('class') == ['body', 'game_desc']:
				
				self.cache['description'] = item.text
				return item.text
			
	def ratings(self):
		pass
	
	def details(self):
		if self.cache.get('details'):
			return self.cache['details']
		
		dets = ""
		ls = self.html.find_all('div')

		for item in ls:
			if item.get('class') == ['pod', 'pod_gameinfo']:
				for thing in item.find_all(['h2', 'li']):
					if thing.get_text(' ', strip=True) != "Game Detail":
						print(thing.get_text(' ', strip=True))
						dets += f"{thing.get_text(' ', strip=True)}\n"
					
		self.cache['details'] = dets
		return dets
	
	def trivia(self):
		if self.cache.get('trivia'):
			return self.cache['trivia']
		
		trivs = self.html.find_all('p')
		for item in trivs:
			if item.get('class'):
				if item.get('class')[0] == 'trivia':
					self.cache['trivia'] = item.text
					return item.text
	
	def cheats(self):
		if self.cache.get('cheats'):
			return self.cache['cheats']

		html = BeautifulSoup(requests.get(self.cheatsurl, headers=self.headers, allow_redirects=True).text, 'html5lib')
		

		cheats = html.find_all('script')
		for item in cheats:

			if item.get('type') and item.get('type') == 'application/ld+json':
				item = item.text.replace('<script type="application/ld+json">', '')
				item = item.replace('</script>', '')
				js = json.loads(item)
				if js.get('@type') == "VideoGame":
					for en in js['gameTip']:
						en['text'] = unescape(en['text'])
						en['text'] = en['text'].replace('&quot;', '"')
						en['text'] = en['text'].replace('<br />', '\n')
					self.cache['cheats'] = js
					return js
				
	def faqs(self):
		if self.cache.get('faqs'):
			return self.cache['faqs']

		html = BeautifulSoup(requests.get(self.faqsurl, headers=self.headers, allow_redirects=True).text, 'html5lib')
		faqs = html.find_all('a')
		res = []
		en = {}
		for item in faqs:
			if item.get('href') and "/faqs/" in item.get('href'):
				en['url'] = f"https://gamefaqs.gamespot.com{item.get('href')}"
			if item.get('href') and "/community/" in item.get('href'):	
				en['author'] = f"https://gamefaqs.gamespot.com{item.get('href')}"
				en['author_name'] = item.string	

			if en.get('author') and en.get('url'):
				res.append(FAQ(en, self.headers))
				en = {}

		self.cache['faqs'] = res
		return res
	
	def reviews(self):
		pass
	
	def images(self):
		if self.cache.get('images'):
			return self.cache['images']

		html = BeautifulSoup(requests.get(self.imagesurl, headers=self.headers, allow_redirects=True).text, 'html5lib')
		
		results = {'box': [], 'screens': [], 'unknown': []}
		images = html.find_all('a')
		for item in images:
			if item.get('href') and "/images/" in item.get('href'):
				url = item.find('img').get('src')
				if "/box/" in url:
					results['box'].append(url)
				elif "/screens/" in url:
					results['screens'].append(url)
				else:
					results['unknown'].append(url)
		
		self.cache['images'] = results
		return results
	
	def answers(self):
		pass	

class FAQ:
	def __init__(self, payload, headers):
		self.url = payload.get('url')
		self.author = payload.get('author')
		self.author_url = payload.get('author_url')
		self.html = ""
		self.headers = headers
		
	def text(self):
		if self.html:
			return self.html
		
		html = BeautifulSoup(requests.get(self.url, headers=self.headers, allow_redirects=True).text, 'html5lib')
		
		for item in html.find_all('pre'):
			if item.get('id') == "faqtext":
				self.html = item.text
				return item.text
		
	def assumeHeader(self):
		c = Counter(self.text().split("\n"))
		return list(c.keys()[1])

	def find(self, term, breakln=""):
		if type(breakln) == str and breakln.isdigit():
			breakln = int(breakln)
		text = self.text()
		capt = []
		running = False
		for item in text.split("\n"):
			if term in item:
				running = True
			if running:
				capt.append(item)
			if type(breakln) == str:
				if item == breakln:
					running = False
			if type(breakln) == int:
				if breakln == len(capt):
					running = False
		return capt
