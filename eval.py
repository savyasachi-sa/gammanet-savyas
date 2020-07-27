from experiment import Experiment
import numpy as np
from file_utils import *


def get_pretty_string(exp, data):
    a = ['current', 'best_loss', 'best_dice']
    dices = [data[i][1] for i in a]
    best = np.argmax(dices)
    str = " {} : {:.2f} ({:.2f}, {:.2f})".format(exp, 100 * data[a[best]][1], 100 * data[a[best]][2],
                                                 100 * data[a[best]][3])
    return str


if __name__ == "__main__":
    exps = {
        "batch_4": ["batch_4", "batch_4-2", "batch_4-3", "batch_4-4", "batch_4-5"],
        "batch_8": ["batch_8", "batch_8-run-2", "batch_8-3", "batch_8-4", "batch_8-5"],
        "5e-4_full": ["5e-4-1", "5e-4-2", "5e-4-3", "5e-4-4", "5e-4-5"],
        "unet_lite_1e-4": ["unet-1e-4-1", "unet-1e-4-2", "unet-1e-4-3", "unet-1e-4-4", "unet-1e-4-5"],
        "unet_lite_5e-4": ["unet_lite_0.4_5e-4-1", "unet_lite_0.4_5e-4-2", "unet_lite_0.4_5e-4-3",
                           "unet_lite_0.4_5e-4-4"]

    }
    results = {}

    for exp in exps:
        for i in exps[exp]:
            print(exp, i)
            e = Experiment(exp, i)
            r = e.get_perf_stats()
            results[i] = r
            write_to_file_in_dir('../experiment_data', 'results8.json', results)
            log_to_file_in_dir('../experiment_data', 'results8-pretty.log', get_pretty_string(i, r))

    print("Finished")
