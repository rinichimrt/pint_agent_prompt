#!/usr/bin/env python3

#!/usr/bin/env python
import ollama
from actor import Actor
from prompts_and_roles import ROLES, DIALOGUE_SCENARIOS, META_PROMPTS
import config
import os
from datetime import datetime

def run_pds_agent_simulation(ollama_client, model_name, agent_actor_role_key, user_actor_role_key, initial_prompt, max_turns=5, seed=None):
    """
    2つのLLMアクター同士を対話させるPDSセッションを実行します。
    """
    # --- 1. エージェント役とユーザー役、2つのアクターを初期化 ---
    if agent_actor_role_key not in ROLES or user_actor_role_key not in ROLES:
        print("エラー: 指定されたロールキーが ROLES に存在しません。")
        return None

    # エージェント役アクターのプロンプト組み立て
    agent_system_prompt = ROLES[agent_actor_role_key]
    if config.ENABLE_SELF_ANALYSIS:
        meta_prompt_key = "self_analysis_" + config.ENHANCED_USER_UTTERANCE_KEY.lower()
        if meta_prompt_key in META_PROMPTS:
            agent_system_prompt += "\n\n" + META_PROMPTS[meta_prompt_key]
            print(f"--- [INFO] エージェント役にメタ解説機能({config.ENHANCED_USER_UTTERANCE_KEY})が追加されました。 ---")

    agent_actor = Actor(model_name, agent_system_prompt, ollama_client, seed)
    user_actor = Actor(model_name, ROLES[user_actor_role_key], ollama_client, seed + 1 if seed is not None else None)

    print(f"\n--- PDSエージェントシミュレーション開始 ---")
    print(f"エージェント役: {agent_actor_role_key} | ユーザー役: {user_actor_role_key}")
    print("---------------------------------------")

    last_response = initial_prompt
    print(f"\n[ターン 0 - PDS (開始)]\n最初の発話: {last_response}")

    merged_conversation_history = [
        {'role': 'system', 'content': f"これはエージェント '{agent_actor_role_key}' とユーザー役 '{user_actor_role_key}' の対話シミュレーションです。"},
        {'role': 'user', 'content': last_response}
    ]

    for i in range(max_turns):
        current_turn_display = i + 1
        print(f"\n[ターン {current_turn_display} - エージェント役 ({agent_actor_role_key}) が応答を生成中...]")
        agent_reminded_prompt = set_reminder(last_response, agent_actor_role_key)
        agent_response = agent_actor.ask(agent_reminded_prompt)
        if agent_response is None: break
        print(f"応答: {agent_response}")
        last_response = agent_response
        merged_conversation_history.append({'role': 'assistant', 'content': agent_response})

        print(f"\n[ターン {current_turn_display} - ユーザー役 ({user_actor_role_key}) が応答を生成中...]")
        user_reminded_prompt = set_reminder(last_response, user_actor_role_key)
        user_response = user_actor.ask(user_reminded_prompt)
        if user_response is None: break
        print(f"応答: {user_response}")
        last_response = user_response
        merged_conversation_history.append({'role': 'user', 'content': user_response})
        print("--------------------------")

    print("\n--- PDSセッション終了 ---")
    return merged_conversation_history

def run_evaluation(ollama_client, model_name, conversation_history, seed=None):
    """
    対話履歴を評価エージェントに渡し、評価結果を取得します。
    """
    print("\n--- 対話評価セッション開始 ---")
    evaluator_role_key = "evaluator_agent_ja"
    if evaluator_role_key not in ROLES:
        print(f"エラー: 評価ロール '{evaluator_role_key}' が prompts_and_roles.py に定義されていません。")
        return None

    history_string = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    evaluation_prompt = f"以下の対話履歴を分析し、指示されたフォーマットに従って評価してください。\n\n--- 対話履歴 ---\n{history_string}"

    evaluator_actor = Actor(model_name, ROLES[evaluator_role_key], ollama_client, seed)

    print("評価エージェントが対話履歴を分析中...")
    evaluation_result = evaluator_actor.ask(evaluation_prompt)

    if evaluation_result:
        print("--- 評価完了 ---")
        print(evaluation_result)
    else:
        print("--- 評価失敗 ---")
    return evaluation_result

def set_reminder(response, actor_role_key):
    """毎回の生成前に自分（返答するLLM）の役割をリマインドさせるための処理"""
    if config.ENHANCED_USER_UTTERANCE_KEY == "JA":
        return f"\nあなたは「{ROLES[actor_role_key]}」という役割です。次の発言に答えてください：なお応答の文量は100程度にしてください。\n{response}"
    elif config.ENHANCED_USER_UTTERANCE_KEY == "EN":
        return f"\nYour role is '{ROLES[actor_role_key]}'. Please respond to the following statement: \n{response}"
    return response

if __name__ == '__main__':
    # --- PDS実行設定 ---
    TARGET_MODEL_NAME = config.DEFAULT_MODEL_NAME
    AGENT_ACTOR_ROLE_KEY = config.DEFAULT_TARGET_ACTOR_ROLE_KEY
    USER_ACTOR_ROLE_KEY = config.DEFAULT_USER_ACTOR_ROLE_KEY
    INITIAL_PROMPT = config.DEFAULT_INITIAL_PROMPT
    MAX_TURNS = config.DEFAULT_MAX_TURNS
    SESSION_SEED_VALUE = config.DEFAULT_SEED
    # --------------------

    print("プロジェクトPDS 実行エンジン (エージェントシミュレーション + 評価モード)")
    print(
        f"""設定情報:
    モデル         : {TARGET_MODEL_NAME}
    エージェント役 : {AGENT_ACTOR_ROLE_KEY}
    ユーザー役     : {USER_ACTOR_ROLE_KEY}
    シード         : {SESSION_SEED_VALUE}
    ターン数       : {MAX_TURNS}
"""
    )

    ollama_client = ollama.Client()

    # 1. 対話シミュレーションを実行
    final_conversation_history = run_pds_agent_simulation(
        ollama_client=ollama_client, model_name=TARGET_MODEL_NAME, agent_actor_role_key=AGENT_ACTOR_ROLE_KEY,
        user_actor_role_key=USER_ACTOR_ROLE_KEY, initial_prompt=INITIAL_PROMPT, max_turns=MAX_TURNS, seed=SESSION_SEED_VALUE
    )

    if final_conversation_history:
        print("\nシミュレーションは完了しました。")

        # 2. 対話履歴の評価を実行
        evaluation_result_str = run_evaluation(
            ollama_client=ollama_client, model_name=TARGET_MODEL_NAME,
            conversation_history=final_conversation_history, seed=SESSION_SEED_VALUE
        )

        # 3. 対話履歴と評価結果をまとめて保存
        try:
            history_dir = "history"
            os.makedirs(history_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_model_name = TARGET_MODEL_NAME.replace('/', '_')
            history_filename = f"sim_history_{safe_model_name}_{AGENT_ACTOR_ROLE_KEY}_vs_{USER_ACTOR_ROLE_KEY}_{timestamp}.json"
            full_filepath = os.path.join(history_dir, history_filename)

            import json
            evaluation_data = {}
            if evaluation_result_str:
                try:
                    evaluation_data = json.loads(evaluation_result_str)
                except json.JSONDecodeError:
                    evaluation_data = {"error": "Failed to parse evaluation JSON.", "raw_output": evaluation_result_str}

            final_data_to_save = {
                "simulation_log": final_conversation_history,
                "evaluation_result": evaluation_data
            }

            with open(full_filepath, "w", encoding="utf-8") as f:
                json.dump(final_data_to_save, f, ensure_ascii=False, indent=2)

            print(f"対話履歴と評価結果は {full_filepath} に保存されました。")

        except Exception as e:
            print(f"エラー: ファイル保存中に問題が発生しました - {e}")
