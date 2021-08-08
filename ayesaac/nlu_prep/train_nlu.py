from rasa.shared.nlu.training_data.loading import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config

data_path = 'data/nlu_combi.md'
data_path = 'data/nlu_textual_queries.md'

training_data = load_data(data_path)
trainer = Trainer(config.load())
trainer.train(training_data)
directory = '../data/models/rasa/nlu'
trainer.persist(directory)

from pathlib import Path
import datetime as dt
from distutils.dir_util import copy_tree
import os

src = '../data/models/rasa/nlu'
dst = '../../data/rasa/nlu'
i = input("Copy latest model from {src} into {dst} ? (Y/n)\n".format(src=src,dst=dst))

latest_modif_time = dt.datetime(1970,1,1)
latest_modif_path = None

if i == 'Y':
    for path in Path(src).iterdir():
        mtime = dt.datetime.fromtimestamp(path.stat().st_mtime)
        if not ".DS_Store" in str(path) and mtime > latest_modif_time:
            latest_modif_time = mtime
            latest_modif_path = path

    if not latest_modif_path == None:
        (head, tail) = os.path.split(latest_modif_path)

        src += "/" + tail
        dst += "/" + tail

        print("Copying model {src} into {dst}...".format(src=src, dst=dst))
        copy_tree(src,dst)
        print("Successfully copied model")
