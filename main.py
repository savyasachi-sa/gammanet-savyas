from experiment import Experiment
import sys


def run_experiment(experiment_name, instance_name):
    print("Running Experiment: {}, {}".format(experiment_name, instance_name))
    exp = Experiment(experiment_name, instance_name)
    exp.run()


if __name__ == "__main__":
    exp_name = 'default'
    instance_name = None

    if len(sys.argv) > 1:
        exp_name = sys.argv[1]

    if len(sys.argv) > 2:
        instance_name = sys.argv[2]

    run_experiment(exp_name, instance_name)
