# -*- coding: utf-8 -*-
'''
    Created on 27/01/2012

    Copyright (c) 2010-2012 Shai Bentin.
    All rights reserved.  Unpublished -- rights reserved

    Use of a copyright notice is precautionary only, and does
    not imply publication or disclosure.
 
    Licensed under Eclipse Public License, Version 1.0
    Initial Developer: Shai Bentin.

    @author: shai
'''
from APModel import APModel

class APCategory(APModel):
    '''
    classdocs
    '''
    id = ''
    thumbNameImageURL = ''
    fanArtImageURL = ''
    title = ''
    description= ''

    def __init__(self, params):
        '''
        Constructor
        '''
        self.innerDictionary = params
        
        self.id = str(self.get('id'))
        self.fanArtImageURL = self.get('large-poster')
        self.thumbNameImageURL = self.get('icon_url')
        self.title = self.get('name')
        self.description = self.get('description')
        
    def getId(self):
        return self.id
    
    def getThumbnail(self):
        return self.thumbNameImageURL
    
    def getFanartImage(self):
        return self.fanArtImageURL
    
    def getTitle(self):
        return self.title
    
    def getDescription(self):
        return self.description