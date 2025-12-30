### LLMs

This application works with AIs that follow the OpenAI API, Anthropic API, or Google request/response paradigms. Simple application created for messing around with LLMs.

Built following the Udemy Course https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models along with custom touches and implementations. 

##### Environment

Project is set up to use PyEnv with a `requirements.txt` file and PyInstaller to compile to an exe.

##### Set up

1. Install and activate pyenv environment
    ```bash
   pyenv local 3.13.11
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. Create `.env` file with your OpenAIApiKey and place it into the `src` directory (you can set this in the `app.json` file if you wish not to create this or in a custom `<yourProvider>.json` file: see below)
   ```text
   OPEN_AI_KEY=<yourOpenAIApiKey>
   ANTHROPIC_API_KEY=<yourAnthropicApiKey>
   GOOGLE_API_KEY=<yourGoogleApiKey>
   ```
3. Update `./src/app.json` with default configuration
   ```json
   {
     "tone": "As a casual, laid-back fellow, answer any inquiry with whit and an aura of charm.",
     "request": "Tell me about yourself.",
     "model": "llama3.2",
     "library": "openai",
     "baseUrl": "http://localhost:11434/v1",
     "key": "ollama",
     "requestCharLimit": 5000,
     "maxTokens": 200,
     "temperature": 0.7
   }
   ```
4. (Only for macOS at this time) If you wish to compile and install this to your `/usr/local/bin`, run the `macos_build_install.sh` script
   ```bash
   ./macos_build_install.sh
   ```

##### Options
```
usage: llms [options]

positional arguments:
  {createBrochure,simpleRequest,makeJoke,battle,addConfig,listConfig}
                        Available commands
    createBrochure      create brochure using ai
    simpleRequest       makes simple request to llm
    makeJoke            makes joke using ai
    battle              battle between different llms
    addConfig           add config to llm
    listConfig          list llms configurations

options:
  -h, --help            show this help message and exit
  -p [{-,anthropic,openai,google-open,google}], --provider [{-,anthropic,openai,google-open,google}]
                        provider to use.
  -t [TONE], --tone [TONE]
                        tone that the llm should respond with
```

##### Configurations

You can now create different provider configuration json files and add them to your application directory `PROFILE_DIR = Path.home() / '.llms'`.

The files should be named `<yourProvider>.json`. The `<yourProvider>` will be what you will pass to the `-p` option when running.

Supported libraries:
   * `openai`
   * `google`
   * `anthropic`

Your custom json files must match this format:

```json
{
   "tone": "As a casual, laid-back fellow, answer any inquiry with whit and an aura of charm.", // default tone that the llm should respond with
   "request": "Tell me about yourself.", // default request
   "model": "llama3.2", // this will be the model used with the openai library
   "library": "openai", // see from list of libraries above
   "baseUrl": "http://localhost:11434/v1", // you can leave this blank if you wish to call out to OpenAI directly
   "key": "ollama", // this would be your api_key that initializes the openai library
   "requestCharLimit": 5000, // this limits the size of each request to the llm to reduce cost. detault in the code is 100000
   "maxTokens": 200,
   "temperature": 0.7
}
```

Adding file:

```bash
llms addConfig -f yourProvider.json
```

##### Example Usage:

Python:
```bash
cd ./src
python llms.py -p yourProvider -t 'Respond as an arrogant, pious individual injecting your beliefs into any and all response details.' createBrochure https://linkedin.com
```

Installed on macOS:
```bash
llms -p yourProvider -t 'Respond as an arrogant, pious individual injecting your beliefs into any and all response details.' createBrochure https://linkedin.com
```

### Feedback

Feedback is appreciated and welcomed. Updates will come as they come
