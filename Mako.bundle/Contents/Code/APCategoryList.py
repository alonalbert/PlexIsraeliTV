# -*- coding: utf-8 -*-
'''
    Created on 23/01/2012
    
    Copyright (c) 2010-2012 Shai Bentin.
    All rights reserved.  Unpublished -- rights reserved

    Use of a copyright notice is precautionary only, and does
    not imply publication or disclosure.
 
    Licensed under Eclipse Public License, Version 1.0
    Initial Developer: Shai Bentin.

    @author: shai
'''
from APModel import APModel
from APVodItem import APVodItem
from APCategory import APCategory

class APCategoryList(APModel):
    def __init__(self, params = {}):
        self.innerDictionary = params
        self.children = []
        self.vodItems = []

        items = self.innerDictionary.get('children')
        if items is not None:
            for child in items:
                self.children.append(APCategory(child))

        items = self.innerDictionary.get('vod_items')
        if items is not None:
            for vod in items:
                self.vodItems.append(APVodItem(vod))

    def hasSubCategories(self):
        return self.children
    
    def hasVideoitems(self):
        return self.vodItems
    
    # returns the subCategories or an empty list
    def getSubCategories(self):
        return self.children
    
    # returns the vodItems or an empty list
    def getVodItems(self):
        return self.vodItems