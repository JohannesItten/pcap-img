import st_2110_20.pgroup_dictionary as pd


class Pgroup:
    def __init__(self, colorspace, sampling, depth):
        self.colorspace = colorspace
        self.sampling = sampling
        self.depth = depth
        #TODO: process Not Found Data For Colorspace And Sampling Error
        pgroup_table_values = self._get_pgroup_table_values()
        if pgroup_table_values is None:
            self._init_empty()
            return
        self.size = pgroup_table_values["size"]
        self.pixel_amount = pgroup_table_values["coverage"]
        self.pixel_components_amount = pgroup_table_values["pixel_components_amount"]
        self.shift_multipliers = pgroup_table_values["shift_multipliers"]
        self.shift = self.size * 8 // self.pixel_components_amount
        self.pixel_mask = (2 << (self.shift - 1)) - 1

    def _init_empty(self):
        self.size = 0
        self.pixel_amount = 0
        self.pixel_components_amount = 0
        self.shift_multipliers = []
        self.shift = 0
        self.pixel_mask = 0

    def _get_pgroup_table_values(self):
        try:
            return pd.pgroup_dictionary[self.colorspace][self.sampling][self.depth]
        except KeyError:
            return None
    
    def is_valid(self):
        return self.size > 0
    
    def get_pixels(self, pgroup_bytes):
        pixels = []
        #due to ST-2110-20 data is always Big Endian
        pgroup = int.from_bytes(pgroup_bytes, byteorder="big")
        for multipliers in self.shift_multipliers:
            pixel_components = []
            for m in multipliers:
                component = (pgroup >> (m * self.shift)) & self.pixel_mask
                pixel_components.append(component)
            pixels.append(pixel_components)
        return pixels
