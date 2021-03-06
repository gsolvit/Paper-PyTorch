import torch
import torch.nn as nn
import torch.nn.functional as F


class Generator(nn.Module):
    def __init__(self, channels=3):
        super(Generator, self).__init__()

        def conv(in_feat, out_feat, stride_, padding_, bn=True):
            layers = [nn.Conv2d(in_feat, out_feat, 4, stride=stride_, padding=padding_)]
            if bn:
                layers.append(nn.BatchNorm2d(out_feat, 0.8))
            layers.append(nn.LeakyReLU(0.2))
            return layers

        def uconv(in_feat, out_feat, stride_, padding_, bn=True):
            layers = [nn.ConvTranspose2d(in_feat, out_feat, 4, stride=stride_, padding=padding_)]
            if bn:
                layers.append(nn.BatchNorm2d(out_feat, 0.8))
            layers.append(nn.ReLU())
            return layers

        self.model = nn.Sequential(
            *conv(channels, 64, 2, 1, bn=False),
            *conv(64, 64, 2, 1),
            *conv(64, 128, 2, 1),
            *conv(128, 256, 2, 1),
            *conv(256, 512, 2, 1),
            *conv(512, 4000, 1, 0),  # mark
            *uconv(4000, 512, 1, 0),
            *uconv(512, 256, 2, 1),
            *uconv(256, 128, 2, 1),
            *uconv(128, 64, 2, 1),
            nn.ConvTranspose2d(64, channels, 4, 2, 1),  # mark
            nn.Tanh()
        )

    def forward(self, x):
        x = self.model(x)
        return x


class Discriminator(nn.Module):
    def __init__(self, channels=3):
        super(Discriminator, self).__init__()

        def discriminator_block(in_filters, out_filter, bn=True):
            layers = [nn.Conv2d(in_filters, out_filter, 4, 2, 1)]  # mark
            if bn:
                layers.append(nn.BatchNorm2d(out_filter, 0.8))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *discriminator_block(channels, 64, bn=False),
            *discriminator_block(64, 128),
            *discriminator_block(128, 256),
            *discriminator_block(256, 512),
            nn.Conv2d(512, 1, 4, 1, 0),
            nn.Sigmoid()
        )

    def forward(self, img):
        img = self.model(img)
        return img.view(-1, 1)

    # ------------------parallel computing------------------------------------------------
    # def forward(self, img):
    #     if isinstance(img.data, torch.cuda.FloatTensor) and self.ngpu > 1:
    #         img = nn.parallel.data_parallel(self.main, img, range(self.ngpu))
    #     else:
    #         img = self.main(img)
    #
    #     return img.view(-1, 1)
