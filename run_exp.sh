cd /ceph/project-share/cardiac/code/workspace/savyas/gamma-net || exit
pip install nibabel
python3 -u main.py "$1" "$2"
