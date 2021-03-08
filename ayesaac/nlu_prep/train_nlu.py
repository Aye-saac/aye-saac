from rasa.shared.nlu.training_data.loading import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config

# list of paths of training files
#data_path=[]

#data_path.append('data/nlu_textual_queries.md')
#data_path.append('data/nlu.md')

data_path = 'data/nlu_textual_queries.md'
# data_path = 'data/nlu.md'

#for i in range(len(data_path)):
training_data = load_data(data_path)
trainer = Trainer(config.load())
trainer.train(training_data)
directory = '../data/models/rasa/nlu'
trainer.persist(directory)
