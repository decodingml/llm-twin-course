from pandas import DataFrame
from qwak.model.tools import run_local

from finetuning import CopywriterMistralModel

if __name__ == '__main__':
    model = CopywriterMistralModel()
    input_vector = DataFrame(
        [{
            "instruction": "Write me a Linkedin post about Data Science"
        }]
    ).to_json()

    prediction = run_local(model, input_vector)
    print(prediction)
