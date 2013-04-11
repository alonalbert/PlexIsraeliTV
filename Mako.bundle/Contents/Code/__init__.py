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

PROPERTIES = {'pKey': '81d42db7c211bf9615a895c504', 'accountId': '39', 'broadcasterId': '24',
                'bundle': 'com.keshet.mako.VODandroid'}

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
  # Initialize the plugin
  Plugin.AddPrefixHandler(VIDEO_PREFIX, listShows, NAME, ICON, ART)
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  # Setup the artwork associated with the plugin
  ObjectContainer.art = R(ART)
  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = "List"
  DirectoryObject.thumb = R(ICON)

  rand1 = int((random.random() * 8999) + 1000)
  rand2 = int((random.random() * 89) + 10)
  deviceId = '1d' + str(rand1) + 'd3b4f71c' + str(rand2)
  PROPERTIES['deviceId'] = deviceId

@route('/video/mako/listShows')
def listShows():
  accountLoader = APAccountLoader.APAccountLoader(PROPERTIES)
  jsonAccountDictionary = accountLoader.loadURL()
  Log('accountURL --> %s' % (accountLoader.getQuery()))
  broadcaster = APBroadcaster.APBroadcaster(PROPERTIES['broadcasterId'],
                                            jsonAccountDictionary["account"]["broadcasters"])
  Log('Main Category --> %s' % (broadcaster.getRootCategory()))
  categories = loadCategories(broadcaster.getRootCategory())
  oc = ObjectContainer(title2 = "Mako")

  for category in categories.getSubCategories():
      oc.add(TVShowObject(
          key = Callback(listSeasons, showId=category.getId(), showName=category.getTitle()),
          rating_key = category.getId(),
          title = category.getTitle(),
          summary = category.getDescription(),
          thumb = category.getThumbnail()))
  return oc

@route('/video/mako/listSeasons')
def listSeasons(showId, showName):
  showName = unicode(showName)
  categories = loadCategories(showId)
  oc = ObjectContainer(title2 = showName)
  seasonNum = 0
  for category in categories.getSubCategories():
    seasonNum += 1
    oc.add(SeasonObject(
      key = Callback(listEpisodes, seasonId=category.getId(), showId = showId, showName = showName, seasonName=category.getTitle()),
      rating_key = category.getId(),
      show = showName,
      index = seasonNum,
      title = category.getTitle(),
      summary = category.getDescription(),
      thumb = category.getThumbnail()))
  return oc


@route('/video/mako/listEpisodes')
def listEpisodes(seasonId, showId, showName, seasonName):
  showName = unicode(showName)
  seasonName = unicode(seasonName)
  categories = loadCategories(seasonId)
  oc = ObjectContainer(title1=showName,  title2 = showName + " - " + seasonName)
  episodeNum = 0
  for item in categories.getVodItems():
    episodeNum += 1
    oc.add(EpisodeObject(
      key = Callback(getEpisode, episodeId=item.getId(), seasonId = seasonId, showId = showId , showName = showName, seasonName = seasonName),
      rating_key = item.getId(),
      title = item.getTitle(),
      show = showName,
      index = episodeNum,
      thumb = item.getThumbnail()))
  return oc


def getEpisode(episodeId, seasonId, showId,  showName, seasonName):
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
      key = Callback(getEpisode, episodeId=episodeId, seasonId = seasonId, showId = showId , showName = showName, seasonName = seasonName),
      rating_key = episodeId,
      title = showName + " - " + seasonName + " - " + item.getTitle(),
      thumb =thumbnail,
      summary = item.getDescription(),
      items = [
          MediaObject(
              parts = [
                  PartObject(key=item.getStreamUrl())
              ],
          )
      ])

  return ObjectContainer(objects=[episode], title2="Hello")

def loadCategories(categoryId):
    categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
    jsonCategoryDictionary = categoryLoader.loadURL()
    return APCategoryList.APCategoryList(jsonCategoryDictionary["category"])

def loadCategory(categoryId):
    categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
    jsonCategoryDictionary = categoryLoader.loadURL()
    return APCategory.APCategory(jsonCategoryDictionary["category"])

