Mopidy-Headless
===============

This is an [mopidy](https://www.mopidy.com) extension to control volume and playlists just with scroll devices like mouse-wheel or dedicated [rotary encoders](https://github.com/avanc/rotary-encoder).

Installation
------------

It is available in [Arch Linux User Repository](https://aur.archlinux.org/packages/mopidy-headless-git):
    trizen -Sa mopidy-headless
    

Configuration
-------------
Add the configuration to mopidy.conf. The default configuration uses the first input device and assumes it is a mouse:
    [headless]
    enabled = true
    
    volume_device = /dev/input/event2
    volume_axis = REL_WHEEL
    
    playlist_device = /dev/input/event2
    playlist_axis = REL_X
    
    mute_device = /dev/input/event2
    mute_key = BTN_LEFT

If using the rotary-encoder device driver as mentioned above, the configuration might look as follows:

    [headless]
    enabled = true

    volume_device = /dev/input/event0
    volume_axis = REL_WHEEL
    
    playlist_device = /dev/input/event2
    playlist_axis = REL_WHEEL
    
    mute_device = /dev/input/event0
    mute_key = BTN_LEFT
    
    shutdown_command = "/usr/bin/sudo /usr/bin/systemctl poweroff"
