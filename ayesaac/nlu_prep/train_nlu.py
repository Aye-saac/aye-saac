from rasa.shared.nlu.training_data.loading import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config

# data_path = 'data/nlu_textual_queries.md'
data_path = 'data/nlu.md'

training_data = load_data(data_path)
trainer = Trainer(config.load())
trainer.train(training_data)

directory = '../data/models/rasa/nlu'
trainer.persist(directory)
