# PegasusDrone

1. 数据转换代码（to coco/voc）-- 以后可能用于发布的

- 代码存储在 devtoolkit 中的 labelTransformer.py中
  - 通过首先创建一个 object：labelTransformer = LabelTransformer()
  - 该 object 需要四个 parameter 进行初始化：
    - rootFolder: 存放我们 Pegasus dataset 的根文件夹，绝对路径或相对路径，默认 '..'
    - outFolder: 放置转换后文件的根文件夹，绝对路径或相对路径，默认 'output'
    - outType: 选择哪种格式 voc 或者 coco，默认 voc
    - copyIMG: 是否从 Pegasus 文件夹中拷贝文件到 outFolder，默认 false

- 转换为 voc 格式：
  - 调用 labelTransformer.toVOC() 方法
- 转换为 coco 格式：
  - 调用 labelTransformer.toCOCO() 方法

- 转换后的文件夹为如下格式：
  - VOC 格式：
    - Annotations 文件夹：存放所有 xml 标注文件
    - ImagesSets 文件夹：
      - Main 文件夹：存放 train.txt/ val.txt/ trainval.txt/ test.txt 四个文件
    - JPEGImages 文件夹：存放图片
  - COCO 格式：
    - annotations 文件夹：存放 instances_test.json/ instances_train.json/ instances_val.json
    - train 文件夹：存放 train dataset 的图片
    - val 文件夹：存放 valid dataset 的图片
    - test 文件夹：存放 test dataset 的图片.

2. 可视化 -- 我们自己使用来验证的

- 通过 devtoolkit 文件夹中的 visulization.py 可视化生成的 voc 文件
  - 调用输入两个 parameter
    - root: 存放生成 voc 格式的 root 文件夹
    - path：xml 标注文件的路径

3. AP 计算 -- 后续可能发布的，半成品目前

- 文件为 AP.py
  - 可以计算 fp 和 tp
  - 不适用于计算 obb 

4. 所标注 XML 文件转换为 Pegasus dataset 格式

- 文件为 utils 文件夹中的 readXML.py

  - 共有 7 个 parameter 可供调试
    - dataset: 标注完的数据集的根文件夹
    - train_proportion: 训练集的比例
    - val_proportion: 验证集的比例
    - infoFolder: info 文件夹的位置
    - ouput: 转换后数据集的根目录
    - existedFile: 记录现有数据集的文件，保存有 train/val/test 数据集每个图片的名字，用于数据集的增量更新，以保证 V1 与 V2 训练集图片的一致性
    - bboxtype: 0 (obb) or 1(normal)

  - 使用时创建 JSONMaker 类
    - 调用 makeJSON() 方法制作 Pegasus 数据集
    - 调用 getJSONSTATE() 方法确定 图片数量和 bbox 数量
    - 调用 copyImgs() 复制图片到 Pegasus 数据集
    - 调用 showIMG() 方法 随机展示 obb 和 hbb 标注在图片上

5. 训练 YOLOv4

- 制作训练集
  - 训练集已经制作完，上传至网盘中的 `pegasus_yolo.7z`
- 将该文件解压后放置到跟 darknet 可执行文件同级
- cfg 和 data 文件已经调整完，可以直接训练：
  - 数据集共5类，共训练10000次，8000 与 9000 iteration 的时候会各自 lr 下降十倍
  - windows: `darknet.exe detector train pegasus/pegasus.data pegasus/pegasus.cfg pegasus/yolov4.conv.137 -map`
  - linux: `./darknet detector train pegasus/pegasus.data pegasus/pegasus.cfg pegasus/yolov4.conv.137 -map`

- 训练过程中使用 val dataset 进行 mAP 评价
- 训练完后将 
  - pegasus/pegasus.data 中的 `valid  = pegasus/val.txt` 注释
  - 取消 `# valid = pegasus/test.txt` 的注释
  - 运行`darknet.exe detector map pegasus/pegasus.data pegasus/pegasus.cfg backup/pegasus_best.weights` 计算最佳 weights 在 test dataset 上的 mAP
