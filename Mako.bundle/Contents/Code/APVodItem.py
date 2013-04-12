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
        try:
            self.free = self.get('free')
            self.id = str(self.get('id'))
            self.description = self.get('summary')
            self.title = self.get('title')
            imagesJosn = json.loads(self.get("images_json"))
            self.thumbnail = imagesJosn["large_thumb"]
            self.stream = self.get('stream_url')
        except:
            pass
        
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