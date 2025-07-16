# https://pub.smpte.org/pub/st2110-20/st2110-20-2022.pdf
# proper formats for tests cheatsheet
# https://gstreamer.freedesktop.org/documentation/additional/design/mediatype-video-raw.html

pgroup_dictionary = {
    "YCbCr": {
        "4:2:2": {
            8: {
                "size": 4,
                "coverage": 2,
                "pixel_components_amount": 4,
                "shift_multipliers": [[2, 1, 3], [0, 1, 3]]
                #sample order C’B,Y0’,C’R,Y1’
                #checked
            },
            10: {
                "size": 5,
                "coverage": 2,
                "pixel_components_amount": 4,
                "shift_multipliers": [[2, 1, 3], [0, 1, 3]]
                #sample order C’B,Y0’,C’R,Y1’
                #checked
            },
        },
    },
    "RGB": {
        "4:4:4": {
            8: {
                "size": 3,
                "coverage": 1,
                "pixel_components_amount": 3,
                "shift_multipliers": [[2, 1, 0]]
                #sample order R, G, B
                #checked
            },
        },
    }
}