from rasa.nlu.training_data import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config

training_data = load_data('data/nlu.md')
trainer = Trainer(config.load())
trainer.train(training_data)

directory = '../data/models/rasa/nlu'
trainer.persist(directory)
