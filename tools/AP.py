import json
import os
import numpy as np
from tqdm import tqdm

class Evaluator():
    '''
    calculate mAP, Precision, Recall from result file
    '''
    def __init__(self, detPath, annoPath, category, cachePath, iouThresh=0.5):
        self.detPath = detPath
        self.annoPath = annoPath
        self.cachePath = cachePath
        self.category = category
        self.iouThresh = iouThresh

    def getGT(self):
        """
        return the dict of {imgname: bbox, ...}
        """
        if os.path.isfile(self.cachePath) and os.path.exists(self.cachePath):
            with open(self.cachePath, 'r', encoding='utf-8') as f:
                whole_gt = json.load(f)

        else:
            with open(self.annoPath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            annotations = data['annotations']

            # save the gt bbox in id
            whole_gt = {}

            totalCategories = 5   # the total classes
            for category in range(totalCategories):
                whole_gt['%d' % category] = {}

            for annotation in annotations:
                numBBOX = len(annotation['bbox']) * [False]
                if ('%d' % annotation['image_id']) not in whole_gt['%d' % annotation['category_id']]:
                    whole_gt['%d' % annotation['category_id']]['%d' % annotation['image_id']] = []
                    whole_gt['%d' % annotation['category_id']]['%d' % annotation['image_id']].append({'bbox': annotation['bbox'],'difficult': annotation['difficult'],'detected': numBBOX})
                else:
                    whole_gt['%d' % annotation['category_id']]['%d' % annotation['image_id']].append({'bbox': annotation['bbox'],'difficult': annotation['difficult'],'detected': numBBOX})
            with open('sorted_gt', 'w', encoding='utf-8') as f:
                json.dump(whole_gt, f)

        self.gt = whole_gt[self.category]

    def getDet(self):
        with open(self.detPath, 'r', encoding='utf-8') as f:
            result = json.load(f)['result']

        dets = []
        for det in result:
            if det['category_id'] == self.category:
                dets.append(det)
        # sort keys of the detections with score, from high to low
        dets.sort(key=lambda k:(k.get('score'), 0), reverse=True)
        self.dets = dets

    def getPR(self):
        numDets = len(self.dets)

        tp = np.zeros(numDets, dtype=np.int)
        fp = np.zeros(numDets, dtype=np.int)

        for idx, det in enumerate(tqdm(self.dets)):
            imgID = det['image_id']

            # get detection
            detBBOX = np.array(det['bbox'])
            detBBOX[2] += detBBOX[0]
            detBBOX[3] += detBBOX[1]

            # get gt bboxes of a picture
            gtBBOX = None
            gts = self.gt['%d' % imgID]
            for gt in gts:
                if gtBBOX is None:
                    gtBBOX = np.array(gt['bbox']).reshape((-1, 4))
                else:
                    gtBBOX = np.vstack(gtBBOX, np.array(gt['bbox']).reshape((-1, 4)))

            gtBBOX[:, 2] += gtBBOX[:, 0]
            gtBBOX[:, 3] += gtBBOX[:, 1]

            # save the maximum iou between detection and gt bboxes
            ioumax = -np.inf

            if gtBBOX.size() > 0:
                ixmin = np.maximum(gtBBOX[:, 0], detBBOX[0])
                iymin = np.maximum(gtBBOX[:, 1], detBBOX[1])
                ixmax = np.minimum(gtBBOX[:, 2], detBBOX[2])
                iymax = np.minimum(gtBBOX[:, 3], detBBOX[3])
                iw = np.maximum(ixmax - ixmin + 1., 0.)
                ih = np.maximum(iymax - iymin + 1., 0.)
                intersection = iw * ih

                # union
                uni = ((detBBOX[2] - detBBOX[0] + 1.) * (detBBOX[3] - detBBOX[1] + 1.) +
                       (gtBBOX[:, 2] - gtBBOX[:, 0] + 1.) * (gtBBOX[:, 3] - gtBBOX[:, 1] + 1.) - intersection)

                overlaps = intersection / uni
                ioumax = np.max(overlaps)

                # get index of the bbox with max IoU
                jmax = np.argmax(overlaps)

                # calculate tp and fp
                if ioumax > self.iouThresh:
                    if not self.gt[imgID][jmax]['difficult']:
                        # if the gt was already detected, avoid the redundant detection
                        if not self.gt[imgID][jmax]['detected']:
                            tp[idx] = 1.
                            self.gt[imgID][jmax]['detected'] = 1  # mark the gt bbox as detected
                        else:
                            fp[idx] = 1.
                else:
                    fp[idx] = 1.
                print("**************")

        # compute True/False positive
        fp = np.cumsum(fp)
        tp = np.cumsum(tp)

        # recall = tp / float(npos)

        # avoid divide by zero in case the first detection matches a difficult
        # ground truth
        # np.finfo(np.float64).eps 
        precision = tp / np.maximum(tp + fp, np.finfo(np.float64).eps)

        # ap = voc_ap(rec, prec, use_07_metric)
        
        print(precision[-1])








