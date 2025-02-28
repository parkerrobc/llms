### LLMs

This application works with AIs that follow the OpenAI API request/response paradigm. Simple application created for messing around with LLMs.

Built following the Udemy Course https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models along with custom touches and implementations. 

##### Environment

Project is set up to use Anaconda with an `environment.yml` file and PyInstaller to compile to an exe.

##### Set up

1. Install and activate conda environment
    ```
   conda env create --file environment.yml
   conda activate ai_llms
   ```
2. Create `.env` file with your OpenAIApiKey and place it into the `src` directory (you can set this in the `app.properties` file if you wish not to create this)
   ```
   OPEN_AI_KEY=<yourOpenAIApiKey>
   ```
3. Update `./src/app.properties`
   ```
   [DEFAULTS]
   tone=<thisIsTheDefaultSystemPromptUsedInRequestToLLM>
   request=<thisIsTheDefaultUserPromptUsedInRequestToLLM>

   [OPEN_AI]
   key=<yourOpenAIApiKeyIfYouWantToAddItHereInsteadOfCreatingEnvFile>

   [CUSTOM_AI]
   baseUrl=<urlToCustomLLMOrOtherLLMThatUsesTheOpenAIApiFormat>
   key=<keyForSaidLLM>
   ```
4. (Only for macOS at this time) If you wish to compile and install this to your `/usr/local/bin`, run the `macos_build_install.sh` script
   ```
   ./macos_build_install.sh
   ```

##### Options

```
usage: llms [options]

positional arguments:
  {createBrochure,simpleRequest}
                        Available commands
    createBrochure      create brochure using ai
    simpleRequest       makes simple request to llm

options:
  -h, --help            show this help message and exit
  -c, --custom, --no-custom
                        connects to llm with [CUSTOM_AI] properties, [OPEN_AI] is default
  -m MODEL, --model MODEL
                        language model to use. ex: -m llama3.2
  -rcl [REQUESTCHARLIMIT], --requestCharLimit [REQUESTCHARLIMIT]
                        limits the request size to the llm: default is 5000
  -t [TONE], --tone [TONE]
                        tone that the llm should respond with
```

##### Example Usage:

Python:
```
cd ./src
python llms.py -c -m llama3.2 -t 'Respond as an arrogant, pious individual injecting your beliefs into any and all response details.' createBrochure --url https://linkedin.com
```

Installed on macOS:
```
llms -c -m llama3.2 -t 'Respond as an arrogant, pious individual injecting your beliefs into any and all response details.' createBrochure --url https://linkedin.com
```

### Feedback

Feedback is appreciated and welcomed. Updates will come as they come
