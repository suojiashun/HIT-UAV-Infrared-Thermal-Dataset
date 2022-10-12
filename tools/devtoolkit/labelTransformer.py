import json
from tqdm import trange
from lxml import etree
from pathlib import Path
import shutil


class LabelTransformer(object):
    def __init__(self, rootFolder='../utils/Pegasus', outFolder='output', outType='voc', copyIMG=True):
        """
        Transform the Pegasus's annotated file to voc/coco format.
        Args:
            rootFolder (str): The folder of the Pegasus dataset
            outFolder (str): The folder to place the transformed voc/coco dataset
            outType (str): voc or coco, by default: voc
            copyIMG (bool): copy the image to the output folder if it is true
        """
        self.jsonFolder = Path(rootFolder).joinpath('annotations')
        self.imgFolder = Path(rootFolder).joinpath('images')
        self.outFolder = outFolder
        self.outType = outType
        self.copyIMG = copyIMG
        self.jsonPaths = {}

        self.getJSONPath()

    def getJSONPath(self):
        """
        Prepare the JSON files.
        Returns:

        """
        annoFiles = ['train', 'val', 'test']
        for annoFile in annoFiles:
            self.jsonPaths[annoFile] = Path(self.jsonFolder).joinpath(annoFile).with_suffix('.json')
            assert Path(self.jsonPaths[annoFile]).exists() == True, '[!] %s is lost' % str(self.jsonPaths[annoFile])
        print('[*] found all JSON files')

    def obb2hbb(self, obb, flag='voc'):
        """
        Transform the annotations from oriented bbox to horizontal bbox.
        Args:
            obb (list): oriented bbox
            flag (str): voc or coco, by default voc

        Returns:

        """
        cx = float(obb[0])
        cy = float(obb[1])
        w = float(obb[2])
        h = float(obb[3])
        angle = float(obb[4])

        p0x, p0y = self.rotatePoint(cx, cy, cx - w / 2, cy - h / 2, -angle)
        p1x, p1y = self.rotatePoint(cx, cy, cx + w / 2, cy - h / 2, -angle)
        p2x, p2y = self.rotatePoint(cx, cy, cx + w / 2, cy + h / 2, -angle)
        p3x, p3y = self.rotatePoint(cx, cy, cx - w / 2, cy + h / 2, -angle)

        points = [(p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y)]

        totalX = [x[0] for x in points]
        totalY = [x[1] for x in points]
        xmin = min(totalX)
        ymin = min(totalY)
        xmax = max(totalX)
        ymax = max(totalY)

        if flag == 'voc':
            return xmin, ymin, xmax, ymax
        else:
            return xmin, ymin, xmax - xmin, ymax - ymin

    def rotatePoint(self, xc, yc, xp, yp, theta):
        import math
        # x, y coordinate offset from the corner point to center point
        xoff = xp - xc
        yoff = yp - yc

        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        pResx = cosTheta * xoff + sinTheta * yoff
        pResy = - sinTheta * xoff + cosTheta * yoff
        return int(xc + pResx), int(yc + pResy)

    def toVOC(self):
        """
        Main function to start transform the Pegasus's file to voc format.
        Returns:

        """
        # init folders in VOC format
        vocAnnotationFolder = Path(self.outFolder).joinpath('Annotations')
        vocImgFolder = Path(self.outFolder).joinpath('JPEGImages')
        vocImgsetFolder = Path(self.outFolder).joinpath('ImageSets', 'Main')

        vocAnnotationFolder.mkdir(parents=True, exist_ok=True)
        vocImgFolder.mkdir(parents=True, exist_ok=True)
        vocImgsetFolder.mkdir(parents=True, exist_ok=True)

        # create the train, trainval, val and test.txt
        ftrain = open(Path(vocImgsetFolder).joinpath('train.txt'), 'w')
        ftrainval = open(Path(vocImgsetFolder).joinpath('trainval.txt'), 'w')
        fval = open(Path(vocImgsetFolder).joinpath('val.txt'), 'w')
        ftest = open(Path(vocImgsetFolder).joinpath('test.txt'), 'w')

        # get path to the json file
        for key, value in self.jsonPaths.items():
            print('[*] start with %s' % key)

            with open(value, 'r') as f:
                jsonFile = json.load(fp=f)

            totalImgs = len(jsonFile['images'])

            annotations = jsonFile['annotations']

            totalAnnotations = len(annotations)

            for idx in trange(totalImgs):
                img_idx = int(jsonFile['images'][idx]['id'])
                img_name = Path(jsonFile['images'][idx]['filename']).name

                # check if need to copy the img to target folder
                if self.copyIMG:
                    shutil.copy(Path(self.imgFolder).joinpath(key, img_name), Path(vocImgFolder).joinpath(img_name))

                # create xml tree
                root = etree.Element('annotation')

                folder = etree.SubElement(root, 'folder')
                folder.text = './JPEGImages'

                filename = etree.SubElement(root, 'filename')
                filename.text = img_name

                source = etree.SubElement(root, 'source')
                source_database = etree.SubElement(source, 'database')
                source_database.text = 'The pegasus Database'
                source_annotation = etree.SubElement(source, 'annotation')
                source_annotation.text = 'Pegasus 2021'

                size = etree.SubElement(root, 'size')
                size_width = etree.SubElement(size, 'width')
                size_width.text = str(jsonFile['images'][idx]['width'])
                size_height = etree.SubElement(size, 'height')
                size_height.text = str(jsonFile['images'][idx]['height'])
                size_depth = etree.SubElement(size, 'depth')
                size_depth.text = str(jsonFile['images'][idx]['depth'])

                segmented = etree.SubElement(root, 'segmented')
                segmented.text = '0'

                for i in range(totalAnnotations):
                    # find the needed annotations
                    if annotations[i]['image_id'] == img_idx:
                        obj = etree.SubElement(root, 'object')
                        obj_name = etree.SubElement(obj, 'name')
                        obj_name.text = jsonFile['categories'][int(annotations[i]['category_id'])]['name']
                        obj_pose = etree.SubElement(obj, 'pose')
                        obj_pose.text = str(jsonFile['images'][idx]['perspective'])
                        obj_truncated = etree.SubElement(obj, 'truncated')
                        obj_truncated.text = '0'
                        obj_difficult = etree.SubElement(obj, 'difficult')
                        obj_difficult.text = str(int(annotations[i]['difficult']))
                        obj_bndbox = etree.SubElement(obj, 'bndbox')
                        xmin, ymin, xmax, ymax = self.obb2hbb(annotations[i]['bbox'])
                        obj_bndbox_xmin = etree.SubElement(obj_bndbox, 'xmin')
                        obj_bndbox_xmin.text = str(xmin)
                        obj_bndbox_ymin = etree.SubElement(obj_bndbox, 'ymin')
                        obj_bndbox_ymin.text = str(ymin)
                        obj_bndbox_xmax = etree.SubElement(obj_bndbox, 'xmax')
                        obj_bndbox_xmax.text = str(xmax)
                        obj_bndbox_ymax = etree.SubElement(obj_bndbox, 'ymax')
                        obj_bndbox_ymax.text = str(ymax)

                # save etree elementTree to file
                doc = etree.ElementTree(root)
                doc.write(open(Path(vocAnnotationFolder).joinpath(img_name).with_suffix('.xml'), 'wb'),
                          pretty_print=True)

                # save the img name to the train/val/trainval/test.txt
                if key == 'train':
                    ftrain.write(img_name[:-4] + '\n')
                    ftrainval.write(img_name[:-4] + '\n')
                elif key == 'val':
                    fval.write(img_name[:-4] + '\n')
                    ftrainval.write(img_name[:-4] + '\n')
                else:
                    ftest.write(img_name[:-4] + '\n')

        ftrain.close()
        ftrainval.close()
        fval.close()
        ftest.close()

    def toCOCO(self):
        """
        Main function to transform the Pegasus's files to coco format.
        Returns:

        """
        # init folders in COCO format
        annotationFolder = Path(self.outFolder).joinpath('annotations')

        annotationFolder.mkdir(parents=True, exist_ok=True)

        for key, value in self.jsonPaths.items():
            print('[*] start with %s' % key)

            if self.copyIMG:
                Path(self.outFolder).joinpath(key).mkdir(parents=True, exist_ok=True)

            with open(value, 'r') as f:
                jsonFile = json.load(fp=f)

            cocoJson = {}

            cocoJson['info'] = jsonFile['info']
            cocoJson['licenses'] = jsonFile['licenses']
            cocoJson['images'] = []

            for imgAnno in jsonFile['images']:
                tmp = {}
                tmp['filename'] = imgAnno['filename']
                tmp['height'] = imgAnno['height']
                tmp['width'] = imgAnno['width']
                tmp['id'] = imgAnno['id']
                tmp['date_captured'] = imgAnno['date']
                cocoJson['images'].append(tmp)

                # copy images to new folder
                if self.copyIMG:
                    shutil.copy(Path(self.imgFolder).joinpath(key, imgAnno['filename']),
                                Path(self.outFolder).joinpath(key, imgAnno['filename']))

            superCategory = {'Person': 'Person', 'Car': 'Vehicle', 'Bicycle': 'Vehicle', 'OtherVehicle': 'Vehicle',
                             'DontCare': 'DontCare'}
            cocoJson['categories'] = []

            for categoryAnno in jsonFile['categories']:
                tmp = {}
                tmp['supercategory'] = superCategory[categoryAnno['name']]
                tmp['id'] = categoryAnno['id']
                tmp['name'] = categoryAnno['name']
                cocoJson['categories'].append(tmp)

            cocoJson['annotation'] = []

            for anno in jsonFile['annotations']:
                tmp = {}
                xLeft, yLeft, w, h = self.obb2hbb(anno['bbox'], flag='coco')
                tmp['segmentation'] = [[xLeft, yLeft, xLeft + w, yLeft, xLeft + w, yLeft + h, xLeft, yLeft + h]]
                tmp['area'] = w * h
                tmp['image_id'] = anno['image_id']
                tmp['bbox'] = [xLeft, yLeft, w, h]
                tmp['category_id'] = anno['category_id']
                tmp['id'] = anno['id']
                cocoJson['annotation'].append(tmp)

            with open(annotationFolder.joinpath('instances_%s.json' % key), 'w') as f:
                json.dump(cocoJson, f)


if __name__ == '__main__':
    labelTransformer = LabelTransformer()
    labelTransformer.toVOC()
    # labelTransformer.toCOCO()
