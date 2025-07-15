# https://pub.smpte.org/pub/st2110-20/st2110-20-2022.pdf
pgroup_dictionary = {
    "YCbCr": {
        "4:2:2": {
            8: {
                "size": 4,
                "coverage": 2,
                "pixel_components_amount": 4,
                "shift_multipliers": [[2, 1, 3], [0, 1, 3]]
                #sample order C’B,Y0’,C’R,Y1’
            },
            10: {
                "size": 5,
                "coverage": 2,
                "pixel_components_amount": 4,
                "shift_multipliers": [[2, 1, 3], [0, 1, 3]]
                #sample order C’B,Y0’,C’R,Y1’
            },
            12: {
                "size": 6,
                "coverage": 2,
                "pixel_components_amount": 4,
                "shift_multipliers": [[2, 1, 3], [0, 1, 3]]
                #sample order C’B,Y0’,C’R,Y1’
            },
            16: {
                "size": 8,
                "coverage": 2,
                "pixel_components_amount": 4,
                "shift_multipliers": [[2, 1, 3], [0, 1, 3]]
                #sample order C’B,Y0’,C’R,Y1’
            }
        },
        "4:4:4": {
            8: {
                "size": 3,
                "coverage": 1,
                "pixel_components_amount": 3,
                "shift_multipliers": []
                #sample order C’B,Y’,C’R
            },
            10: {
                "size": 15,
                "coverage": 4,
                "pixel_components_amount": 3,
                "shift_multipliers": []
                #sample order C’B,Y’,C’R
            },
            12: {
                "size": 3,
                "coverage": 1,
                "pixel_components_amount": 3,
                "shift_multipliers": []
                #sample order C’B,Y’,C’R
            },
        }
    },
    "RGB": {
        "4:2:2": {

        },
        "4:4:4": {

        }
    }
}