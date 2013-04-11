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
NAME = "Mako"
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
  MediaContainer.art = R(ART)
  MediaContainer.title1 = NAME
  MediaContainer.viewGroup = "List"
  DirectoryItem.thumb = R(ICON)

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
          key = Callback(listSeasons, categoryId=category.getId(), showName=category.getTitle()),
          rating_key = category.getId(),
          title = category.getTitle(),
          summary = category.getDescription(),
          thumb = category.getThumbnail()))
  return oc

def listSeasons(categoryId, showName):
  categories = loadCategories(categoryId)
  oc = ObjectContainer(title2 = showName)
  seasonNum = 0
  for category in categories.getSubCategories():
    seasonNum += 1
    oc.add(SeasonObject(
      key = Callback(listEpisodes, categoryId=category.getId(), showName = showName, seasonName=category.getTitle(), seasonNum=seasonNum),
      rating_key = category.getId(),
      show = showName,
      index = seasonNum,
      title = category.getTitle(),
      summary = category.getDescription(),
      thumb = category.getThumbnail()))
  return oc


def listEpisodes(categoryId, showName, seasonName, seasonNum):
  categories = loadCategories(categoryId)
  oc = ObjectContainer(title2 = showName + " - " + seasonName)
  episodeNum = 0
  for item in categories.getVodItems():
    episodeNum += 1
    oc.add(EpisodeObject(
      key = Callback(getEpisode, episodeId=item.getId(), showName = showName, seasonName = seasonName),
      rating_key = item.getId(),
      title = item.getTitle(),
      show = showName,
      index = episodeNum,
      thumb = item.getThumbnail()))
  return oc


@route('/video/mako/getEpisode')
def getEpisode(episodeId, showName, seasonName):
  itemLoader = APItemLoader.APItemLoader(PROPERTIES, episodeId)
  Log('ItemURL --> %s' % (itemLoader.getQuery()))
  jsonItemDictionary = itemLoader.loadURL()
  item = APVodItem.APVodItem(jsonItemDictionary["vod_item"])

  episode = EpisodeObject(
      key = Callback(getEpisode, episodeId=episodeId, showName = showName, seasonName = seasonName),
      rating_key = episodeId,
      title = showName + " - " + seasonName + " - " + item.getTitle(),
      thumb = item.getThumbnail(),
      summary = item.getDescription(),
      items = [
          MediaObject(
              parts = [
                  PartObject(key=item.getStreamUrl())
              ],
              container = Container.MP4,
              video_codec = VideoCodec.H264,
              audio_codec = AudioCodec.AAC,
              audio_channels = 2,
          )
      ])

  return ObjectContainer(objects=[episode], title2="Hello")

def loadCategories(categoryId):
    categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
    jsonCategoryDictionary = categoryLoader.loadURL()
    categories = APCategoryList.APCategoryList(jsonCategoryDictionary["category"])
    return categories

