#!/usr/bin/env python
from devicewrapper.android import device as d
from uiautomator import device as dd
import unittest
import time
import sys
import os
import commands
import string
import random

PACKAGE_NAME = 'com.intel.android.gallery3d'
ACTIVITY_NAME = PACKAGE_NAME + '/.app.Gallery'

#Get count for images in DCIM folder
GET_IMAGE_COUNT = 'adb shell ls /sdcard/DCIM/* | grep IMG | wc -l'

#Get count for convert images in Sharing folder
GET_CONVERT_COUNT = 'adb shell ls /sdcard/Sharing/* | grep 1 | wc -l'

#Commands for refreshing media
REFRESH_MEDIA = 'adb shell am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///sdcard'

#Read geo info for camera
CAMERA_GEOTAG_ON_OFF = "adb shell cat /data/data/com.intel.camera22/shared_prefs/com.intel.camera22_preferences_0.xml | grep pref_camera_geo_location_key"

#Point for selecting when edit burst
POINT_ONE = '30 200'
POINT_TWO = '160 200'
POINT_THR = '310 200'
POINT_FOR = '460 200'
POINT_FIV = '600 200'

#All mode could be selected for gallery
ModeList = {'Albums': 'Albums',
            'Places': 'Places',
            'Events': 'Events',
            'Dates': 'Dates',
            'People': 'People'
            }

class GalleryBatTest(unittest.TestCase):
    def setUp(self):
        super(GalleryBatTest,self).setUp()



    '''
    #######################################################
    def testWirelessDisplay(self):
        print('\n testWirelessDisplay \n case is not yet')

    def testSharingToFacebookFromCardpop(self):
        print('\n testSharingToFacebookFromCardpop \n case is not yet')

    def testCheckingShareItemInFacebook(self):
        print('\n testCheckingShareItemInFacebook \n case is not yet')

    def testSocialSync(self):
        print('\n testSocialSync \n case is not yet')

    def testCalendarEvent(self):
        print ('Case not ready')
    #######################################################
    '''





    def _launchGallery(self):
        commands.getoutput('adb shell am start -n %s' %ACTIVITY_NAME)
        #Confirm gallery launch successfully by the icon on left-top corner
        assert d(text = 'Albums').wait.exists(timeout = 2000), 'Gallery launch failed'

    def _launchCamera(self):
        commands.getoutput('adb shell am start -n com.intel.camera22/.Camera')
        #Confirm camera is launched successfully
        assert d(resourceId = 'com.intel.camera22:id/shutter_button').wait.exists(timeout = 5000), 'Camera launch failed'

    def _launchMap(self):
        commands.getoutput('adb shell am start -n com.google.android.apps.maps/com.google.android.maps.MapsActivity')
        #Confirm map is launched
        assert d(description = 'Directions').wait.exists(timeout = 3000), 'Map does not launch'
        try:
            assert d(description = 'Move to your location').wait.exists(timeout = 3000) #Check if location has not been found
            d(description = 'Move to your location').click.wait() #Tap on icon to find the location
        except:
            pass
        finally:
            assert d(description = 'Enter compass mode').wait.exists(timeout = 3000), 'Location has not been found' #Check if location has been found

    def _takePicture(self):
        before = commands.getoutput('adb shell ls /sdcard/DCIM/* | grep IMG | wc -l') #Count before taking picture
        d(resourceId = 'com.intel.camera22:id/shutter_button').click.wait() #Tap on capture button
        after = commands.getoutput('adb shell ls /sdcard/DCIM/* | grep IMG | wc -l') #Count after taking picture
        if string.atoi(before) == string.atoi(after) - 1 or string.atoi(before) == string.atoi(after) - 2:
            pass
        else:
            self.fail('Take picture failed.')

    def testLaunchingCamera(self):
        self._deleteAllPictures()
        self._launchGallery()
        #Tap on camera icon in Gallery album view
        d(description = 'Switch to camera').click.wait()
        #Check if default camera has already been set up
        #If not, set default camera as intel camera
        try: 
            assert d(text = 'Complete action using').wait.exists(timeout = 2000)
            d(text = 'Always').click.wait()
            d(text = 'com.intel.camera22').click.wait()
            d(text = 'Always').click.wait()
        except:
            pass
        finally:
            #Check camera launch successful
            assert d(resourceId = 'com.intel.camera22:id/shutter_button').wait.exists(timeout = 5000), 'Camera launch failed'
        self._takePicture()

    def testSingleViewCardpop(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()

    def testCardpopDetails(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.swipe(350,1100,350,350) #Pull pop up card up
        assert d(text = 'Facebook').wait.exists(timeout = 2000), 'Pop up card has not been pulled up'
        d.swipe(350,1100,350,350) #Pull up second time to show details
        assert d(text = 'Advanced photo details').wait.exists(timeout = 2000), 'Details in pop up card does not shown'

    def testGeotagInformation(self):
        self._deleteAllPictures()
        self._launchMap()
        d.press('back','back')
        self._launchCamera()
        self._setGeoOn()
        self._takePicture()
        d.press('back','back')
        self._launchGallery()
        time.sleep(2)
        self._enterSingleView()
        self._showPopupCard()
        d.click(350,1100) #Tap on pop up card bar to invoke it
        assert d(resourceId = 'com.intel.android.gallery3d:id/street').wait.exists(timeout = 2000), 'Geo tag information does not show on pictures details'

    def testAddingDeletingKeywords(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.click(350,1100) #Tap on pop up card bar to invoke it
        assert d(text = 'Facebook').wait.exists(timeout = 2000), 'Details has not pop up'
        d.swipe(350,1100,350,350) #Pull up pop up card to show more details
        assert d(resourceId = 'com.intel.android.gallery3d:id/addKeywordButton').wait.exists(timeout = 2000), 'Keywords has not shown in details'
        d(resourceId = 'com.intel.android.gallery3d:id/addKeywordButton').click.wait() #Tap on add keywords
        d(text = 'Enter new keyword').set_text('NewKeyword') #Input keywords content
        self._clickDoneButton()
        assert d(text = 'NewKeyword').wait.exists(timeout = 2000), 'Add keywords failed'
        d.click(280,700) #Delete the keyword just added
        try:
            assert d(text = 'NewKeyword').wait.exists(timeout = 2000), 'Delete keywords failed'
        except:
            d.press('back','back')
        finally:
            self._deleteAllPictures()

    def testAddingEventVenue(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.click(350,1100) #Tap on pop up card bar to invoke it
        assert d(text = 'Facebook').wait.exists(timeout = 2000), 'Details has not pop up'
        #Add & delete Event****************************************************************
        d(resourceId = 'com.intel.android.gallery3d:id/event_edit').click.wait() #Add new event
        d(resourceId = 'com.intel.android.gallery3d:id/search_text').set_text('HappyDay') #Input envent
        self._clickDoneButton()
        assert d(text = 'HappyDay').wait.exists(timeout = 2000), 'Set Event failed'
        d(resourceId = 'com.intel.android.gallery3d:id/event_edit').click.wait() #Delete event
        self._clearInputText()
        self._clickDoneButton()
        assert d(text = 'Add an event').wait.exists(timeout = 2000), 'Event has not been deleted'
        #Add & delete Venue****************************************************************
        d(resourceId = 'com.intel.android.gallery3d:id/venue_edit').click.wait() #Add new venue
        d(resourceId = 'com.intel.android.gallery3d:id/search_text').set_text('RNB') #Input venue
        self._clickDoneButton()
        assert d(text = 'RNB').wait.exists(timeout = 2000), 'Set Venue failed'
        d(resourceId = 'com.intel.android.gallery3d:id/venue_edit').click.wait() #Delete venue
        self._clearInputText()
        self._clickDoneButton()
        assert d(text = 'Add a venue').wait.exists(timeout = 2000), 'Venue has not been deleted'

    def testAutoTag(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.click(350,1100) #Tap on pop up card bar to invoke it
        assert d(text = 'Facebook').wait.exists(timeout = 2000), 'Details has not pop up'
        #Add Event
        d(resourceId = 'com.intel.android.gallery3d:id/event_edit').click.wait() #Add new event
        d(resourceId = 'com.intel.android.gallery3d:id/search_text').set_text('HappyDay') #Input envent
        self._clickDoneButton()
        assert d(text = 'HappyDay').wait.exists(timeout = 2000), 'Set Event failed'
        #Add Venue
        d(resourceId = 'com.intel.android.gallery3d:id/venue_edit').click.wait() #Add new venue
        d(resourceId = 'com.intel.android.gallery3d:id/search_text').set_text('RNB') #Input venue
        self._clickDoneButton()
        assert d(text = 'RNB').wait.exists(timeout = 2000), 'Set Venue failed'
        #Check auto tag on pop up card
        assert d(textStartsWith = 'HappyDay at RNB').wait.exists(timeout = 2000), 'Auto tag shows incorrect'

    def testFaceDetection(self):
        #self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        self._enableGalleryFR()
        self._tapOnFace()
        assert d(text = '   Find contacts').wait.exists(timeout = 2000), 'Face is not detected'

    def testRegisterAContact(self):
        self.testFaceDetection()
        d(text = 'Create new contact').click.wait() #Create a new contact
        try:
            assert d(text = 'Create new contact').wait.exists(timeout = 2000)
            d(text = 'OK').click.wait()
        except:
            pass
        d(text = 'Name').set_text('NewContact') #Input contact name
        time.sleep(2)
        d.click(520,520) #Tap on a block area...
        d(text = 'Done').click.wait() #Save new contact
        assert d(text = 'Crop picture').wait.exists(timeout =2000)
        d(text = 'Crop').click.wait() #Save the portrait for contact
        self._tapOnFace()
        assert d(resourceId = 'com.intel.android.gallery3d:id/action_edit_menu').wait.exists(timeout = 2000), 'Contact for the face created failed'
        d(resourceId = 'com.intel.android.gallery3d:id/action_edit_menu').click.wait()
        d(text = 'Remove identity').click.wait() #Remove the contact identity
        d(text = 'Remove identity').click.wait() #Confirm removing

    def testFaceRecognition(self):
        for i in range (0,3):
            self.testRegisterAContact()
            time.sleep(2)
            d.press('back','back') #Exit gallery
            galleryPID = commands.getoutput("adb shell ps | grep com.intel.android.gallery3d | awk '{print $2}'")
            KILL_GALLERY = 'adb shell kill %s' %galleryPID
            if galleryPID != -1:
                commands.getoutput(KILL_GALLERY)
            time.sleep(5)

    def testVideoPlayback(self):
        self._checkVideoResource()
        self._launchGallery()
        self._enterSingleView()
        self._tapOnPlaybackIcon()
        try:
            assert d(text = 'Complete action using').wait.exists(timeout = 2000)
            d(text = 'com.intel.android.gallery3d').click.wait() #Select social gallery
            d(text = 'Always').click.wait() #Select always
        except:
            pass
        assert d(className = 'android.widget.VideoView').wait.exists(timeout = 2000)
        time.sleep(100) #Wait video playing till the end
        assert d(className = 'android.widget.VideoView').wait.gone(timeout = 2000)

    def testEditingAPicture(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.press('menu')
        d(text = 'Edit').click.wait()
        try:
            assert d(text = 'Choose an action').wait.exists(timeout = 2000)
            d(text = 'com.intel.android.gallery3d').click.wait() #Select Social gallery
        except:
            pass
        d(resourceId = 'com.intel.android.gallery3d:id/geometryButton').click.wait() #Select geometry
        assert d(resourceId = 'com.intel.android.gallery3d:id/cropButton').wait.exists(timeout = 2000), 'Switch to geometry failed.'
        d(resourceId = 'com.intel.android.gallery3d:id/cropButton').click.wait() #Select crop pic
        assert d(resourceId = 'com.intel.android.gallery3d:id/aspect').wait.exists(timeout = 2000), 'Phone has not go to crop mode.'
        d(resourceId = 'com.intel.android.gallery3d:id/aspect').click.wait() #Select aspect
        assert d(text = '3:4').wait.exists(timeout = 2000) #Check if aspect selections pop up
        d(text = '3:4').click.wait() #Select 3:4 aspect
        d(text = 'Apply').click.wait() #Apply it
        assert d(resourceId = 'com.intel.android.gallery3d:id/cropButton').wait.exists(timeout = 2000), 'Apply changes failed'
        d(text = 'SAVE').click.wait() #Save the changes
        assert d(resourceId = 'com.intel.android.gallery3d:id/action_share').wait.exists(timeout = 2000), 'Save edited pic suc'

    def testEditingPerfectShot(self):
        self._deleteAllPictures()
        self._takePicUnderPerfectMode()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d(resourceId = 'com.intel.android.gallery3d:id/action_edit_perfectshot').click.wait()
        time.sleep(5) #This may take a few seconds
        assert d(index = '8', resourceId = 'com.intel.android.gallery3d:id/base_image_button8').wait.exists(timeout = 2000), 'Count for Perfect pictures is not touch 9.'

    def testRotatePictures(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.press('menu')
        d(text = 'Rotate left').click.wait() #Rotate to left
        time.sleep(2)
        d.press('menu')
        d(text = 'Rotate right').click.wait()
        time.sleep(2)
        d.press('back')
        assert d(description = 'Search').wait.exists(timeout = 2000), 'It does not back to the grid view' #Back to the grid view
        d.swipe(370, 590, 371, 591) #Long click the picture in the center
        time.sleep(2)
        #Prepare to rotate to left
        assert d(text = '1 selected').wait.exists(timeout = 2000), 'It does not in select view'
        d(text = '1 selected').click.wait()
        assert d(text = 'Select all').wait.exists(timeout = 2000)
        d(text = 'Select all').click.wait()
        d(description = 'More options').click.wait() #Press menu key
        d(text = 'Rotate left').click.wait() #Rotate to left
        time.sleep(2)
        #Prepare to rotate to right
        d.swipe(370, 590, 371, 591) #Long click the picture in the center
        time.sleep(2)
        assert d(text = '1 selected').wait.exists(timeout = 2000), 'It does not in select view'
        d(text = '1 selected').click.wait()
        assert d(text = 'Select all').wait.exists(timeout = 2000)
        d(text = 'Select all').click.wait()
        d(description = 'More options').click.wait() #Press menu key
        d(text = 'Rotate right').click.wait() #Rotate to right
        time.sleep(2)
        assert d(resourceId = 'com.intel.android.gallery3d:id/action_camera').wait.exists(timeout = 5000)

    def testEditBurst(self):
        self._deleteAllPictures()
        self._pushBurstPicture()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d(resourceId = 'com.intel.android.gallery3d:id/action_edit_burst').click.wait() #Enter burst edit view
        assert d(text = '0 selected').wait.exists(timeout = 2000), 'It does not go to edit view in 2 seconds'
        #***Export marked pic to gallery***
        #Generate how many and which points shall be selected
        selected_pics_count, touch_points = self._getRandomSelectBurstPoint()
        #Get image count in DCIM folder
        before = commands.getoutput(GET_IMAGE_COUNT)
        #Start to point selected pictures
        for i in range(len(touch_points)):
            self._pointOnSelectedPic(touch_points[i])
        d(description = 'More options').click.wait() #Press menu button
        assert d(text = 'Export to gallery').wait.exists(timeout = 2000), 'Menu list does not pop up in 2s'
        d(text = 'Export to gallery').click.wait() #Try to export the selected pictures to the gallery
        time.sleep(3) #Wait till the exporting complete
        #Get image count in DCIM folder after exporting
        after = commands.getoutput(GET_IMAGE_COUNT)
        if string.atoi(before) == string.atoi(after) - len(touch_points):
            pass
        else:
            self.fail('Exporting failed.')

        #***Delete marked pic***
        selected_pics_count, touch_points = self._getRandomSelectBurstPoint()
        for i in range(len(touch_points)):
            self._pointOnSelectedPic(touch_points[i])
        d(description = 'More options').click.wait() #Press menu button
        assert d(text = 'Delete marked').wait.exists(timeout = 2000), 'Menu list does not pop up in 2s'
        d(text = 'Delete marked').click.wait() #Try to delete the selected pictures
        assert d(text = '0 selected').wait.exists(timeout = 2000)

    def testSlideshow(self):
        self._deleteAllPictures()
        self._pushBurstPicture()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d(resourceId = 'com.intel.android.gallery3d:id/action_edit_burst').click.wait() #Enter burst edit view
        assert d(text = '0 selected').wait.exists(timeout = 2000), 'It does not go to edit view in 2 seconds'
        #Select all burst pic
        d(text = '0 selected').click.wait()
        d(text = 'Select all').click.wait()
        assert d(text = '10 selected').wait.exists(timeout = 2000), 'All pictures has not been selected'
        #Press playback icon and check options in menu list
        d(description = 'Slideshow').click.wait()
        assert d(text = 'Dissolve').wait.exists(timeout = 2000) #Check Dissolve option in menu list
        assert d(text = 'Flash').wait.exists(timeout = 2000) #Check Flash option in menu list
        assert d(text = 'Page flip').wait.exists(timeout = 2000) #Check Page flip option in menu list
        #Play as page flip
        d(text = 'Page flip').click.wait()
        time.sleep(5) #Let it play 5s
        d.press('back')
        assert d(description = 'Slideshow').wait.exists(timeout = 2000)

    def testSharePerfectShotUsingGmail(self):
        self._deleteAllPictures()
        self._takePicUnderPerfectMode()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        #Tap on share icon
        d(description = 'Share').click.wait()
        assert d(text = 'See all').wait.exists(timeout = 2000), 'Share options does not pop up in 2s'
        d(text = 'See all').click.wait() #List all share options
        #When share picture via Gmail, it may locate at the end of the option list
        try:
            assert d(text = 'Gmail').wait.exists(timeout = 2000)
        except:
            d.swipe(600, 800, 600, 300)
        finally:
            d(text = 'Gmail').click.wait()
        #Check if composing  interface display
        assert d(description = 'Send').wait.exists(timeout = 5000), 'Share picture to Gmail failed'
        #Discard the sharing item
        d.press('menu')
        assert d(text = 'Discard').wait.exists(timeout = 2000) #Check if menu list pop up
        d(text = 'Discard').click.wait() #Click discard in menu list
        assert d(text = 'Discard this message?').wait.exists(timeout = 2000)
        d(text = 'Discard').click.wait() #Click discard when confirm

    def testShareSingleShotUsingBluetooth(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d(description = 'Share').click.wait()
        assert d(text = 'See all').wait.exists(timeout = 2000), 'Share options does not pop up in 2s'
        d(text = 'See all').click.wait() #List all share options
        try:
            assert d(text = 'Bluetooth').wait.exists(timeout = 2000)
        except:
            d.swipe(600, 800, 600, 300)
        finally:
            d(text = 'Bluetooth').click.wait()
        time.sleep(5) #When BT is off, this may take a few seconds
        if d(text = 'Turn on').wait.exists(timeout = 2000):
            d(text = 'Turn on').click.wait()
        #Check if BT device list could display normally
        assert d(text = 'Bluetooth device chooser').wait.exists(timeout = 5000), 'BT device list does not show in 5s'

    def testDeleteMediaItems(self):
        self._checkResource()
        self._launchGallery()
        self._enterGridView()
        d.swipe(370, 590, 371, 591) #Long click the picture in the center
        time.sleep(2)
        assert d(text = '1 selected').wait.exists(timeout = 2000), 'The picture in the center has not been selected'
        d(text = '1 selected').click.wait()
        assert d(text = 'Select all').wait.exists(timeout = 2000), 'Selection extra menu does not pop up'
        d(text = 'Select all').click.wait()
        d(description = 'Delete').click.wait() #Try to delete the all pictures in the album
        assert d(text = 'Delete').wait.exists(timeout = 2000) #Here shall pop up an extra menu
        d(text = 'Delete').click.wait() #Confirm and delete the all pic
        #After deleting all pictures, it shall back to the album view due to there is no any picture in the album
        time.sleep(5)
        assert d(text = 'Albums').wait.exists(timeout = 3000), 'All pictures have not been deleted in 8s'

    def testCreateVideoFromPhotos(self):
        self._checkResource()
        self._launchGallery()
        self._enterGridView()
        d.swipe(390, 280, 391, 281) #Long click the first picture on second row
        #This will run 3 circles, means select the second, the third and the fouth pic on second row
        for y in range(530, 1100, 250): #530 = 280 + 250, that means the second pic on second row
            d.click(390, y)
        d(description = 'More options').click.wait() #Tap on the extra menu
        assert d(text = 'Animate').wait.exists(timeout = 2000)
        d(text = 'Animate').click.wait() #Try to convert the selected pictures to an animate
        assert d(text = 'Video').wait.exists(timeout = 3000), 'Animate does not pop up in 3s'
        d(text = 'Video').click.wait() #Select Video to convert
        assert d(text = 'Resolution').wait.exists(timeout = 2000)
        #Count has been changed, so get count before converting here
        before = commands.getoutput(GET_CONVERT_COUNT) #Count before creating animate
        d(text = 'Create').click.wait() #Tap on create button
        time.sleep(8) #This action may take a few seconds
        assert d(text = 'Save').wait.exists(timeout = 2000), 'Converting does not complete in 10s'
        #Save and check
        d(text = 'Save').click.wait() #Save the animate
        time.sleep(5) #Saving action    
        after = commands.getoutput(GET_CONVERT_COUNT) #Count after creating animate
        if string.atoi(before) == string.atoi(after) - 1 or string.atoi(before) == string.atoi(after) - 2:
            pass
        else:
            self.fail('Converting picture failed.')

    def testCreateAnimateGIF(self):
        self._checkResource()
        self._launchGallery()
        self._enterGridView()
        d.swipe(390, 280, 391, 281) #Long click the first picture on second row
        #This will run 3 circles, means select the second, the third and the fouth pic on second row
        for y in range(530, 1100, 250): #530 = 280 + 250, that means the second pic on second row
            d.click(390, y)
        d(description = 'More options').click.wait() #Tap on the extra menu
        assert d(text = 'Animate').wait.exists(timeout = 2000)
        d(text = 'Animate').click.wait() #Try to convert the selected pictures to an animate
        assert d(text = 'Animated GIF').wait.exists(timeout = 3000), 'Animate does not pop up in 3s'
        d(text = 'Animated GIF').click.wait() #Select Video to convert
        assert d(text = 'Speed').wait.exists(timeout = 2000)
        #Count has been changed, so get count before converting here
        before = commands.getoutput(GET_CONVERT_COUNT) #Count before creating animate
        d(text = 'Create').click.wait() #Tap on create button
        time.sleep(5) #This action may take a few seconds, but faster than video
        assert d(text = 'Save').wait.exists(timeout = 2000), 'Converting does not complete in 7s'
        #Save and check
        d(text = 'Save').click.wait() #Save the animate
        time.sleep(5) #Saving action    
        after = commands.getoutput(GET_CONVERT_COUNT) #Count after creating animate
        if string.atoi(before) == string.atoi(after) - 1 or string.atoi(before) == string.atoi(after) - 2:
            pass
        else:
            self.fail('Converting picture failed.')

    def testCreatingCollage(self):
        self._checkResource()
        self._launchGallery()
        self._enterGridView()
        d.swipe(390, 280, 391, 281) #Long click the first picture on second row
        #This will run 3 circles, means select the second, the third and the fouth pic on second row
        for y in range(530, 1100, 250): #530 = 280 + 250, that means the second pic on second row
            d.click(390, y)
        d(description = 'More options').click.wait() #Tap on the extra menu
        assert d(text = 'Photo collage').wait.exists(timeout = 2000)
        d(text = 'Photo collage').click.wait() #Try to convert the selected pictures to a collage
        before = commands.getoutput(GET_CONVERT_COUNT) #Count before creating animate
        assert d(text = 'Save').wait.exists(timeout = 2000), 'Converting does not complete in 7s'
        #Save and check
        d(text = 'Save').click.wait() #Save the animate
        assert d(text = 'Share').wait.exists(timeout = 2000)
        time.sleep(5) #Saving action    
        after = commands.getoutput(GET_CONVERT_COUNT) #Count after creating animate
        if string.atoi(before) == string.atoi(after) - 1 or string.atoi(before) == string.atoi(after) - 2:
            pass
        else:
            self.fail('Converting collage failed.')

    def testCopyingImagesFromExternalSource(self):
        self._checkResource()
        self._launchGallery()
        self._enterGridView()
        d.swipe(390, 280, 391, 281) #Long click the first picture on second row
        #Check if select one pic is success
        assert d(text = '1 selected').wait.exists(timeout = 2000)
        #Select all pic and get the count
        d(text = '1 selected').click.wait()
        assert d(text = 'Select all').wait.exists(timeout = 2000)
        d(text = 'Select all').click.wait()
        #Check count for all selected items on UI
        assert d(text = '20 selected').wait.exists(timeout = 2000)

    def testFRBackgroundProcess(self):
        self._checkResource()
        self._launchGallery()
        d(text = 'Albums').click.wait() #Tap on album to switch other view
        assert d(text = 'People').wait.exists(timeout = 2000)
        d(text = 'People').click.wait() #Swtich to people view
        time.sleep(3)
        d.expect('Unknown_New_Face.png')

    def testAddingPlaceEventToGroup(self):
        self._checkResource()
        self._launchGallery()
        d.swipe(360, 780, 361, 781) #Long click the album
        assert d(text = '1 selected').wait.exists(timeout = 2000) #Check whether the album has been highlighted
        #Edit place for album
        d(description = 'More options').click.wait()
        assert d(text = 'Edit Place').wait.exists(timeout = 2000)
        d(text = 'Edit Place').click.wait()
        d(text = 'Enter new venue').set_text('RNB01') #Input place info
        self._clickDoneButton()

        d.swipe(360, 780, 361, 781) #Long click the album

        #Edit event for album
        d(description = 'More options').click.wait()
        assert d(text = 'Edit Event').wait.exists(timeout = 2000)
        d(text = 'Edit Event').click.wait()
        d(text = 'Enter new event').set_text('Sprint Review') #Input event info
        self._clickDoneButton()
        #Check place and event
        self._enterSingleView()
        self._showPopupCard()
        d.click(350,1100) #Tap on pop up card bar to invoke it
        assert d(text = 'RNB01').wait.exists(timeout = 2000)
        assert d(text = 'Sprint Review').wait.exists(timeout = 2000)

    def testSearchByKeyword(self):
        self._checkResource()
        self._launchGallery()
        self._enterSingleView()
        self._showPopupCard()
        d.click(350,1100) #Tap on pop up card bar to invoke it
        assert d(text = 'Facebook').wait.exists(timeout = 2000), 'Details has not pop up'
        d.swipe(350,1100,350,350) #Pull up pop up card to show more details
        assert d(resourceId = 'com.intel.android.gallery3d:id/addKeywordButton').wait.exists(timeout = 2000), 'Keywords has not shown in details'
        d(resourceId = 'com.intel.android.gallery3d:id/addKeywordButton').click.wait() #Tap on add keywords
        d(text = 'Enter new keyword').set_text('NewKeyword') #Input keywords content
        self._clickDoneButton()
        assert d(text = 'NewKeyword').wait.exists(timeout = 2000), 'Add keywords failed'
        #Search by keyword
        d.press('back') #Back to the grid view
        time.sleep(2)
        d.press('back') #Back to the album view
        assert d(description = 'Search').wait.exists(timeout = 2000), 'It has not back to the album view'
        d(description = 'Search').click.wait()
        assert d(resourceId = 'com.intel.android.gallery3d:id/search_src_text').wait.exists(timeout = 2000)
        d(resourceId = 'com.intel.android.gallery3d:id/search_src_text').set_text('NewKeyword')
        d.expect('Search_Result_Item.png')
        #Check the search result
        d(resourceId = 'com.intel.android.gallery3d:id/searchedText').click.wait()
        assert d(text = 'NewKeyword').wait.exists(timeout = 2000)

    def testSort(self):
        self._checkResource()
        self._launchGallery()
        ModeToBeSelect = ModeList.keys()
        ModeCount = len(ModeList)
        #Random switch all modes without repetition
        for i in range(0 , ModeCount):
            selviewmode = random.choice(ModeToBeSelect)
            self._selectViewMode(selviewmode)
            ModeToBeSelect.remove(selviewmode)
        #Check whether view mode switch suc
        assert d(text = ModeList[viewmode]).wait.exists(timeout = 3000)

    def _selectViewMode(self,viewmode):
        d(resourceId = 'android:id/text1').click.wait() #Tap on the left top corner
        assert d(text = 'Albums').wait.exists(timeout = 2000)
        #Click the selected viewmode
        d(text = ModeList[viewmode]).click.wait()

    def _enterGridView(self):
        time.sleep(2)
        d.click(350,700) #Tap on an album

    def _takePicUnderPerfectMode(self):
        self._launchCamera()
        d(description = 'Show switch camera mode list').click.wait()
        assert d(resourceId = 'com.intel.camera22:id/mode_wave_perfectshot').wait.exists(timeout = 2000)
        d(resourceId = 'com.intel.camera22:id/mode_wave_perfectshot').click.wait() #Switch to perfect mode
        time.sleep(5) #Sometimes it takes much time for switching mode
        assert d(resourceId = 'com.intel.camera22:id/shutter_button').wait.exists() #Check if mode has been switched
        d(resourceId = 'com.intel.camera22:id/shutter_button').click.wait()
        time.sleep(5) #Take picture under perfect mode may take more time
        d.press('back','back')

    def _pointOnSelectedPic(self, touch_points):
        commands.getoutput('adb shell input tap %s' %touch_points)

    def _getRandomSelectBurstPoint(self):
        touch_point = [POINT_ONE, POINT_TWO, POINT_THR, POINT_FOR, POINT_FIV] #Define five points for seleced when editing burst
        random_count = random.randint(1, 5) #Random set count for selected burst
        selected_point = random.sample(touch_point, random_count)
        return random_count, selected_point #Define how many and which points shall be selected


    def _pushBurstPicture(self):
        commands.getoutput('adb push ' + sys.path[0] + '/resource/testburstpics/ ' + '/sdcard/DCIM/100ANDRO/')
        commands.getoutput(REFRESH_MEDIA)
        time.sleep(5) #Waiting for merging burst picture

    def _tapOnPlaybackIcon(self):
        time.sleep(2)
        d.click(360,620) #Click on playback icon

    def _checkVideoResource(self):
        self._deleteAllPictures()
        self._pushVideoResource()
        commands.getoutput(REFRESH_MEDIA)

    def _pushVideoResource(self):
        commands.getoutput('adb push ' + sys.path[0] + '/resource/testvideo/ ' + '/sdcard/testvideo/')
        commands.getoutput(REFRESH_MEDIA)

    def _enableGalleryFR(self):
        d(description = 'More options').click.wait()
        try:
            assert d(text = 'Face recognition Off').wait.exists(timeout = 2000)
            d.click(660,120)
        except:
            d(text = 'Face recognition On').click.wait()

    def _tapOnFace(self):
        time.sleep(2)
        d.click(300,630) #Tap on the face

    def _tapOnFRIcon(self):
        time.sleep(2)
        d.click(60,230) #Tap on the face rec icon

    def _setGeoOn(self):
        geovalue = commands.getoutput(CAMERA_GEOTAG_ON_OFF)
        geoonoffv = geovalue.find('off')
        if geoonoffv != -1:
            d(description = 'Camera settings').click.wait()
            d.click(290,170) #Tap on Geo point
            d.click(170,300) #Set Geo On

    def _enterSingleView(self):
        time.sleep(2)
        d.click(350,700) #Tap on an album
        time.sleep(2)
        d.click(350,700) #Tap on a picture to enter full view

    def _clickDoneButton(self):
        time.sleep(1)
        d.click(660,1120) #Tap on Done button on keyboard

    def _clearInputText(self):
        time.sleep(1)
        d(resourceId = 'com.intel.android.gallery3d:id/search_text_clear').click.wait() #Tap on x button

    def _showPopupCard(self):
        time.sleep(3)
        d.click(350,200) #Tap on screen to invoke pop up card
        time.sleep(3)
        assert d(description = 'Share').wait.exists(timeout = 5000), 'Pop up card does not pop up...'

    def _checkResource(self):
        self._deleteAllPictures()
        self._pushPictures()        

    def _deleteAllPictures(self):
        commands.getoutput('adb shell rm -r /mnt/sdcard/test*')
        commands.getoutput('adb shell rm -r /mnt/sdcard/DCIM/100ANDRO/*')
        commands.getoutput('adb shell rm -r /mnt/sdcard/Sharing/*')
        commands.getoutput(REFRESH_MEDIA)

    def _pushPictures(self):
        commands.getoutput('adb push ' + sys.path[0] + '/resource/testalbum/ ' + '/sdcard/testalbum/')
        #aaa = commands.getoutput('adb push ' + sys.path[0] + '/' + '/resource/testalbum/ ' + '/sdcard/testalbum')
        #print(aaa)
        commands.getoutput(REFRESH_MEDIA)

    def tearDown(self):
        super(GalleryBatTest,self).tearDown()
        d.press('back','back')
        #Check whether Gallery has been exit completely
        galleryPID = commands.getoutput("adb shell ps | grep com.intel.android.gallery3d | awk '{print $2}'")
        KILL_GALLERY = 'adb shell kill %s' %galleryPID
        if galleryPID != -1:
            commands.getoutput(KILL_GALLERY)
        time.sleep(5)

if __name__ == '__main__':
    unittest.main()


