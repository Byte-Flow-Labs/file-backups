

class ResParseResult:
    def __init__(self, md5, path, mine_type, width, height, size, latitude, longitude, create_time,
                 duration=None, bitrate=None, framerate=None):
        self.md5 = md5
        self.path = path
        self.mine_type = mine_type
        self.width = width
        self.height = height
        self.size = size
        self.latitude = latitude
        self.longitude = longitude
        self.create_time = create_time
        self.duration = duration
        self.bitrate = bitrate
        self.framerate = framerate