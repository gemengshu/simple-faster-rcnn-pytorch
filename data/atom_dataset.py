import numpy as np
import os
import torch
from torch.utils.data import Dataset

from .util import read_image


class AtomDataset(Dataset):
    def __init__(self, data_root, split='train', *args, **kwargs):
        self.data_root = data_root
        self.im_root = os.path.join(self.data_root, 'image')
        self.position_root = os.path.join(self.data_root, 'position')
        self.radius_root = os.path.join(self.data_root, 'radius')

        self.image_names = os.listdir(self.im_root)
        if split == 'train':
            self.image_names = self.image_names[0:-1000]
        elif split == 'test':
            self.image_names = self.image_names[-1000:]

        self.label_names = ('c',)

    def circles_to_bboxes(self, centers, radius):
        centers = np.asarray(centers, dtype=np.float)
        bboxes = np.concatenate((centers - radius, centers + radius), axis=-1)
        return bboxes

    def get_example(self, i):
        name = os.path.splitext(self.image_names[i])[0]
        im_fn = os.path.join(self.im_root, self.image_names[i])
        pos_fn = os.path.join(self.position_root, '{}.txt'.format(name))
        rad_fn = os.path.join(self.radius_root, '{}.txt'.format(name))

        image = read_image(im_fn, color=True)

        positions = []

        with open(pos_fn, 'r') as f:
            for line in f.readlines():
                try:
                    cy, cx = [float(v) for v in line.strip().split(' ') if len(v) > 0]

                    positions.append((cy, cx))
                except:
                    print(pos_fn)
                    print(line, len(line))
                    assert False

        with open(rad_fn, 'r') as f:
            radius = float(f.readline().strip())

        bboxes = self.circles_to_bboxes(positions, radius).astype(np.float32)
        labels = np.zeros(len(bboxes), dtype=np.int32)
        difficult = np.zeros(len(bboxes), dtype=np.uint8)

        return image, bboxes, labels, difficult

    def __len__(self):
        return len(self.image_names)

    __getitem__ = get_example
