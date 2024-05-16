"""Runs the Agent"""

from agent.app_agent import QuantaAgent
from agent.utils import Utils

# This is the original command line Quanta Agent that only reads prompts from 'question.txt',
# rather than the newer Streamlit app approach.

if __name__ == "__main__":
    agent = QuantaAgent()

    # Ask for the output file name. They can enter any filename they want. The result will be that after the tool
    # runs, the output will be in the data folder with the name they provided (both a question file and an answer file)
    output_file_name = input("Enter filename for output (without extension, or path): ")

    with Utils.open_file(f"{agent.cfg.data_folder}/question.txt") as file:
        prompt = file.read()
        agent.run(None, agent.cfg.update_strategy, output_file_name, None, prompt)
