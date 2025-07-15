# pcap-img
Simple CLI tool to extract images from ST-2110-20 pcap files. All images will be converted to 16-bit .png files. Based on [dpkt](https://github.com/kbandla/dpkt) and [OpenCV](https://opencv.org)

## Usage example
```
python main.py -f pcap/ST2110-20_720p_59_94_color_bars.pcap -vw 1280 -vh 720 -vs p -c YCbCr -s 4:2:2 -d 10 -l 3 -dir test-images
```

## Known limitations
Works only with these color spaces: YCbCr and RGB (linear only), except 16f bit depth. Sampling 4:2:0 is also not supported.

The limitations are due to the fact that I do not have access to files with other parameters at the moment. Therefore, I cannot test the functionality. If you have the opportunity to share the files, please [provide me a link](https://t.me/drunkninja).

## Possible options
```
  -f, --filename FILENAME pcap file absolute path
  -vw, --width WIDTH           video width
  -vh, --height HEIGHT         video height
  -vs, --scan {i,p}            video scan
  -c, --colorspace {YCbCr,RGB} colorspace
  -s, --sampling {4:2:2,4:4:4} sampling
  -d, --depth {8,10,12,16}     bit depth
  -l, --limit LIMIT            image amount limit
  -dir, --directory DIRECTORY  output directory for images
```
## Other notes
Test files in directory pcap, taken from here:
[PCAP Zoo](https://github.com/NEOAdvancedTechnology/ST2110_pcap_zoo)