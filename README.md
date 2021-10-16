## Merkury1080P (CW017) Rooting and Customization


### THIS IS A FORK of https://github.com/guino/Merkury1080P/
Follow instructions below except all files in mmc should be good.

I used this busybox for my best results.
https://busybox.net/downloads/binaries/1.21.1/busybox-armv5l


### TL;DR

You can jump to the **Conclusion** section all the way at the bottom if you just want to the steps to root the camera (and don't care about the details on how we got to them).

#### Summary

I created this repo to catalog information related to the Merkury 1080P (CW017) camera since it cannot be rooted with information from https://github.com/guino/Merkury720 nor https://github.com/guino/BazzDoorbell/issues/2 as it has different bootloader/address and different ppsapp (version 4.0.x as of writing this).

#### Hardware

This is what the device looks like (Other brand devices may look similar with the same hardware/software in them):

![Merkury1080P](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/cw017.jpg)

#### Getting Serial Access

I do not have an actual device to work with so all the work on the device was done in collaboration with @parkerlreed and if you are interested in the full discussion/progress it can be viewed at the original issue posted here: https://github.com/guino/BazzDoorbell/issues/21

Since the existing processes for 2.7.x and 2.9.x devices did not work for this camera, the only options left involved opening the camera to either connect a serial port (to try and see why the previous methods were failing) OR to use a hardware programmer to read the flash so it could be reviewed.

Here are the pictures from the inside:

![Inside1](https://user-images.githubusercontent.com/841440/107162854-eb9ca800-6973-11eb-97fc-4dedb2363854.jpg)

![Inside2](https://user-images.githubusercontent.com/841440/107163325-f7d63480-6976-11eb-90f5-620c92721cfb.jpg)

Here's a close up of the flash chip (3.3v/VCC/pin 8 circled) and the 4 pads for UART (bottom right):

![Flash](https://user-images.githubusercontent.com/4961810/107163562-23a5ea00-6978-11eb-9f2f-9f7b5ca0d73e.jpeg)

Here's the rig @parkerlreed put together to connect to the UART using a jetson nano board (a pi board would work too):

![Serial](https://user-images.githubusercontent.com/841440/107467503-25b4a800-6b34-11eb-81ab-b5abdaa37489.jpg)

#### Rooting

By default the device only had port 6668 open (tuya service port). Once we got a serial output I notice similarities between this hardware and older hardware with 2.7.x firmware but most importantly the load address was changed from 81808000 (on 2.7.x) to 81C08000 on this firmware (4.0.6):

```
## Booting kernel from Legacy Image at 81c08000 ...
   Image Name:   Linux-3.4.35
   Image Type:   ARM Linux Kernel Image (uncompressed)
   Data Size:    2789360 Bytes = 2.7 MiB
   Load Address: 81c08000
   Entry Point:  81c08040
   Verifying Checksum ... OK
   XIP Kernel Image ... OK

Starting kernel ...
```

Once we noticed that I suggested modifying the env and ppsMmcTool.txt files to have the correct address and then try applying the hack in the same manner as in https://github.com/guino/Merkury720 -- once everything was adjusted the process worked correctly and the device was rooted:

![ROOTED](https://user-images.githubusercontent.com/841440/107464107-8b516600-6b2d-11eb-8c76-2b5bf2e54b3c.png)

The SD card also got a copy of the application files: 
![FILES](https://user-images.githubusercontent.com/841440/107462873-0e24f180-6b2b-11eb-9b21-b5336aae932b.png)

With the ppsapp at hand it was time to take a look at this different (new?) firmware 4.0.x in ghidra.

#### Customization

With the rooting applied we immediately got telnet and httpd working (for download/scripting support). While working on the rooting process we also added a ppsFactoryTool.txt into the SD card which after looking in ghidra is actually what opened the http server on port 8090 (which used to be on port 80 on 2.7.x and 2.9.x firmware). So basically by adding that we can use the http urls such as http://admin:056565099@IP:8090/proc/cmdline like before (notice the port 8090 on the URL):

```
mem=64M console=ttySAK0,115200n8 loglevel=10 mtdparts=spi0.0:256k(bld),64k(env),64k(enc),64k(sysflg),3m(sys),4032k(app),640k(cfg) ppsAppParts=5 ip=0 - ip=30;/mnt/mmc01/initrun.sh)&:::::;date>/tmp/hack;(sleep
```

Unfortunately this firmware no longer has the 'echoshow' functions as in the 2.7.x and 2.9.x firmware, but it does have onvif support (disabled by default) which also has a working RTSP server with it. The main problem though is that this ppsapp has quite a bit of a different structure when it comes to the main function and initialization which seems to be more modular and lets the SDK handle more of how the functions are called.

To enable ONVIF the first thing we tried was to set **onvif_enable** to **1** in /home/cfg/tuya_config.json -- that did not work as it seems the device downloads the settings from the tuya servers and rebuilds the file on the fly (likely comparing for any changes).

That not working I searched the code that 'loads' the onvif_enable setting (CTRL+SHIFT+E on main window and typed in **onvif_enable** and clicked 'all fields'), which brought me to the function that reads the 'tuya_config.json' file and originally had this in regards to the onvif_enable setting:

![ONVIF1](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/onvif_enable1.png)

So I selected the function that sets the onvif_enable setting, right clicked on the **bl** instruction and selected 'Patch Instruction' which I changed to **mov r0,#0x1** to simulate the function returning a value of 1 for the setting:

![ONVIF2](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/onvif_enable2.png)

After testing (and looking at output from ppsapp) this proved not enough to force enable the onvif feature, so double clicked on the setting itself (the DAT_002a8848) and looked at all references which **write** to that address (the ones marked with **(W)** in ghidra) and found 2 more instances besides the one I already had patched above, the first one was:

![ONVIF3](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/onvif_enable3.png)

Which I changed to this in order to force the setting to 1:

![ONVIF4](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/onvif_enable4.png)

And the last one was:

![ONVIF5](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/onvif_enable5.png)

Which I changed to this in order to force the setting to 1:

![ONVIF6](https://raw.githubusercontent.com/guino/Merkury1080P/main/img/onvif_enable6.png)

That beind done there was basically no way the code could change the setting so here are the 3 changes we made in ppsapp with a hex editor (you can find more details on using ghidra and calculating the addresses to change in this repo: https://github.com/guino/ppsapp-rtsp):

```
$ diff 1.hex 2.hex 
1842c1842
< 00007310: 0020 a0e3 a021 83e5 5830 9fe5 0020 a0e3  . ...!..X0... ..
---
> 00007310: 0020 a0e3 a021 83e5 5830 9fe5 0120 a0e3  . ...!..X0... ..
1969c1969
< 00007b00: d821 c3e1 0200 a0e1 0310 a0e1 0ccb 08eb  .!..............
---
> 00007b00: d821 c3e1 0200 a0e1 0310 a0e1 0100 a0e3  .!..............
2844c2844
< 0000b1b0: 0420 93e5 8430 9fe5 a821 83e5 7c30 9fe5  . ...0...!..|0..
---
> 0000b1b0: 0120 a0e3 8430 9fe5 a821 83e5 7c30 9fe5  . ...0...!..|0..
```

 Once loaded we were able to confirm that the onvif server was started on port 8000 and that the RTSP server was running on port 8554 with the URLs: `rtsp://IP:8554//Streaming/Channels/101` (HD) and `rtsp://IP:8554//Streaming/Channels/102` (SD) as confirmed by @parkerlreed waving success:

![SUCCESS](https://user-images.githubusercontent.com/841440/108290352-354c7600-715e-11eb-98ae-f24d3b7f0206.png)

#### MJPEG/SNAP and Play features

Before we got ONVIF working I was pleasantly surprised that despite all the internal changes in ppsapp the instructions from https://github.com/guino/ppsapp-rtsp#if-you-want-to-get-snapcgi-and-mjpegcgi-working and https://github.com/guino/ppsapp-rtsp#if-you-want-to-get-playcgi-working still work to find the addresses used for MJPEG, SNAPSHOT and PLAY features, so there's no need to provide detail on those (just use the two links posted).

#### Conclusion

I have to thank @parkerlreed for doing all of the manual work on this since I don't have the camera and I am certain he agrees that this project was 100% successful. I may still look into disabling the 'online' requirement for the device but the camera is definitely rooted and customized with the features we wanted to get.

Here you can find the files required to hack (root) the camera using the steps described in https://github.com/guino/Merkury720 -- The differences are:
* Copy the 3 files posted [here](https://github.com/guino/Merkury1080P/tree/main/mmc) **over** of the mmc files on the SD card from the original instructions
* Create the ppsFactoryTool.txt file as described in the original instructions so you enable the http server for URLs like http://admin:056565099@IP:8090/proc/cmdline
* Make sure to add **:8090** to each URL in the original instructions (as I did in the previous link)
* It has been pointed out that some of the URLs (i.e. /devices/deviceinfo) have user/password admin:admin like: http://admin:admin@IP:8090/devices/deviceinfo so if you can't get a URL to open with admin:056565099, try admin:admin as well (I don't have the device to know which URLs use which user/password combination)

If you have a different ppsapp feel free to open an issue and request it to be patched, I just ask that you include the response of http://admin:056565099@IP:8090/devices/deviceinfo with the ppsapp (zip) file so I can create a patch for it.

If you'd like to buy me a beer/coffee in appreciation of the effort I put in to make the above possible, feel free to:

http://paypal.me/wbbo

cash app: $wbbo

Enjoy!
