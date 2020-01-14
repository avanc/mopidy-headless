
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
        logger.debug("Toggle mute")
        self.actor_proxy.toggle_mute()


class InputFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(InputFrontend, self).__init__()
        self.config = config['headless']
        self.core=core
        
        self.playlists = None
        self.selected_playlist = None
        if self.config["volume_max"] is None:
            self.config["volume_max"]=100
            
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
      volume=self.core.mixer.get_volume().get()+value
      if volume<0:
          volume=0
      elif volume>self.config["volume_max"]:
          volume=self.config["volume_max"]
          
      logger.debug("Volume changed: {0}".format(volume))
      self.core.mixer.set_volume(volume)

    def toggle_mute(self):
        mute = not self.core.mixer.get_mute().get()
        logger.debug("Muted: {0}".format(mute))
        self.core.mixer.set_mute(mute)
        if (mute):
            self.core.playback.pause()
        else:
            self.core.playback.resume()

    def change_playlist(self, value):
        self.selected_playlist= (self.selected_playlist+1) % len(self.playlists)
        logger.debug("Change playlist: {0}".format(self.selected_playlist))
        self.core.tracklist.clear()
        logger.debug("Playing {0}".format(self.playlists[self.selected_playlist].uri))
        tracks = self.core.playlists.get_items(self.playlists[self.selected_playlist].uri).get()
        logger.debug(tracks)
        track_uris = [track.uri for track in tracks]
        logger.debug("Tracks: {0}".format(track_uris))
        self.core.tracklist.add(uris=track_uris)
        self.core.playback.play()
        
    def reload_playlists(self):
        self.playlists = []
        for playlist in self.core.playlists.as_list().get():
            self.playlists.append(playlist)
            logger.debug(playlist)
        self.selected_playlist = 0
        logger.debug("Found {0} playlists.".format(len(self.playlists)))
