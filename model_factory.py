from unet import UNet
from gammanet import get_model as get_gammanet


def get_model(config):
    if config['model']['type'] == 'UNet':
        return UNet(n_classes=1, padding=True, batch_norm=True, up_mode='upsample', wf=config['model']['wf'])
    elif config['model']['type'] == 'GammaNet':
        return get_gammanet(config)
    else:
        raise Exception('Invalid Model Type')
