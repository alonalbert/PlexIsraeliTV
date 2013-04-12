import random
import APCategoryLoader
import APAccountLoader
import APBroadcaster
import APCategoryList
import APItemLoader
import APEpgLoader
import APVodItem
import APCategory

VIDEO_PREFIX = "/video/mako"
NAME = "Mako Plugin"
ART = 'art-default-2.jpg'
ICON = 'icon-default-2.png'

PROVIDERS = {
  "Mako": {'pKey': '81d42db7c211bf9615a895c504', 'accountId': '39', 'broadcasterId': '24',
           'bundle': 'com.keshet.mako.VODandroid'},
  "Mako2": {'pKey': '81d42db7c211bf9615a895c504', 'accountId': '39', 'broadcasterId': '24',
           'bundle': 'com.keshet.mako.VODandroid'}
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


def getRootId(properties):
  accountLoader = APAccountLoader.APAccountLoader(properties)
  jsonAccountDictionary = accountLoader.loadURL()
  Log('accountURL --> %s' % (accountLoader.getQuery()))
  broadcaster = APBroadcaster.APBroadcaster(
    properties['broadcasterId'], jsonAccountDictionary["account"]["broadcasters"])
  rootId = broadcaster.getRootCategory()
  return rootId


def listProviders():
  oc = ObjectContainer(title1="Israeli TV")

  for (provider, properties) in PROVIDERS.items():
    rootId = getRootId(properties)
    oc.add(DirectoryObject(
      key=Callback(listDirectories, provider=provider, categoryId=rootId, title=provider),
      title=provider
    ))
  return oc


@route('/video/mako/listDirectories')
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


def getClip(provider, itemId):
  itemLoader = APItemLoader.APItemLoader(PROVIDERS[provider], itemId)
  Log('ItemURL --> %s' % (itemLoader.getQuery()))
  jsonItemDictionary = itemLoader.loadURL()
  item = APVodItem.APVodItem(jsonItemDictionary["vod_item"])

  clip = VideoClipObject(
    key=Callback(getClip, itemId=itemId),
    rating_key=itemId,
    title=item.getTitle(),
    thumb=item.getThumbnail(),
    summary=item.getDescription(),
    items=[
      MediaObject(
        parts=[
          PartObject(key=item.getStreamUrl())
        ],
      )
    ])

  return ObjectContainer(objects=[clip], title2="Hello")


@route('/video/mako/listShows')
def listShows():
  accountLoader = APAccountLoader.APAccountLoader(PROPERTIES)
  jsonAccountDictionary = accountLoader.loadURL()
  Log('accountURL --> %s' % (accountLoader.getQuery()))
  broadcaster = APBroadcaster.APBroadcaster(PROPERTIES['broadcasterId'],
                                            jsonAccountDictionary["account"]["broadcasters"])
  Log('Main Category --> %s' % (broadcaster.getRootCategory()))
  categories = loadCategories(broadcaster.getRootCategory())
  oc = ObjectContainer(title2="Mako")
  for category in categories.getSubCategories():
    oc.add(TVShowObject(
      key=Callback(listSeasons, showId=category.getId(), showName=category.getTitle()),
      rating_key=category.getId(),
      title=category.getTitle(),
      summary=category.getDescription(),
      thumb=category.getThumbnail()))
  return oc


@route('/video/mako/listSeasons')
def listSeasons(showId, showName):
  showName = unicode(showName)
  categories = loadCategories(showId)
  oc = ObjectContainer(title2=showName)
  seasonNum = 0
  for category in categories.getSubCategories():
    seasonNum += 1
    oc.add(SeasonObject(
      key=Callback(listEpisodes, seasonId=category.getId(), showId=showId, showName=showName,
                   seasonName=category.getTitle()),
      rating_key=category.getId(),
      show=showName,
      index=seasonNum,
      title=category.getTitle(),
      summary=category.getDescription(),
      thumb=category.getThumbnail()))
  return oc


@route('/video/mako/listEpisodes')
def listEpisodes(seasonId, showId, showName, seasonName):
  showName = unicode(showName)
  seasonName = unicode(seasonName)
  categories = loadCategories(seasonId)
  oc = ObjectContainer(title1=showName, title2=showName + " - " + seasonName)
  episodeNum = 0
  for item in categories.getVodItems():
    episodeNum += 1
    oc.add(EpisodeObject(
      key=Callback(getEpisode, episodeId=item.getId(), seasonId=seasonId, showId=showId, showName=showName,
                   seasonName=seasonName),
      rating_key=item.getId(),
      title=item.getTitle(),
      show=showName,
      index=episodeNum,
      thumb=item.getThumbnail()))
  return oc


def getEpisode(episodeId, seasonId, showId, showName, seasonName):
  showName = unicode(showName)
  seasonName = unicode(seasonName)

  itemLoader = APItemLoader.APItemLoader(PROPERTIES, episodeId)
  Log('ItemURL --> %s' % (itemLoader.getQuery()))
  jsonItemDictionary = itemLoader.loadURL()
  item = APVodItem.APVodItem(jsonItemDictionary["vod_item"])

  thumbnail = item.getThumbnail()
  Log("Thumbnail: " + thumbnail)
  if thumbnail is None or thumbnail == "":
    Log("Thumbnail: " + thumbnail)
    thumbnail = loadCategory(seasonId).getThumbnail()
    if thumbnail is None or thumbnail == "":
      Log("Thumbnail: " + thumbnail)
      thumbnail = loadCategory(showId).getThumbnail()

  episode = EpisodeObject(
    key=Callback(getEpisode, episodeId=episodeId, seasonId=seasonId, showId=showId, showName=showName,
                 seasonName=seasonName),
    rating_key=episodeId,
    title=showName + " - " + seasonName + " - " + item.getTitle(),
    thumb=thumbnail,
    summary=item.getDescription(),
    items=[
      MediaObject(
        parts=[
          PartObject(key=item.getStreamUrl())
        ],
      )
    ])

  return ObjectContainer(objects=[episode], title2="Hello")


def loadCategories(provider, categoryId):
  categoryLoader = APCategoryLoader.APCategoryLoader(PROVIDERS[provider], categoryId)
  jsonCategoryDictionary = categoryLoader.loadURL()
  return APCategoryList.APCategoryList(jsonCategoryDictionary["category"])


def loadCategory(categoryId):
  categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
  jsonCategoryDictionary = categoryLoader.loadURL()
  return APCategory.APCategory(jsonCategoryDictionary["category"])

