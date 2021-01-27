# NLU Preparation

## Train model for further use

### Dependencies

Run the following commands after meeting main project dependencies

- [Rasa](https://rasa.com/docs/rasa/user-guide/installation/)

```
pip3 install --upgrade rasa
```

### Before running

Fill the nlu.md file in the data directory which is the file that contains the training data (See https://rasa.com/docs/rasa/nlu/training-data-format/ for more information on how to format this file).

Don't forget to fill the "entries" directory with every entry file you would need. For example: the lookup files.

### Usage

python3 train_nlu.py

## Using trained model in Aye-Saac

Move your newly trained model in `../data/models/rasa/nlu/` to `../../data/rasa/nlu/`
