### LLMs

This application works with AIs that follow the OpenAI API, Anthropic API, or Google request/response paradigms. Simple application created for messing around with LLMs.

Built following the Udemy Course https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models along with custom touches and implementations.

##### Environment

Project is set up to use PyEnv with a `requirements.txt` file and PyInstaller to compile to an exe.
Docker is used to create a postgres database used to store vectors (this is not compiled into the exe, this is standalone such that you can connect to any other postgres vector store/db)
Required LongChain API Key if using `kbase.type == 'vector'`



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
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/postgres
   LANGSMITH_API_KEY=<yourLongchainApiKey>
   CO_API_KEY=<yourCohereApiKey>>

   OPEN_AI_KEY=<yourOpenAIApiKey>
   ANTHROPIC_API_KEY=<yourAnthropicApiKey>
   GOOGLE_API_KEY=<yourGoogleApiKey>
   
   LANGSMITH_TRACING_V2=true
   LANGSMITH_PROJECT=llms
   ```
3. Update `./src/app.json` with default configuration
   ```json
   {
     "kbase": {
       "name": "some_kbase_name",
       "location": "'some location on your file system",
       "type": "vector",
       "connectionStr": "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres",
       "topN": 3,
       "embedModel": "text-embedding-3-small",
       "reRankModel": "rerank-multilingual-v3.0",
       "tableName": "some_name",
       "metadataColumns": ["document_id", "category", "source"],
       "metadataJsonColumn": "metadata"
     }
     ,
     "aiConfig": {
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
  {createBrochure,simpleRequest,makeJoke,battle,addConfig,listConfig,interactive,chatBot}
                        Available commands
    createBrochure      create brochure using ai
    simpleRequest       makes simple request to llm
    makeJoke            makes joke using ai
    battle              battle between different llms
    addConfig           add config to llm
    listConfig          list llms configurations
    interactive         use gradio to create interactive UI
    chatBot             use gradio to create interactive chat bot

options:
  -h, --help            show this help message and exit
  -p, --provider [{-,anthropic,openai,google-open,google}]
                        provider to use.
  -t [TONE], --tone [TONE]
                        tone that the llm should respond with
```

##### Configurations

You can now create different provider configuration json files and add them to your application directory `PROFILE_DIR = Path.home() / '.llms'`.

The files should be named `<yourProvider>.json`. The `<yourProvider>` will be what you will pass to the `-p` option when running.

Support kbase types:
   * `directory`
   * `vector`

Supported libraries:
   * `openai`
   * `google`
   * `anthropic`

Your custom json files must match this format:

```json
{
  "kbase": {
    "name": "some_kbase_name",
    "location": "'some location on your file system",
    "type": "vector", // kbase type you want to use
    "connectionStr": "postgresql+asyncpg://postgres:postgres@postgres:5432/postgres",
    "topN": 3,
    "embedModel": "text-embedding-3-small",
    "reRankModel": "rerank-multilingual-v3.0",
    "tableName": "some_name",
    "metadataColumns": ["document_id", "category", "source"],
    "metadataJsonColumn": "metadata"
  },
  "aiConfig": {
    "tone": "As a casual, laid-back fellow, answer any inquiry with whit and an aura of charm.", // This is the system prompt passed to the LLM
    "request": "Tell me about yourself.", // Default request to the LLM if you don't pass a request
    "model": "llama3.2", // model you want to use
    "library": "openai", // AI library you want to use
    "baseUrl": "http://localhost:11434/v1", // URL used to access LLM (this can be blank)
    "key": "ollama", // This is the key used to call the API
    "requestCharLimit": 5000, 
    "maxTokens": 200,
    "temperature": 0.7
  }
}
```

Adding file:

```bash
llms addConfig -f yourProvider.json
```

##### Postgres Setup:
Must have Docker installed on your machine.

```bash
# to start
docker-compose up postgres

#to stop
docker-compose down postgres
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
