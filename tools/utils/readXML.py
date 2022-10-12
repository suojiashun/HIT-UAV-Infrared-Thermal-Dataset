from lxml import etree
import os
import json
import argparse
from pathlib import Path
from PIL import Image
import random
import numpy as np
import cv2
import shutil
from tqdm import tqdm


class XMLReader():
    """
    parse the xml from a xml file or xml files from a folder
    """

    def __init__(self, path):
        # path can be a xml file or a folder which contains xml files
        if os.path.isdir(path) and os.path.exists(path):
            self.filepaths = []
            files_ = os.listdir(path)
            for file in files_:
                if os.path.splitext(file)[1] == '.xml':
                    self.filepaths.append(os.path.join(path, file))
        elif os.path.isfile(path) and os.path.splitext(path)[1] == '.xml':
            self.filepaths = [path]

        self.annotation = {}

        # call the parse function
        self.parseXML()

    def parseXML(self):
        for filepath in self.filepaths:
            parser = etree.XMLParser(encoding='utf-8')
            xmltree = etree.parse(filepath, parser).getroot()
            filename = xmltree.find('filename').text
            path = xmltree.find('path').text

            self.annotation[filename] = {}
            self.annotation[filename]['picname'] = os.path.basename(path)

            size = xmltree.find('size')
            self.annotation[filename]['size'] = {}
            self.annotation[filename]['size']['width'] = int(size.find('width').text)
            self.annotation[filename]['size']['height'] = int(size.find('height').text)
            self.annotation[filename]['size']['depth'] = int(size.find('depth').text)

            # save the non-OBB and OBB respectively
            self.annotation[filename]['nobbox'] = []
            self.annotation[filename]['robbox'] = []

            for obj in xmltree.findall('object'):
                typeItem = obj.find('type')

                tmp = {}

                if typeItem.text == 'bndbox':
                    bndbox = obj.find('bndbox')

                    tmp['category'] = obj.find('name').text

                    difficult = False

                    tmp['xmin'] = int(bndbox.find('xmin').text)
                    tmp['ymin'] = int(bndbox.find('ymin').text)
                    tmp['xmax'] = int(bndbox.find('xmax').text)
                    tmp['ymax'] = int(bndbox.find('ymax').text)

                    if obj.find('difficult') is not None:
                        difficult = bool(int(obj.find('difficult').text))
                    tmp['difficult'] = difficult

                    self.annotation[filename]['nobbox'].append(tmp)

                elif typeItem.text == 'robndbox':
                    robndbox = obj.find('robndbox')

                    tmp['category'] = obj.find('name').text

                    difficult = False

                    tmp['cx'] = float(robndbox.find('cx').text)
                    tmp['cy'] = float(robndbox.find('cy').text)
                    tmp['w'] = float(robndbox.find('w').text)
                    tmp['h'] = float(robndbox.find('h').text)
                    tmp['angle'] = float(robndbox.find('angle').text)

                    if obj.find('difficult') is not None:
                        difficult = bool(int(obj.find('difficult').text))
                    tmp['difficult'] = difficult

                    self.annotation[filename]['robbox'].append(tmp)

    def getAnnotation(self):
        return self.annotation


class JSONMaker():
    """
    make the json file for the dataset, call the XMLReader to parse the xml file
    """

    def __init__(self, datasetPath, infoFolderPath, outFolder, bboxType, train_proportion, val_proportion,
                 existedFilePath):
        self.infoPath = os.path.join(infoFolderPath, 'info.txt')
        self.licensePath = os.path.join(infoFolderPath, 'license.txt')
        self.scenarioPath = os.path.join(infoFolderPath, 'scenario.txt')
        self.weatherPath = os.path.join(infoFolderPath, 'weather.txt')
        self.categoryPath = os.path.join(infoFolderPath, 'category.txt')

        self.outFolder = outFolder
        self.datasetPath = datasetPath
        self.bboxType = bboxType

        self.trainProportion = train_proportion
        self.valProportion = val_proportion

        self.existedFilePath = existedFilePath

        self.imgPaths = {'train': [], 'val': [], 'test': []}
        self.imgSection = {'train': [], 'val': [], 'test': []}
        self.annotationSection = {'train': [], 'val': [], 'test': []}

        self.LOGFILE = {}
        self.LOGFILE['summary'] = {}
        self.LOGFILE['xml_no_existence'] = []

        # assign unique ID for img and bbox
        self.numIMG = 0
        self.numBBOX = 0

        self.initOutput()

    def handleExisted(self, existedFilePath):
        # make sure the existed imgs in train/val/test datasets won't change after add new images
        if existedFilePath is not None and Path(existedFilePath).exists() and Path(existedFilePath).suffix == '.json':
            with open(existedFilePath, 'r+') as f:
                existedFile = json.load(f)

            existed_imgNames = []
            for section in ['train', 'val', 'test']:
                for idx in range(len(existedFile[section])):
                    existed_imgNames.append(existedFile[section][idx])

            unique_existed_imgIDS = set(existed_imgNames)
            assert len(existed_imgNames) == len(unique_existed_imgIDS), 'Error: The image id in map.json is not unique!'

            return existedFile, existed_imgNames
            # for idx in existed_imgNames:
            #     imgIDS.remove(idx)
        else:
            print('[*] Make the file from scratch')
            existedFile = {'train': [], 'val': [], 'test': []}
            return existedFile, None

    def initOutput(self):
        self.imgFolderTrain = Path(self.outFolder).joinpath('images', 'train')
        self.imgFolderVal = Path(self.outFolder).joinpath('images', 'val')
        self.imgFolderTest = Path(self.outFolder).joinpath('images', 'test')
        self.annotationFolder = Path(self.outFolder).joinpath('annotations')

        self.imgFolderTrain.mkdir(parents=True, exist_ok=True)
        self.imgFolderVal.mkdir(parents=True, exist_ok=True)
        self.imgFolderTest.mkdir(parents=True, exist_ok=True)
        self.annotationFolder.mkdir(parents=True, exist_ok=True)

    def parseInfo(self):
        with open(self.infoPath, 'r') as f:
            data = f.read().splitlines()

        self.infoSection = {}

        for line in data:
            key, value = line.split(':')
            key = key.strip()
            value = value.strip()
            self.infoSection[key] = value

    def parseLicense(self):
        with open(self.licensePath, 'r') as f:
            data = f.read().splitlines()

        self.licenseSection = []

        for line in data:
            key, value = line.split(':')
            key = key.strip()
            value = value.strip()

            tmp = {}
            tmp[key] = value
            self.licenseSection.append(tmp)

    def parseScenario(self):
        with open(self.scenarioPath, 'r') as f:
            data = f.read().splitlines()

        self.scenarioSection = []

        for idx, line in enumerate(data):
            tmp = {}
            tmp['id'] = idx
            tmp['name'] = line.strip()
            self.scenarioSection.append(tmp)

    def parseWeather(self):
        with open(self.weatherPath, 'r') as f:
            data = f.read().splitlines()

        self.weatherSection = []

        for idx, line in enumerate(data):
            tmp = {}
            tmp['id'] = idx
            tmp['name'] = line.strip()
            self.weatherSection.append(tmp)

    def parseCategory(self):
        with open(self.categoryPath, 'r') as f:
            data = f.read().splitlines()

        self.categorySection = []

        # save the categories for reading xml
        self.category = []

        for idx, line in enumerate(data):
            tmp = {}
            tmp['id'] = idx
            tmp['name'] = line.strip()
            self.categorySection.append(tmp)
            self.category.append(line.strip())

    def getPaths(self):
        imgExt = ['jpg', 'jpeg', 'png']

        existedFile, existed_imgNames = self.handleExisted(self.existedFilePath)

        imgPaths = []
        for root, folders, files in os.walk(self.datasetPath):
            for imgFile in files:
                imgFullPath = os.path.join(root, imgFile)
                if os.path.splitext(imgFullPath)[1][1:] in imgExt:
                    xmlFullPath = os.path.splitext(imgFullPath)[0] + '.xml'
                    if os.path.exists(xmlFullPath):
                        imgPaths.append(imgFullPath)
                    else:
                        self.LOGFILE['xml_no_existence'].append(imgFullPath)

        if existed_imgNames is not None:
            remove_idx = len(imgPaths)

            # find the existed file, and remove them from the imgPaths
            for imgPath in reversed(imgPaths):
                remove_idx -= 1
                if Path(imgPath).stem in existedFile['train']:
                    imgPaths.pop(remove_idx)
                    self.imgPaths['train'].append(imgPath)
                elif Path(imgPath).stem in existedFile['val']:
                    self.imgPaths['val'].append(imgPath)
                    imgPaths.pop(remove_idx)
                elif Path(imgPath).stem in existedFile['test']:
                    self.imgPaths['test'].append(imgPath)
                    imgPaths.pop(remove_idx)
                else:
                    pass


        total_new_img_num = len(imgPaths)
        assert total_new_img_num > 0, 'No new image in the dataset'
        new_train_img_num = np.ceil(self.trainProportion * total_new_img_num)
        new_val_img_num = np.ceil(self.valProportion * total_new_img_num)

        # shuffle the imgPaths
        random.shuffle(imgPaths)
        for idx, imgPath in enumerate(imgPaths):
            if idx < new_train_img_num:
                self.imgPaths['train'].append(imgPath)
                existedFile['train'].append(str(Path(imgPath).stem))
            elif idx < (new_train_img_num + new_val_img_num):
                self.imgPaths['val'].append(imgPath)
                existedFile['val'].append(str(Path(imgPath).stem))
            else:
                self.imgPaths['test'].append(imgPath)
                existedFile['test'].append(str(Path(imgPath).stem))
        with open('existedFile.json', 'w+') as f:
            json.dump(existedFile, f)

    def parseImage(self):
        for part in ['train', 'val', 'test']:
            print('[*] Parsing %s images' % part)
            for imgPath in tqdm(self.imgPaths[part]):
                splitPath = Path(imgPath).parts
                # get the information from the img name
                img_info = os.path.splitext(splitPath[-1])[0].split('_')

                width, height = Image.open(imgPath, 'r').size

                tmp = {}
                tmp['id'] = self.numIMG
                tmp['width'] = width
                tmp['height'] = height
                tmp['depth'] = len(Image.open(imgPath, 'r').split())
                tmp['filename'] = os.path.basename(imgPath)
                tmp['scenario'] = img_info[0]
                tmp['weather'] = img_info[3]
                tmp['perspective'] = img_info[2]
                tmp['altitude'] = img_info[1]
                tmp['date'] = splitPath[-2]

                self.imgSection[part].append(tmp)
                # the id of img +1
                self.numIMG += 1

    def parseAnnotation(self):
        self.LOGFILE['error_bbox'] = {}
        self.LOGFILE['error_category'] = {}
        # initial the category counter
        for category in self.category:
            self.LOGFILE['summary'][category] = 0

        image_id = -1
        for part in ['train', 'val', 'test']:
            print('[*] Parsing %s annotations' % part)
            # read the xml files from folders one by one
            for imgPath in tqdm(self.imgPaths[part]):
                image_id += 1
                xmlPath = os.path.splitext(imgPath)[0] + '.xml'
                xmlreader = XMLReader(xmlPath)
                annotations = xmlreader.getAnnotation()
                # get the annotation for each xml file
                for key in annotations:
                    for bbox in annotations[key]['robbox']:
                        tmp = {}
                        tmp['id'] = self.numBBOX
                        tmp['image_id'] = image_id
                        if bbox['category'] in self.category:
                            tmp['category_id'] = self.category.index(bbox['category'])
                        else:
                            self.LOGFILE['error_category'][imgPath] = bbox['category']
                            continue

                        tmp['difficult'] = bbox['difficult']
                        tmp['bbox'] = list([bbox['cx'], bbox['cy'], bbox['w'], bbox['h'], bbox['angle']])

                        self.annotationSection[part].append(tmp)

                        # count the bbox in category
                        self.LOGFILE['summary'][bbox['category']] += 1
                        # the id of bbox +1
                        self.numBBOX += 1
                    if annotations[key]['nobbox']:
                        self.LOGFILE['error_bbox'][imgPath] = annotations[key]['nobbox']

    def makeJSON(self):
        # get the sections
        self.parseInfo()
        self.parseLicense()
        self.parseScenario()
        self.parseWeather()
        self.parseCategory()
        self.getPaths()
        self.parseImage()
        self.parseAnnotation()

        self.LOGFILE['summary']['totalIMG'] = self.numIMG
        self.LOGFILE['summary']['totalBBOX'] = self.numBBOX

        # make the sections together and save file
        for part in ['train', 'val', 'test']:
            print('[*] Making new %s json file' % part)
            jsonFile = {}
            jsonFile['info'] = self.infoSection
            jsonFile['licenses'] = self.licenseSection
            jsonFile['scenarios'] = self.scenarioSection
            jsonFile['weather'] = self.weatherSection
            jsonFile['images'] = self.imgSection[part]
            jsonFile['categories'] = self.categorySection
            jsonFile['annotations'] = self.annotationSection[part]

            with open(os.path.join(self.annotationFolder, part + '.json'), 'w', encoding='utf-8') as f:
                json.dump(jsonFile, f)

        with open(os.path.join(self.annotationFolder, 'log.json'), 'w', encoding='utf-8') as f:
            json.dump(self.LOGFILE, f)

    def copyImgs(self):
        for part in ['train', 'val', 'test']:
            print('[*] Copying images to %s dataset' % part)
            for imgPath in tqdm(self.imgPaths[part]):
                if part == 'train':
                    newPath = Path(self.imgFolderTrain).joinpath(Path(imgPath).name)
                elif part == 'val':
                    newPath = Path(self.imgFolderVal).joinpath(Path(imgPath).name)
                else:
                    newPath = Path(self.imgFolderTest).joinpath(Path(imgPath).name)
                shutil.copy(imgPath, newPath)

    def getJSONSTATE(self):
        return self.numIMG, self.numBBOX

    def showIMG(self):
        color = np.random.randint(0, 255, (20, 3))
        while True:
            part = random.choice(['train', 'val', 'test'])
            imgInfo = random.choice(self.imgSection[part])
            imgID = imgInfo['id']
            imgPath = imgInfo['filename']
            imgScenarioIdx = int(imgInfo['scenario'])
            imgScenario = self.scenarioSection[imgScenarioIdx]['name']
            imgWeatherIdx = int(imgInfo['weather'])
            imgWeather = self.weatherSection[imgWeatherIdx]['name']
            imgPespective = int(imgInfo['perspective'])
            imgAltitude = int(imgInfo['altitude'])
            imgDate = imgInfo['date']

            img_ro = cv2.imread(str(Path(self.outFolder).joinpath('images', part, imgPath)))
            img_no = img_ro.copy()

            selectedBBOX = []
            for annotation in self.annotationSection[part]:
                if annotation['image_id'] == imgID:
                    selectedBBOX.append(annotation)

            for bboxInfo in selectedBBOX:
                categoryIdx = bboxInfo['category_id']
                category = self.categorySection[categoryIdx]['name']
                bbox = bboxInfo['bbox']

                roPoints = getRoPoint(bbox)
                img_ro = cv2.polylines(img_ro, [np.array(roPoints, np.int32).reshape((-1, 1, 2))], True,
                                       (color[categoryIdx, :]).tolist(), 2)

                noPoints = getNoPoint(roPoints)
                cv2.rectangle(img_no, noPoints[0], noPoints[1], (color[categoryIdx, :]).tolist(), 2)

            cv2.putText(img_ro, '%s,%s,%s,%d,%d,%s with oriented BBOX' % (
                part, imgScenario, imgWeather, imgPespective, imgAltitude, imgDate), (5, 10), cv2.FONT_HERSHEY_PLAIN,
                        1, [255, 255, 255], 2)

            cv2.putText(img_no, '%s, %s,%s,%d,%d,%s with normal BBOX' % (
                part, imgScenario, imgWeather, imgPespective, imgAltitude, imgDate), (5, 10), cv2.FONT_HERSHEY_PLAIN,
                        1, [255, 255, 255], 2)

            cv2.namedWindow('img_ro', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            cv2.namedWindow('img_no', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            cv2.imshow('img_ro', img_ro)
            cv2.imshow('img_no', img_no)

            key = cv2.waitKey(0) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('n'):
                continue


# calculate the point from [cx, cy, w, h, angle]
def getRoPoint(bbox, difficult=0):
    cx = float(bbox[0])
    cy = float(bbox[1])
    w = float(bbox[2])
    h = float(bbox[3])
    angle = float(bbox[4])

    p0x, p0y = rotatePoint(cx, cy, cx - w / 2, cy - h / 2, -angle)
    p1x, p1y = rotatePoint(cx, cy, cx + w / 2, cy - h / 2, -angle)
    p2x, p2y = rotatePoint(cx, cy, cx + w / 2, cy + h / 2, -angle)
    p3x, p3y = rotatePoint(cx, cy, cx - w / 2, cy + h / 2, -angle)

    points = [(p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y)]
    return points


# transform from cx, cy, w, h, angle to the four corners of bboxes
def rotatePoint(xc, yc, xp, yp, theta):
    import math
    # x, y coordinate offset from the corner point to center point
    xoff = xp - xc
    yoff = yp - yc

    cosTheta = math.cos(theta)
    sinTheta = math.sin(theta)
    pResx = cosTheta * xoff + sinTheta * yoff
    pResy = - sinTheta * xoff + cosTheta * yoff
    return int(xc + pResx), int(yc + pResy)


def getNoPoint(roPoints):
    totalX = [x[0] for x in roPoints]
    totalY = [x[1] for x in roPoints]
    xmin = min(totalX)
    ymin = min(totalY)
    xmax = max(totalX)
    ymax = max(totalY)
    return [(xmin, ymin), (xmax, ymax)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', '-D', type=str, default='../oriDataset', help='Path to the dataset root folder')
    parser.add_argument('--train_proportion', '-T', type=float, default=0.7, help='Training dataset proportion')
    parser.add_argument('--val_proportion', '-V', type=float, default=0.1, help='Valid dataset proportion')
    parser.add_argument('--infoFolder', '-I', type=str, default='../info', help='Path to the information folder')
    parser.add_argument('--output', '-O', type=str, default='Pegasus', help='Folder for JSON file and log file')
    parser.add_argument('--existedFile', '-M', type=str, default='./existedFile.json', help='images map')
    parser.add_argument('--bboxType', '-B', type=int, default=0, help='OBB: 0, Normal: 1')
    config = parser.parse_args()

    jsonMaker = JSONMaker(config.dataset, config.infoFolder, config.output, config.bboxType, config.train_proportion,
                          config.val_proportion, config.existedFile)
    jsonMaker.makeJSON()

    numIMG, numBBOX = jsonMaker.getJSONSTATE()
    print('[*] total image with xml: %d, total bbox: %d' % (numIMG, numBBOX))

    jsonMaker.copyImgs()

    jsonMaker.showIMG()
