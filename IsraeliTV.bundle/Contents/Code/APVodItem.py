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
import json
from APModel import APModel

class APVodItem(APModel):
    '''
    classdocs
    '''
    free = False
    id = ''
    title = ''
    description = ''
    thumbnail = ''
    stream = ''

    def __init__(self, params = {}):
        self.innerDictionary = params
        self.free = self.get('free')
        self.id = str(self.get('id'))
        self.description = self.get('summary')
        self.title = self.get('title')
        self_get = self.get("images_json")
        self.stream = self.get('stream_url')
        images = json.loads(self_get)
        if images is not None:
            self.thumbnail = images.get("large_thumb")
            if self.thumbnail is None:
                self.thumbnail = images.get("large_thumbnail")

    def isFree(self):
        return self.free
    
    def getId(self):
        return self.id
    
    def getTitle(self):
        return self.title
    
    def getDescription(self):
        return self.description
    
    def getThumbnail(self):
        return self.thumbnail
    
    def getStreamUrl(self):
        return self.stream