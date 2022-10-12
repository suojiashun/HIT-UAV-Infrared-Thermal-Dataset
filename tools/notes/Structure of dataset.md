# Structure of dataset

## Pegasus dataset

Pegasus_Root

- devtoolkit

- dataset

  - images

    - train
      - 1_60_30_0_00000.jpg

    - val

    - test

  - annotations

    - train.json

    - val.json

    - test.json



oriented bbox: [xc, yc, w, h, angle]

## VOC format

voc_root

- Annotations

  - 1_60_30_0_00000.xml

- JPEGImages

  - 1_60_30_0_00000.jpg

- ImageSets

  - Main

    - train.txt, the name of file, i.e. 1_60_30_0_00000

    - trainval.txt

    - val.txt

    - test.txt



horizontal bbox: [xmin, ymin, xmax, ymax]

## COCO format

COCO_ROOT

- annotations
  -  instances_train.json
  - instances_val.json
  - instances_test.json
- train
  - 1_60_30_0_00000.jpg
- val
  - 1_60_30_0_00000.jpg
- test
  - 1_60_30_0_00000.jpg



horizontal bbox: [xmin, ymin, w, h]

