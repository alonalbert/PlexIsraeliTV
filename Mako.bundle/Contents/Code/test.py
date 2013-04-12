__author__ = 'al'

import random
import APCategoryLoader
import APAccountLoader
import APBroadcaster
import APCategoryList
import APItemLoader
import APEpgLoader
import APVodItem
import APCategory

PROVIDERS = {
  "Mako": {'pKey': '81d42db7c211bf9615a895c504', 'accountId': '39', 'broadcasterId': '24',
           'bundle': 'com.keshet.mako.VODandroid'}
}

def Log(text):
  print text

def getMainCategoryList():
  accountLoader = APAccountLoader.APAccountLoader(PROPERTIES)
  jsonAccountDictionary = accountLoader.loadURL()
  Log('accountURL --> %s' % (accountLoader.getQuery()))
  Log('dict --> %s' % (jsonAccountDictionary))
  broadcaster = APBroadcaster.APBroadcaster(PROPERTIES['broadcasterId'],
                                            jsonAccountDictionary["account"]["broadcasters"])
  Log('Main Category --> %s' % (broadcaster.getRootCategory()))
  mainCategory = broadcaster.getRootCategory()

  categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, mainCategory)
  Log('CategoryURL --> %s' % (categoryLoader.getQuery()))
  jsonCategoryDictionary = categoryLoader.loadURL()
  categories = APCategoryList.APCategoryList(jsonCategoryDictionary["category"])

  if (categories.hasSubCategories()):
    for category in categories.getSubCategories():
      Log(category.getTitle() + " " + category.getId())

def getCategory(categoryId):
  Log("GetCategory " + categoryId)
  # get the main categories list
  categoryLoader = APCategoryLoader.APCategoryLoader(PROPERTIES, categoryId)
  Log('CategoryURL --> %s' % (categoryLoader.getQuery()))
  jsonCategoryDictionary = categoryLoader.loadURL()
  categories = APCategoryList.APCategoryList(jsonCategoryDictionary["category"])

  for category in categories.getSubCategories():
    Log("Sub: %s - %s" % (category.getTitle(), category.getId()))
  for item in categories.getVodItems():
    Log("Item: %s - %s" % (item.getTitle(), item.getId()))

def getItem(itemId):
  itemLoader = APItemLoader.APItemLoader(PROPERTIES, itemId)
  Log('ItemURL --> %s' % (itemLoader.getQuery()))
  jsonItemDictionary = itemLoader.loadURL()
  item = APVodItem.APVodItem(jsonItemDictionary["vod_item"])

rand1 = int((random.random() * 8999) + 1000)
rand2 = int((random.random() * 89) + 10)
deviceId = '1d' + str(rand1) + 'd3b4f71c' + str(rand2)

for provider, properties in PROVIDERS.items():
  properties['deviceId'] = deviceId
  print provider


