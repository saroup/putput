# Generating NLU Model Tests

```putput``` can be used to quickly and effortlessly generate thousands of tests for [LUIS](www.luis.ai) or other NLU models.
This allows you to immediately find weak points in your model to fix.

This is an example to generate tests for a HR bot trained on [LUIS](www.luis.ai).

## Instructions

1. Create a LUIS account at luis.ai
2. Follow these [instructions](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-batch-testing#import-example-app) on how to import the example HR app
3. Run ```python -m samples.luis_test``` to generate [HumanResources-jobs-batch.json](HumanResources-jobs-batch.json)
4. Follow these [instructions](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-batch-testing#run-the-batch-with-entities) on how to upload the batch test file to LUIS and run it.
5. Review the test results: [instructions](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-batch-testing#review-entity-batch-results)

Make sure to checkout the [patterns.yml](patterns.yml) file that was used and also checkout [\_\_main\_\_.py](__main__.py) for usage.

## Example Generated Tests

```JSON
{
        "text": "my resume to the SQL database engineer is here",
        "intent": "ApplyForJob",
        "entities": [
            {
                "entity": "Job",
                "startPos": 17,
                "endPos": 38
            }
        ]
    },
    {
        "text": "are there any backend development jobs open ?",
        "intent": "GetJobInformation",
        "entities": []
    },
    {
        "text": "are there any currently open janitorial jobs ?",
        "intent": "GetJobInformation",
        "entities": []
    },

```
