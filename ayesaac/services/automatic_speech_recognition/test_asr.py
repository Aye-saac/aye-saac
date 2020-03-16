import unittest
from ayesaac.services.automatic_speech_recognition import main as asr


class MyTestCase(unittest.TestCase):
    def test_asr(self):
        # create fake 'data' dict
        data = {"path_done": []}

        # run asr on file
        data = asr.callback_impl(data, asr.Level.FULL_TEST)

        # a query should have been added
        assert('query' in data)


if __name__ == '__main__':
    unittest.main()
