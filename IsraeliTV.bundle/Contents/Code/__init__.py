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

VIDEO_PREFIX = "/video/israelitv"
NAME = "Israeli TV Plugin"
ART = 'art-default.jpg'
ICON = 'icon-default.png'

PROVIDERS = {
  "Mako": {'pKey': '81d42db7c211bf9615a895c504', 'accountId': '39', 'broadcasterId': '24', 'bundle': 'com.keshet.mako.VODandroid'},
  "Ten": {'pKey':'b52501f01699218ca6f6df33c1', 'accountId': '69', 'broadcasterId':'67', 'bundle':'com.applicaster.il.tenandroid'}
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

  for (provider, properties) in PROVIDERS.items():
    properties['deviceId'] = deviceId


def listProviders():
  oc = ObjectContainer(title1="Israeli TV")

  for (provider, properties) in PROVIDERS.items():
    rootId = getRootId(properties)
    oc.add(DirectoryObject(
      key=Callback(listDirectories, provider=provider, categoryId=rootId, title=provider),
      title=provider
    ))
  return oc

@route(VIDEO_PREFIX + '/listDirectories')
def listDirectories(provider, categoryId, title):
  title=unicode(title)

  categories = loadCategories(provider, categoryId)
  oc = ObjectContainer(title1=title)
  for category in categories.getSubCategories():
    categoryTitle = category.getTitle()
    Log("categoryTitle: " + categoryTitle)
    oc.add(DirectoryObject(
      key=Callback(listDirectories, provider=provider, categoryId=category.getId(), title=categoryTitle),
      title=categoryTitle,
      summary=category.getDescription(),
      thumb=category.getThumbnail()))

  for item in categories.getVodItems():
    oc.add(VideoClipObject(
      key=Callback(getClip, provider=provider, itemId=item.getId()),
      rating_key=item.getId(),
      title=item.getTitle(),
      thumb=item.getThumbnail()))

  return oc


@route(VIDEO_PREFIX + '/getClip')
def getClip(provider, itemId):
  itemLoader = APItemLoader.APItemLoader(PROVIDERS[provider], itemId)
  Log('ItemURL --> %s' % (itemLoader.getQuery()))
  jsonObject = itemLoader.loadURL()

#  Log(params.dumps(jsonObject, indent=2))

  item = APVodItem.APVodItem(jsonObject["vod_item"])

  streamUrl = item.getStreamUrl()
  Log("streamUrl: %s" % (streamUrl))
  clip = VideoClipObject(
    key=Callback(getClip, provider=provider, itemId=itemId),
    rating_key=itemId,
    title=item.getTitle(),
    thumb=item.getThumbnail(),
    summary=item.getDescription(),
    items=[
      MediaObject(
        parts=[
          PartObject(key=streamUrl)
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

def loadCategories(provider, categoryId):
  categoryLoader = APCategoryLoader.APCategoryLoader(PROVIDERS[provider], categoryId)
  jsonCategoryDictionary = categoryLoader.loadURL()
  return APCategoryList.APCategoryList(jsonCategoryDictionary["category"])


def loadCategory(categoryId):
  categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
  jsonCategoryDictionary = categoryLoader.loadURL()
  return APCategory.APCategory(jsonCategoryDictionary["category"])

