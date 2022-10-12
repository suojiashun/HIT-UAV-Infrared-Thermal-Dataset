import cv2
from lxml import etree
import json
from pathlib import Path
import random


def parseXML(root, path):
    parser = etree.XMLParser(encoding='utf-8')
    xmlTree = etree.parse(path, parser).getroot()

    # get the corresponding image path
    filename = xmlTree.find('filename').text
    size = xmlTree.find('size')
    depth = size.find('depth').text
    imgPath = str(Path(root).joinpath('JPEGImages', filename))

    if depth == '1':
        img = cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE)
    else:
        img = cv2.imread(imgPath)

    for obj in xmlTree.findall('object'):
        objClass = obj.find('name').text
        if objClass == 'DontCare':
            continue

        bbox = obj.find('bndbox')
        xmin = int(bbox.find('xmin').text)
        ymin = int(bbox.find('ymin').text)
        xmax = int(bbox.find('xmax').text)
        ymax = int(bbox.find('ymax').text)

        img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), 255, thickness=2)
    return img


def main():
    root = 'voc_output'
    annotations = list(Path(root).joinpath('Annotations').iterdir())
    random.shuffle(annotations)

    for annotation in annotations:
        img = parseXML(root, str(annotation))

        cv2.namedWindow('img', cv2.WINDOW_NORMAL)
        cv2.imshow('img', img)
        if cv2.waitKey(2000) == 27:
            break


if __name__ == '__main__':
    main()
