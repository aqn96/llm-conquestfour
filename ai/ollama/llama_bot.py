#https://github.com/ollama/ollama/blob/main/README.md
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

from ai.ollama.personality import personality_dict as p_dict
from ai.ollama.personality import occupation_dict as o_dict
from ai.ollama.personality import setting_dict as s_dict


class LLMBot:

    def __init__(self, model_name:str, name: str, opponent_name: str,*, game_name:str="connect four", personality_key:str ="", occupation_key:str="", setting_key:str="", history:str=""):
        """
        Constructor for the LLMBot
        :param model_name: name of the ollama model to use. model must be installed locally
        :param name: name to call the bot by
        :param opponent_name: name of the person playing against the bot
        :param game_name: name of the game being played
        :param personality_key: type of personality.
        :param occupation_key: type of occupation the bot has.
        :param setting_key: the environment / setting that the player and bot occupy
        :param history: (Optional) include a text history for reference
        """
        self.__last_user_text = ""
        self.__last_bot_text = ""
        self.__last_event = ""
        self.__game_setup = ""
        self.__template = ""
        self.__name = name
        self.__game_name = game_name
        self.__chat_history = history
        self.__opponent_name = opponent_name
        self.__personality = personality_key
        self.__occupation = occupation_key
        self.__setting = setting_key
        self.__model_name = model_name

        self.__model = self.__initialize_model(self.__model_name) # Initialize the model
        self.__initialize_template()    #Initialize template that model will use to interpret text
        self.__chain = self.__get_prompt() | self.__model #chain model and template together


    def __initialize_model(self, model_name):
        """
        Initialize and return a model object
        :param model_name: specify which Ollama model to load as String
        :return: model object
        """
        return OllamaLLM(model=model_name)
    
    def __initialize_template(self):
        self.set_template(
            personality_key = self.__personality, 
            occupation_key = self.__occupation,
            setting_key = self.__setting
        )
    
    def __get_prompt(self):
        return ChatPromptTemplate.from_template(self.__template)
    
    def set_template(self, *,setting_key="", personality_key="", occupation_key=""):
        self.__template = """
        Your name is {bot_name}. Your opponent is {username}.
        You are both playing a game of {game}.
        """
        self.__template += s_dict.get(setting_key, "This describes the setting: " + setting_key) + "\n"
        self.__template += o_dict.get(occupation_key, "This describes your occupation: " + occupation_key) + "\n"
        self.__template += p_dict.get(personality_key, "This describes your personality: " + personality_key) + "\n"
        self.__template += "Respond to the player. Only generate your words or actions. Do not generate label text such as '{bot_name}: ' or '{username}: ' in the beginning of responses.\n"
        self.__game_setup = self.__template
        self.__template += "Here is the chat history {history}.\n"
        self.__template += "{username}: {user_input}"

    def get_response_to_event(self, event:str):
        result = self.__name + ": " + \
            self.__chain.invoke({
                "username" : self.__opponent_name, 
                "history":self.__chat_history, 
                "user_input": event, 
                "bot_name":self.__name, 
                "game":self.__game_name
            })
        
        self.__last_event = event
        self.__last_bot_text = result
        self.__chat_history+= self.__last_event + "\n\n" + result + "\n\n"
        return result
    
    def get_response_to_speech(self, message:str):
        result = self.__name + ": " + \
            self.__chain.invoke({
                "username" : self.__opponent_name, 
                "history":self.__chat_history, 
                "user_input": message, 
                "bot_name":self.__name, 
                "game":self.__game_name
            })
        
        self.__last_user_text = self.__opponent_name + ": " + message
        self.__last_bot_text = result
        self.__chat_history+= self.__last_user_text + "\n\n" + result + "\n\n"
        return result

    #Getters:
    def get_template(self):
        return self.__template
    
    def get_game_setup(self):
        return self.__game_setup

    def get_history(self):
        return self.__chat_history
    
    def get_last_bot_text(self):
        return self.__last_bot_text
    
    def get_last_opponent_text(self):
        return self.__last_user_text
    
    def get_last_event(self):
        return self.__last_event
    
    def get_name(self):
        return self.__name
    
    def get_opponent_name(self):
        return self.__opponent_name
    
    def get_personality(self):
        return self.__personality
    
    def get_occupation(self):
        return self.__occupation

    def print_stats(self):
        print(f"\nAI Bot:\nname{self.__name}\nmodel {self.__model_name}\npersonality: {self.__personality}\noccupation:{self.__occupation}")



#Testing::
if __name__ == "__main__":
    x = LLMBot("mistral","Gemma","Johnny",personality_key="Aggressive",occupation_key="Pikachu",setting_key="Western")
    x.print_stats()
    print("\n\n")
    print("history",x.get_history())
    print("response",x.get_response_to_speech("What you gonna do about it?"))
    print("response",x.get_response_to_speech("Take that!"))
    print("response",x.get_response_to_speech("I'm gonna call Jimmy Joe out if you don't behave!"))
    print("response", x.get_response_to_event("Player makes an outstanding move!"))
    print("response",x.get_response_to_speech("Fine, I give up."))
    print("\n\n\n------------------------------\n")
    print("history",x.get_history())
    print("\n\n\n------------------------------\n")
    print("history",x.get_game_setup())
    