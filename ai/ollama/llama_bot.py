#https://github.com/ollama/ollama/blob/main/README.md
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os
import re
import time

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
        self.__history_entries = []
        if history:
            self.__history_entries.append(history)
        self.__max_history_entries = int(os.getenv("CONQUEST4_MAX_HISTORY_ENTRIES", "12"))
        self.__perf_log = os.getenv("CONQUEST4_PERF_LOG", "1") != "0"
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
        return OllamaLLM(
            model=model_name,
            num_ctx=int(os.getenv("CONQUEST4_NUM_CTX", "2048")),
            num_predict=int(os.getenv("CONQUEST4_NUM_PREDICT", "120")),
            temperature=float(os.getenv("CONQUEST4_TEMPERATURE", "0.8")),
            top_p=float(os.getenv("CONQUEST4_TOP_P", "0.9")),
        )

    def __append_history(self, entry):
        """Append one chat entry and keep a rolling history window."""
        self.__history_entries.append(entry)
        if len(self.__history_entries) > self.__max_history_entries:
            self.__history_entries = self.__history_entries[-self.__max_history_entries:]
        self.__chat_history = "\n\n".join(self.__history_entries)

    def __normalize_response(self, raw_text):
        """Clean up model output so UI gets a complete, readable sentence block."""
        text = (raw_text or "").strip()
        if not text:
            return "Let's keep playing."

        # Remove accidental speaker prefixes.
        lowered = text.lower()
        bot_prefix = f"{self.__name.lower()}:"
        if lowered.startswith(bot_prefix):
            text = text[len(self.__name) + 1 :].strip()
        elif lowered.startswith("assistant:"):
            text = text[len("assistant:") :].strip()

        # Normalize whitespace to avoid odd line wraps.
        text = re.sub(r"\s+", " ", text).strip()

        # Remove prompt-echo artifacts from hidden narrative directives.
        artifacts = [
            f"{self.__opponent_name}: Story premise:",
            "Story premise:",
            "Current phase:",
            "Move quality:",
        ]
        for marker in artifacts:
            idx = text.lower().find(marker.lower())
            if idx != -1:
                text = text[:idx].strip()

        # Force first-person self-reference for bot narration.
        # Replace explicit bot-name references with first-person pronouns.
        name = re.escape(self.__name)
        text = re.sub(rf"\b{name}'s\b", "my", text, flags=re.IGNORECASE)
        text = re.sub(rf"(^|[.!?]\s+){name}\b", r"\1I", text, flags=re.IGNORECASE)
        text = re.sub(rf"\b{name}\b", "I", text, flags=re.IGNORECASE)
        text = re.sub(r"\bmy\b", lambda m: "My" if m.start() == 0 else "my", text)

        # Prefer trimming to the last complete sentence if output was cut.
        sentence_endings = [text.rfind("."), text.rfind("!"), text.rfind("?")]
        last_end = max(sentence_endings)
        if last_end >= max(40, int(len(text) * 0.45)):
            text = text[: last_end + 1].strip()
        elif text and text[-1] not in ".!?":
            text = text + "."

        return text
    
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
        self.__template += (
            "Respond to the player with creative, vivid language in one paragraph at most "
            "(2-4 sentences, under 80 words). Keep it concise and coherent. "
            "End with a complete sentence (no cut-off ending). "
            "Use first-person voice for yourself (I/me/my), never refer to yourself by your name. "
            "Only generate your words or actions. Do not generate label text such as "
            "'{bot_name}: ' or '{username}: ' in the beginning of responses.\n"
        )
        self.__game_setup = self.__template
        self.__template += "Here is the chat history {history}.\n"
        self.__template += "{username}: {user_input}"

    def get_response_to_event(self, event:str):
        start = time.perf_counter()
        raw = self.__chain.invoke({
                "username" : self.__opponent_name, 
                "history":self.__chat_history, 
                "user_input": event, 
                "bot_name":self.__name, 
                "game":self.__game_name
            })
        result = self.__name + ": " + self.__normalize_response(raw)
        
        self.__last_event = event
        self.__last_bot_text = result
        self.__append_history(self.__last_event)
        self.__append_history(result)
        if self.__perf_log:
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(
                f"[perf] llm_event_ms={elapsed_ms:.1f} "
                f"history_entries={len(self.__history_entries)} "
                f"history_chars={len(self.__chat_history)}"
            )
        return result
    
    def get_response_to_speech(self, message:str):
        start = time.perf_counter()
        raw = self.__chain.invoke({
                "username" : self.__opponent_name, 
                "history":self.__chat_history, 
                "user_input": message, 
                "bot_name":self.__name, 
                "game":self.__game_name
            })
        result = self.__name + ": " + self.__normalize_response(raw)
        
        self.__last_user_text = self.__opponent_name + ": " + message
        self.__last_bot_text = result
        self.__append_history(self.__last_user_text)
        self.__append_history(result)
        if self.__perf_log:
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(
                f"[perf] llm_chat_ms={elapsed_ms:.1f} "
                f"history_entries={len(self.__history_entries)} "
                f"history_chars={len(self.__chat_history)}"
            )
        return result

    def get_response_to_directive(self, directive: str):
        """
        Generate a response from an internal directive without storing it as user chat text.
        This prevents hidden control prompts from leaking into visible conversation history.
        """
        start = time.perf_counter()
        raw = self.__chain.invoke({
                "username" : self.__opponent_name,
                "history": self.__chat_history,
                "user_input": directive,
                "bot_name": self.__name,
                "game": self.__game_name
            })
        result = self.__name + ": " + self.__normalize_response(raw)

        # Keep only bot output for continuity; do not append the hidden directive.
        self.__last_bot_text = result
        self.__append_history(result)
        if self.__perf_log:
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(
                f"[perf] llm_directive_ms={elapsed_ms:.1f} "
                f"history_entries={len(self.__history_entries)} "
                f"history_chars={len(self.__chat_history)}"
            )
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
    x = LLMBot("mistral","Gemma","Johnny",personality_key="Aggressive",occupation_key="Teacher",setting_key="Western")
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
    
