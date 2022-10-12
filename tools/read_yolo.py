import numpy as np

with open('d:/result100.txt') as f:
    data = f.readlines()

frames = []
block = []

for line in data:
    if 'Objects' in line:
        block = []
        continue
    if line == '\n':
        continue
    if 'FPS' in line:
        frames.append(block)
        continue
    block.append(line)

# save the width and height
confidence = 0
i = 0

labels = None
for frame in frames:
    for line in frame:
        label = np.zeros((1, 2), dtype='int')
        if 'car' in line:
            if ',' in line:
                line = line.split(',')[1]
            line = line.split()

            i += 1
            confidence = confidence + int(line[1][:-1])

            if int(line[1][:-1]) > 50:
                label[0, 0] = int(line[7])
                label[0, 1] = int(line[9][:-1])

                if labels is None:
                    labels = label
                else:
                    labels = np.concatenate((labels, label), axis=0)

confidence /= i
print('confidence: %d' % confidence)

width, height = np.mean(labels, axis=0)
maxWidth = np.max(labels[:, 0])
maxHeight = np.max(labels[:, 1])
print(width, height)
print(maxWidth, maxHeight)

# w > h
whlabels = labels[labels[:, 0] > labels[:, 1]]
# h >= w
hwlabels = labels[labels[:, 0] <= labels[:, 1]]

wh_w, wh_h = np.mean(whlabels,axis=0)
wh_maxWidth = np.max(whlabels[:, 0])
wh_maxHeight = np.max(whlabels[:, 1])
print(wh_w, wh_h)
print(wh_maxWidth, wh_maxHeight)

hw_w, hw_h = np.mean(hwlabels,axis=0)
hw_maxWidth = np.max(hwlabels[:, 0])
hw_maxHeight = np.max(hwlabels[:, 1])
print(hw_w, hw_h)
print(hw_maxWidth, hw_maxHeight)
