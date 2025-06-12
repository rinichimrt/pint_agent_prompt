#!/usr/bin/env python3


import ollama

class Actor:
    def __init__(self, model_name, role_prompt, ollama_client=None, seed=None):
        self.model_name = model_name
        self.ollama_client = ollama_client # ollama.Client() のインスタンスを期待
        self.seed = seed
        self.messages = [{'role': 'system', 'content': role_prompt}]

    def ask(self, user_prompt):
        current_user_message = {'role': 'user', 'content': user_prompt}
        self.messages.append(current_user_message)


        # self.print_input_prompt(user_prompt)



        options_payload = {}
        if self.seed is not None:
            options_payload['seed'] = self.seed
        try:

            response = self.ollama_client.chat(
                model=self.model_name,
                messages=self.messages,
                stream=False, # PDSの目的からストリーミングはFalse
                options=options_payload if options_payload else None # optionsが空ならNoneを渡す
            )

            llm_response_content = response['message']['content']



            print(f"--- Received response from Ollama ---")

            self.messages.append({'role': 'assistant', 'content': llm_response_content})
            return llm_response_content

        except ollama.ResponseError as e:
            print(f"エラー: Ollama APIからの応答エラー - {e.error}")
            if hasattr(e, 'status_code'):
                print(f"ステータスコード: {e.status_code}")
            return None
        except Exception as e:
            print(f"エラー: LLMとの通信中に予期せぬ問題が発生しました - {e}")
            return None


    def print_input_prompt(self, input_prompt):
        print(f"---------- 入力されたprompt ----------：\n{input_prompt}\n---------------------------------")
