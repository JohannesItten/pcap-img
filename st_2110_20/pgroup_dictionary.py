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
        "4:4:4": {
            8: {
                "size": 3,
                "coverage": 1,
                "pixel_components_amount": 3,
                "shift_multipliers": [[2, 1, 0]]
                #sample order R, G, B
            },
            10: {
                "size": 15,
                "coverage": 4,
                "pixel_components_amount": 12,
                "shift_multipliers": [[11, 10, 9], [8, 7, 6], [5, 4, 3], [2, 1, 0]]
                # R0, G0, B0, R1, G1, B1,
                # R2, G2, B2, R3, G3, B3
            }
        },
    }
}