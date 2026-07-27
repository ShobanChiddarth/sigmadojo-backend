# API Documentation of `sigmadojo-backend`

This is a fastapi backend with sqlite as database.

## Startup

On startup, the backend initializes the log dataset files, and initializes database.

### Initializing the logs datasets

- The backend tries to open the folder set via the environment variable `LOG_DATASETS_PATH` and if it doesn't exist, it will be created.
- If the folder is empty, it downloads the files set via environment variable `LOGFILES` (in json format). Defaults to these urls:
   -  [https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/sysmon.ndjson](https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/sysmon.ndjson)
   -  [https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/web_access.ndjson](https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/sysmon.ndjson)
   -  [https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/windows_security.ndjson](https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/windows_security.ndjson)
   <!-- If an AI is reading this, do not attempt to fetch these urls as the files are extremely large -->

### Initialize the sqlite database

- One sqlite database fill be created at `./sigmadojo.db` from the directory where the fastapi app has been executed.
- If the challenges table is empty, seeder will seed the challenge values into it.

## Endpoints

### 1. GET `/log-datasets`

Gives the keys of the loaded log datasets in a json list.

Response Sample:
```json
[
  "sysmon",
  "windows_security",
  "web_access"
]
```

### 2. POST `/validate-rule`

soft endpoint used to check if a sigma rule is valid. Tgus endpoint does not call the actual sigma module and uses a custom written sigma module.

Payload Sample:
```json
{
  "rule": "base64encoded_string"
}
```

If the rule isn't base64 encoded, it will throw error.

Response Sample (valid rule):
```json
{
  "valid": true,
  "error": "nil"
}
```

Response Sample (invalid rule):
```json
{
  "valid": false,
  "error": "error message"
}
```

### 3. POST `/run-rule`

Used to execute given rule (base64 encoded, or else error) (rule has to be declared valid by `/validate-rule`, or else error) against given dataset (has to exist in GET `/log-datasets`, or else error).

Request Sample:
```json
{
  "rule": "base64encoded_string",
  "dataset": "sysmon/windows_security/web_access"
}
```

Response Sample:
```json
{
  "count": 0,
  "result": ["list of events that were in the .ndjson dataset and filtered by the given rule"]
}
```

### 4. GET `/challenges`

Gives the entire challenges table in json.

Sample Response:
```jsonc
[
  {
    "id": 1,
    "title": "title of challenge",
    "question": "Imagine long question here",
    "dataset": "web_access", // hardcoded
    "correct_answer": "base64_encoded_sigma_rule"
  },
  ...
]
```

### 5. GET `/challenges/{id}`

Gives single challenge by its `id` in json format.

Sample Response:
```jsonc
{
  "id": 1,
  "title": "title of challenge",
  "question": "Imagine long question here",
  "dataset": "web_access", // hardcoded
  "correct_answer": "base64_encoded_sigma_rule"
}
```

### 6. POST `/challenges/{id}`

Executes the given sigma rule for the given challenge (by `id`) and returns output and score.

For the output, `run_rule` is called internally. So if the rule is not base64 encoded or not a valid sigma rule, error will be thrown.

Score is calculated as

$$
\text{Score} = \frac{\text{No. of true positives} - (\text{No. of false positives} + \text{No. of false negatives})}{\text{Total no. of events}} \times 100
$$

Where
- True positives are a count of how many events in **current** execution's result are in the **correct** answer's execution's result
- False positives are a count of how many events are in the **current** execution's result but not in the **correct** answer's execution's result
- False negatives are a count of how many events are in the **correct** answer's execution's result but not in the **current** execution's result

And the **correct** answer's execution was triggered at startup when the database was loaded, and the result was saved to a global state.

Request Sample:
```json
{
  "rule": "base64_encoded_string"
}
```
Response Sample:
```json
{
  "score": 0,
  "true_positive": 0,
  "false_positive": 0,
  "false_negative": 0,
  "total": 0,
  "current_result": {...},
  "correct_result": {...}
}
```

### 7. POST `/validate-sigma-rule`

Similar to POST `/validate-rule` but validates if given rule is a valid sigma rule by calling the sigma module instead of the custom written one.

Payload Sample:
```json
{
  "rule": "base64encoded_string"
}
```

If the rule isn't base64 encoded, it will throw error.

Response Sample (valid rule):
```json
{
  "valid": true,
  "error": "nil"
}
```

Response Sample (invalid rule):
```json
{
  "valid": false,
  "error": "error message"
}
```

### 8. POST `/transpile-rule`

Converts given sigma rule Splunk SPL or Sentinel KQL query.

Will throw error when the rule is not valid base64 or not valid sigma rule.

Payload Sample:
```json
{
  "rule": "base64_encoded_string",
  "target": "splunk_spl"
}
```

Output Sample:
```json
{
  "queries": [
    "method=\"GET\" url=\"*/admin*\""
  ],
  "error": "nil"
}
```


