import json
import random
import APCategoryLoader
import APAccountLoader
import APBroadcaster
import APCategoryList
import APItemLoader
import APEpgLoader
import APVodItem
import APCategory
import Provider

VIDEO_PREFIX = "/video/israelitv"
NAME = "Israeli TV Plugin"
ART = 'art-default.jpg'
ICON = 'icon-default.png'

PROVIDERS = {
  "Mako": Provider.Provider(
      "Mako",
      R("icon-mako.png"),
      R("art-mako.jpg"),
      {
        'pKey': '81d42db7c211bf9615a895c504',
        'accountId': '39',
        'broadcasterId': '24',
        'bundle': 'com.keshet.mako.VODandroid'
      }),
  "Reshet": Provider.Provider(
      "Reshet",
      R("icon-reshet.png"),
      R("art-reshet.jpg"),
      {
        'pKey':'a25129723d425516a51fe2910c',
        'accountId': '32',
        'broadcasterId':'1',
        'bundle':'com.applicaster.iReshetandroid'
      }),
  "Ten": Provider.Provider(
      "Ten",
      R("icon-nana.png"),
      R("art-nana.jpg"),
      {
        'pKey':'b52501f01699218ca6f6df33c1',
        'accountId': '69',
        'broadcasterId':'67',
        'bundle':'com.applicaster.il.tenandroid'
      }),
}

def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, listProviders, NAME, ICON, ART)
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  ObjectContainer.art = R(ART)
  # ObjectContainer.title1 = NAME
  ObjectContainer.view_group = "List"
  DirectoryObject.thumb = R(ICON)

  rand1 = int((random.random() * 8999) + 1000)
  rand2 = int((random.random() * 89) + 10)
  deviceId = '1d' + str(rand1) + 'd3b4f71c' + str(rand2)

  for (providerName, provider) in PROVIDERS.items():
    provider.properties['deviceId'] = deviceId

def listProviders():
  oc = ObjectContainer(title1="Israeli TV")

  for (providerName, provider) in PROVIDERS.items():
    rootId = getRootId(provider.properties)
    oc.add(DirectoryObject(
      key=Callback(
        listDirectories,
        providerName=providerName,
        categoryId=rootId,
        title=providerName,
        icon=provider.icon,
        art=provider.art),
      title=providerName,
      thumb=provider.icon,
      art=provider.art
    ))
  return oc

@route(VIDEO_PREFIX + '/listDirectories')
def listDirectories(providerName, categoryId, title, icon, art):
  title=unicode(title)
  categories = loadCategories(providerName, categoryId)
  oc = ObjectContainer(title1=title, art=art)
  for category in categories.getSubCategories():
    categoryTitle = category.getTitle()
    thumbnail = category.getThumbnail()

    Log("%s: %s" % (categoryTitle, thumbnail))
    if thumbnail is None or thumbnail == "":
      Log("%s: %s" % (categoryTitle, thumbnail))
      thumbnail = icon

    oc.add(DirectoryObject(
      key=Callback(
        listDirectories,
        providerName=providerName,
        categoryId=category.getId(),
        title=categoryTitle,
        icon=thumbnail,
        art=thumbnail),
      title=categoryTitle,
      summary=category.getDescription(),
      art=thumbnail,
      thumb=thumbnail))

  for item in categories.getVodItems():
    oc.add(VideoClipObject(
      key=Callback(getClip, providerName=providerName, itemId=item.getId()),
      rating_key=item.getId(),
      title=item.getTitle(),
      thumb=item.getThumbnail()))

  return oc


@route(VIDEO_PREFIX + '/getClip')
def getClip(providerName, itemId):
  itemLoader = APItemLoader.APItemLoader(PROVIDERS[providerName].properties, itemId)
  Log('ItemURL --> %s' % (itemLoader.getQuery()))
  jsonObject = itemLoader.loadURL()

#  Log(params.dumps(jsonObject, indent=2))

  item = APVodItem.APVodItem(jsonObject["vod_item"])

  streamUrl = item.getStreamUrl()
  Log("streamUrl: %s" % (streamUrl))
  clip = VideoClipObject(
    key=Callback(getClip, providerName=providerName, itemId=itemId),
    rating_key=itemId,
    title=item.getTitle(),
    thumb=item.getThumbnail(),
    summary=item.getDescription(),
    items=[
      MediaObject(
        optimized_for_streaming=True,
        parts=[
          PartObject(key = HTTPLiveStreamURL(Callback(PlayVideo, url=streamUrl)))
        ],
      )
    ])

  return ObjectContainer(objects=[clip], title2="Hello")

def getRootId(properties):
    accountLoader = APAccountLoader.APAccountLoader(properties)
    jsonAccountDictionary = accountLoader.loadURL()
    Log('accountURL --> %s' % (accountLoader.getQuery()))
    broadcaster = APBroadcaster.APBroadcaster(
        properties['broadcasterId'], jsonAccountDictionary["account"]["broadcasters"])
    rootId = broadcaster.getRootCategory()
    return rootId

def loadCategories(providerName, categoryId):
  categoryLoader = APCategoryLoader.APCategoryLoader(PROVIDERS[providerName].properties, categoryId)
  jsonCategoryDictionary = categoryLoader.loadURL()
  return APCategoryList.APCategoryList(jsonCategoryDictionary["category"])


def loadCategory(categoryId):
  categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
  jsonCategoryDictionary = categoryLoader.loadURL()
  return APCategory.APCategory(jsonCategoryDictionary["category"])

@indirect
def PlayVideo(url):
  Log.Debug("PlayVideo: " + url)
  request = HTTP.Request(url, follow_redirects=False)

  base = ""
  if url.find("m3u8") > -1: # direct stream, needs base
    index = url.rfind("/")
    base = url[0:index+1]

  playlist = GeneratePlaylist(request.content, base)
  cookie = request.headers['set-cookie']

  Log.Debug("Playlist:\n" + playlist)
  Log.Debug("Cookies:\n" + cookie)

  return IndirectResponse(
      VideoClipObject,
      key = HTTPLiveStreamURL(url),
      http_cookies = cookie
	)

def GeneratePlaylist(playlist, base):
  newPlaylist = '#EXTM3U'
  for line in playlist.splitlines()[1:-2]:
    if line.startswith('#'):
      # take it as is
      newPlaylist = newPlaylist + "\n" + line
    else:
      line = base + line
      newPlaylist = newPlaylist + "\n" + line

  return newPlaylist
