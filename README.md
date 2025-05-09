# Traveller_health_guide

## A contributor forks your repository.

They clone their fork locally, make changes, then push to their fork.

They go to your repo and submit a Pull Request (PR).
## Getting started

You have a few options for getting started with this repository.
The quickest way to get started is GitHub Codespaces, since it will setup all the tools for you, but you can also [set it up locally](#local-environment).

### GitHub Codespaces

You can run this repository virtually by using GitHub Codespaces. The button will open a web-based VS Code instance in your browser:

1. Open the repository (this may take several minutes):

    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/python-ai-agents-demos)

2. Open a terminal window
3. Continue with the steps to run the examples

   ### Local environment

1. Make sure the following tools are installed:

    * [Python 3.9+](https://www.python.org/downloads/)
    * Git

2. Clone the repository:

    ```shell
    git clone https://github.com/Azure-Samples/python-ai-agents-demos.git
    cd python-ai-agents-demos
    ```

3. Set up a virtual environment:

    ```shell
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. Install the requirements:

    ```shell
    pip install -r requirements.txt
    ```
5. To Run Chainlit
   chainlit run repo/path -w

## Running the Python examples

1. Configure your environment variables by copying the `.env.example` to `.env` and updating the values:

    ```shell
    cp .env.example .env
    ```

2. Edit the `.env` file with your API keys and configuration settings.

