"""
ONNXBot - ONNX Runtime-based LLM inference with Apple Neural Engine

This module provides an alternative to LLMBot that uses ONNX Runtime with
CoreML Execution Provider to leverage the Apple Neural Engine for faster inference.

Architecture:
    Game → ONNXBot → ONNX Runtime → CoreML EP → Apple Neural Engine → Response
"""

import os
import time
from typing import Optional, List, Dict
import numpy as np


class ONNXBot:
    """
    LLM Bot using ONNX Runtime with Apple Neural Engine acceleration.
    
    Drop-in replacement for LLMBot with identical interface.
    """
    
    def __init__(
        self,
        model_path: str,
        name: str,
        opponent_name: str,
        *,
        game_name: str = "connect four",
        personality_key: str = "",
        occupation_key: str = "",
        setting_key: str = "",
        history: str = "",
        use_neural_engine: bool = True
    ):
        """
        Initialize ONNXBot with ONNX model and Neural Engine support.
        
        Args:
            model_path: Path to ONNX model directory
            name: Bot's name
            opponent_name: Player's name
            game_name: Name of the game
            personality_key: Personality type
            occupation_key: Bot's occupation
            setting_key: Game setting/theme
            history: Optional conversation history
            use_neural_engine: Enable CoreML Execution Provider (ANE)
        """
        self._model_path = model_path
        self._name = name
        self._opponent_name = opponent_name
        self._game_name = game_name
        self._personality = personality_key
        self._occupation = occupation_key
        self._setting = setting_key
        self._chat_history = history
        self._use_neural_engine = use_neural_engine
        
        # Performance tracking
        self._inference_times: List[float] = []
        
        # State tracking (matching LLMBot interface)
        self._last_user_text = ""
        self._last_bot_text = ""
        self._last_event = ""
        self._game_setup = ""
        self._template = ""
        
        # Initialize ONNX Runtime session
        self._session = None
        self._tokenizer = None
        self._initialize_model()
        self._initialize_template()
    
    def _initialize_model(self):
        """Load ONNX model with CoreML Execution Provider."""
        print(f"🔧 Initializing ONNX model from: {self._model_path}")
        
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
            
            # Load tokenizer
            print("   Loading tokenizer...")
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_path)
            
            # Configure session options
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            # Set execution providers
            if self._use_neural_engine:
                providers = ["CoreMLExecutionProvider", "CPUExecutionProvider"]
                print("   🚀 Enabling Apple Neural Engine acceleration")
            else:
                providers = ["CPUExecutionProvider"]
                print("   Using CPU execution")
            
            # Create inference session
            print("   Creating ONNX Runtime session...")
            model_file = os.path.join(self._model_path, "model.onnx")
            
            if not os.path.exists(model_file):
                # Try optimum format
                model_file = os.path.join(self._model_path, "decoder_model.onnx")
            
            if not os.path.exists(model_file):
                raise FileNotFoundError(f"No ONNX model found in {self._model_path}")
            
            self._session = ort.InferenceSession(
                model_file,
                sess_options=sess_options,
                providers=providers
            )
            
            # Verify provider
            actual_provider = self._session.get_providers()[0]
            if actual_provider == "CoreMLExecutionProvider":
                print("   ✅ Neural Engine is active!")
            else:
                print(f"   ⚠️  Fell back to: {actual_provider}")
            
            print("✅ ONNX model loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize ONNX model: {e}")
            raise
    
    def _initialize_template(self):
        """Initialize prompt template (matching LLMBot)."""
        from ai.ollama.personality import personality_dict as p_dict
        from ai.ollama.personality import occupation_dict as o_dict
        from ai.ollama.personality import setting_dict as s_dict
        
        self._template = f"""
        Your name is {self._name}. Your opponent is {self._opponent_name}.
        You are both playing a game of {self._game_name}.
        """
        
        self._template += s_dict.get(self._setting, f"Setting: {self._setting}") + "\n"
        self._template += o_dict.get(self._occupation, f"Occupation: {self._occupation}") + "\n"
        self._template += p_dict.get(self._personality, f"Personality: {self._personality}") + "\n"
        self._template += f"Respond to the player. Only generate your words or actions.\n"
        
        self._game_setup = self._template
        self._template += "Chat history: {history}\n{username}: {user_input}"
    
    def _generate_text(self, prompt: str, max_new_tokens: int = 100) -> str:
        """
        Generate text using ONNX model.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        start_time = time.perf_counter()
        
        try:
            # Tokenize input
            inputs = self._tokenizer(prompt, return_tensors="np")
            input_ids = inputs["input_ids"].astype(np.int64)
            attention_mask = inputs["attention_mask"].astype(np.int64)
            
            # Run inference
            # Note: This is simplified - full implementation needs iterative generation
            outputs = self._session.run(
                None,
                {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask
                }
            )
            
            # Decode output
            output_ids = outputs[0]
            response = self._tokenizer.decode(output_ids[0], skip_special_tokens=True)
            
            # Extract only new tokens (remove input prompt)
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            # Track inference time
            elapsed = time.perf_counter() - start_time
            self._inference_times.append(elapsed)
            
            return response
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return f"[Error: {str(e)[:50]}]"
    
    def get_response_to_event(self, event: str) -> str:
        """
        Generate response to game event (matching LLMBot interface).
        
        Args:
            event: Game event description
            
        Returns:
            Formatted bot response
        """
        # Build full prompt
        full_prompt = self._template.format(
            username=self._opponent_name,
            history=self._chat_history,
            user_input=event
        )
        
        # Generate response
        response_text = self._generate_text(full_prompt, max_new_tokens=80)
        
        # Format response
        result = f"{self._name}: {response_text}"
        
        # Update state
        self._last_event = event
        self._last_bot_text = result
        self._chat_history += f"{event}\n\n{result}\n\n"
        
        return result
    
    def get_response_to_speech(self, message: str) -> str:
        """
        Generate response to user speech (matching LLMBot interface).
        
        Args:
            message: User's spoken message
            
        Returns:
            Formatted bot response
        """
        # Build full prompt
        full_prompt = self._template.format(
            username=self._opponent_name,
            history=self._chat_history,
            user_input=message
        )
        
        # Generate response
        response_text = self._generate_text(full_prompt, max_new_tokens=100)
        
        # Format response
        result = f"{self._name}: {response_text}"
        
        # Update state
        self._last_user_text = f"{self._opponent_name}: {message}"
        self._last_bot_text = result
        self._chat_history += f"{self._last_user_text}\n\n{result}\n\n"
        
        return result
    
    # Getters (matching LLMBot interface)
    
    def get_template(self) -> str:
        return self._template
    
    def get_game_setup(self) -> str:
        return self._game_setup
    
    def get_history(self) -> str:
        return self._chat_history
    
    def get_last_bot_text(self) -> str:
        return self._last_bot_text
    
    def get_last_opponent_text(self) -> str:
        return self._last_user_text
    
    def get_last_event(self) -> str:
        return self._last_event
    
    def get_name(self) -> str:
        return self._name
    
    def get_opponent_name(self) -> str:
        return self._opponent_name
    
    def get_personality(self) -> str:
        return self._personality
    
    def get_occupation(self) -> str:
        return self._occupation
    
    def get_mean_inference_time(self) -> float:
        """Get average inference time."""
        if not self._inference_times:
            return 0.0
        return sum(self._inference_times) / len(self._inference_times)
    
    def print_stats(self):
        """Print bot statistics."""
        mean_time = self.get_mean_inference_time()
        print(f"\n🤖 ONNX Bot Stats:")
        print(f"   Name: {self._name}")
        print(f"   Model: {self._model_path}")
        print(f"   Personality: {self._personality}")
        print(f"   Occupation: {self._occupation}")
        print(f"   Neural Engine: {'Enabled' if self._use_neural_engine else 'Disabled'}")
        if self._inference_times:
            print(f"   Inferences: {len(self._inference_times)}")
            print(f"   Mean time: {mean_time:.3f}s")
            print(f"   Min/Max: {min(self._inference_times):.3f}s / {max(self._inference_times):.3f}s")
