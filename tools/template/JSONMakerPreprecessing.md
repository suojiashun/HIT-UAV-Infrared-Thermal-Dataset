## data folder

储存各个文件的路径

- ~~"video.txt"，储存各个视频文件夹的路径，文件夹中为对应图片（重命名后，从0开始命名，前面补零格式化）。~~
- "info.txt"，储存数据集的基本信息。
- "license.txt"，储存数据集licenses信息。
- "scenario.txt"，储存数据集scenario信息。
- "weather.txt"，储存数据集weather信息。
- "category.txt"，储存数据集种类信息。
- 图片信息按照图片命名读取。见最下方图片命名。

## ~~video.txt~~

~~按行储存每个视频文件夹的信息，每列为具体信息。以逗号分割。~~

| ~~FolderPath~~ | ~~Width~~   | ~~Height~~  | ~~Scenario~~            | ~~Weather~~            | ~~Perspective~~        | ~~Altitude~~ | ~~Date~~      |
| -------------- | ----------- | ----------- | ----------------------- | ---------------------- | ---------------------- | ------------ | ------------- |
| ~~str~~        | ~~int[px]~~ | ~~int[px]~~ | ~~int[scenario index]~~ | ~~int[weather index]~~ | ~~int angle [degree]~~ | ~~int[m]~~   | ~~data,time~~ |

## info.txt

按行储存具体信息。

| information  | type |
| ------------ | ---- |
| year         | int  |
| version      | int  |
| description  | str  |
| contributor  | str  |
| url          | str  |
| data_created | str  |

## license.txt

按行储存具体信息。以冒号分割。

| information | type |
| ----------- | ---- |
| url         | str  |
| name        | str  |

## scenario.txt

按行储存信息

| information[str] |
| ---------------- |
| Day              |
| Night            |

## weather.txt

按行存储信息，**保留项**。

| information[str] |
| ---------------- |
| Sunny            |
| Rainy            |

## category.txt

按行存储信息。

| information[str] |
| ---------------- |
| Person           |
| Car              |
| Bicycle          |
| OtherVehicle     |
| DontCare         |

## 图片命名

Template: **1_60_30_0_00000.jpg**。若保存日期，在角度文件夹下建立子文件夹，文件格式为20201222，然后讲相应文件放入子文件夹中。日期为可选择项。

|      | Scenario(Day/Night) |    Altitude[m]     |  Perspective[°]   |    Weather(TBD)    |  ID  | Extention |
| :--: | :-----------------: | :----------------: | :---------------: | :----------------: | :--: | :-------: |
| Info |   Day:0, Night:1    | range(60, 130, 10) | range(30, 90, 10) | Sunny: 0, Rainy: 1 | %05d |   .jpg    |
| Type |         int         |        int         |        int        |        int         | int  |           |

