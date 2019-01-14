
from __future__ import unicode_literals

import logging

from mopidy import core

import pykka

from .input import InputThread, Handler

logger = logging.getLogger(__name__)

class VolumeHandler(Handler):
  def __init__(self, device_fn, event_type, event_code, actor_ref):
    super(VolumeHandler, self).__init__(device_fn, event_type, event_code)
    self.actor_proxy=actor_ref.proxy()

  def handle(self, event):
    logger.debug("Volume change {0}".format(event.value*5))
    self.actor_proxy.change_volume(event.value*5)


class PlaylistHandler(Handler):
  def __init__(self, device_fn, event_type, event_code, actor_ref):
    super(PlaylistHandler, self).__init__(device_fn, event_type, event_code)
    self.actor_proxy=actor_ref.proxy()

  def handle(self, event):
    logger.debug("Playlist change {0}".format(event.value))
    self.actor_proxy.change_playlist(event.value)


class MuteHandler(Handler):
  def __init__(self, device_fn, event_type, event_code, actor_ref, longpress=5):
    super(MuteHandler, self).__init__(device_fn, event_type, event_code)
    self.actor_proxy=actor_ref.proxy()
    self.longpress=longpress

  def handle(self, event):
    if (event.value==1):
      self.timestamp=event.sec
    if (event.value==0):
      diff=event.sec-self.timestamp
      if (diff>self.longpress):
        logger.debug("Longpress mute")
        self.actor_proxy.halt()
      else:
        self.actor_proxy.toggle_mute()


class InputFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(InputFrontend, self).__init__()
        self.config = config['headless']
        self.core=core
        
        self.playlists = None
        self.selected_playlist = None
        

    def on_start(self):
        self.reload_playlists()
        self.change_playlist(0)
        
        
        self.inputthread=InputThread()
        self.inputthread.registerHandler(VolumeHandler(self.config["volume_device"], "EV_REL", self.config["volume_axis"], self.actor_ref))
        self.inputthread.registerHandler(PlaylistHandler(self.config["playlist_device"], "EV_REL", self.config["playlist_axis"], self.actor_ref))
        self.inputthread.registerHandler(MuteHandler(self.config["mute_device"], "EV_KEY", self.config["mute_key"], self.actor_ref))
        self.inputthread.start()

    def on_stop(self):
        self.inputthread.stop()

    def halt(self):
        print("Goodbye")

    def change_volume(self, value):
      volume=self.core.playback.volume.get()+value
      if volume<0:
          volume=0
      elif volume>100:
          volume=100
          
      logger.debug("Volume changed: {0}".format(volume))
      self.core.playback.volume=volume

    def toggle_mute(self):
        mute = not self.core.playback.mute.get()
        logger.debug("Muted: {0}".format(mute))
        self.core.playback.mute = mute

    def change_playlist(self, value):
        self.selected_playlist= (self.selected_playlist+1) % len(self.playlists)
        logger.debug("Change playlist: {0}".format(self.selected_playlist))
        self.core.tracklist.clear()
        self.core.tracklist.add(uri=self.playlists[self.selected_playlist].uri)
        self.core.playback.play()
        
    def reload_playlists(self):
        self.playlists = []
        for playlist in self.core.playlists.playlists.get():
            self.playlists.append(playlist)
        self.selected_playlist = 0
