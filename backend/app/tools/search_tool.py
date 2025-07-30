# app/tools/search_tool.py
from crewai_tools import SerperDevTool

# Initialize the tool. It will automatically use the SERPER_API_KEY
# from the environment variables we set up in the config.
search_tool = SerperDevTool()
