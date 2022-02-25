import watchdog.events
import watchdog.observers
import watchdog.observers.polling
import time
import sys
import requests
import os
import pyvips
from pathlib import Path
from mytools.inference import detection

  
  
class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        self.state = {}
        self.headers = {"Authorization":"JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQ1OTY5OTUwLCJqdGkiOiI3YzcwZWRkMmRhMmQ0YzMyOGFjYTVjZjE2OTUyN2Q3OCIsInVzZXJfaWQiOjJ9.ogWhFnKccPdm0st7uoINB93ArximWLsq_QAopslAlag"}
        self.app_point="http://139.198.169.75:8072"
        self.maxsize=32768
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.tif'],
                                                             ignore_directories=True, case_sensitive=False)
  
    def on_created(self, event):
        print("Watchdog received created event - % s." % event.src_path)
        # self.send_to_system(event.src_path)
        # Event is created, you can process it now
  
    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        if not self.state.get(event.src_path):
            (scale_w,scale_h,dest_path) = self.zip_image(event.src_path)
            pic_id = self.send_to_system(dest_path)
            dia_id = self.getDiagnosisitemId(pic_id)
            labels = self.findLabels(event.src_path)
            labels = self.extractLabels(labels)
            labels = self.scaleLabels(labels,scale_w,scale_h)
            self.setLabels(dia_id,labels)



    
    def zip_image(self,src_path):
        dest_path=f"{Path(src_path).stem}.jpg"
        image = pyvips.Image.new_from_file(src_path, access='sequential')
        o_width=image.width
        o_height=image.height
        image = image.resize(self.maxsize / max(image.width, image.height))
        image.write_to_file(dest_path)
        return (1.0*image.width/o_width,1.0*image.height/o_height,dest_path)
    def send_to_system(self,src_path):
        historicalSize = -1
        while (historicalSize != os.path.getsize(src_path)):
            historicalSize = os.path.getsize(src_path)
            time.sleep(1)
        print("file copy has now finished")
        self.state[src_path]=True
        myobj = {"patient":1,"description":"def"}
        url = f'{self.app_point}/pathology/pathologypictureitems/'
        myfiles = {'pathologyPicture': open(src_path ,'rb')}
        x = requests.post(url, data = myobj,files = myfiles, headers = self.headers)
        print(x.text)
        return x.json()['id']
    def getDiagnosisitemId(self,pic_id):
        """利用图片ID，获取诊断号"""
        url = f"{self.app_point}/pathology/diagnosisitems/?pathologyPicture__id={pic_id}"
        x = requests.get(url,headers = self.headers)
        while not x.json():
            time.sleep(1)
            x = requests.get(url,headers = self.headers)
        print(x.text)
        return x.json()[0]["id"]
    def extractLabels(self,labels):
        print(labels)
        v={}
        for label in labels:
            t = v.get(label["category"],[])
            t.append(label)
            v[label["category"]]=t
        result = []
        for k in v:
            result += sorted(v[k],key=lambda x:-x["confidence"])[:10]
        return result
    def scaleLabels(self,labels,scale_w,scale_h):
        print(scale_w,scale_h)
        for label in labels:
            print(label)
            label["x"] = scale_w * label['xmin']
            label["w"] *= scale_w
            label["y"] = scale_h * label['ymin']
            label["h"] *= scale_h
            label["zoomLevel"] *= 20
            print(label)
        return(labels)

    def setLabels(self,dia_id,labels):
        """
        data=    {
             "category": "AGC(FN)-CC",
             "x": 520.087646484375,
             "y": 677.3016967773438,
             "w": 183.2255859375,
             "h": 141.117919921875,
             "zoomLevel": 1.0,
             "confidence": 1.0
         }
        """
        for label in labels:
            url = f"{self.app_point}/pathology/diagnosisitems/{dia_id}/labelitems/"
            x = requests.post(url, data = label, headers = self.headers)
            print(x.text)
    def findLabels(self,src_path,scale=0.5):
        """
        麦麦处理图片，返回labels
        labels = [{
             "category": "AGC(FN)-CC",
             "x": 520.087646484375,
             "y": 677.3016967773438,
             "w": 183.2255859375,
             "h": 141.117919921875,
             "zoomLevel": 1.0,
             "confidence": 1.0
         }]"""

        result = detection(src_path)
        if result["msg"] == "success":
             # 检测中没有进行报错，返回值是正确的
            labels = result["results"]
        else:
            # 如果出现异常，返回异常信息。具体问题具体分析 （主要是异常是图片路径的问题......）
            labels = result["results"]
        return labels

       
  
  
if __name__ == "__main__":
    src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = Handler()
    #observer = watchdog.observers.Observer()
    observer = watchdog.observers.polling.PollingObserver()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
