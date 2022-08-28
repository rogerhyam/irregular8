import time
from picamera2 import Picamera2, Preview

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
print(picam2.camera_controls)
time.sleep(2)
picam2.set_controls({"ExposureValue": 0})
print(picam2.camera_controls)


