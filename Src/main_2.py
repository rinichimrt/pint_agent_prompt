#!/usr/bin/env python
import ollama # Ollamaクライアントライブラリ
from actor import Actor
from prompts_and_roles import ROLES, DIALOGUE_SCENARIOS # 修正: DIALOGUE_SCENARIOSをインポート
import config
import os
from datetime import datetime

def run_pds_agent_simulation(ollama_client, model_name, agent_actor_role_key, user_actor_role_key, initial_prompt, max_turns=5, seed=None):
    """
    2つのLLMアクター同士を対話させるPDSセッションを実行します。

    Args:
        ollama_client (ollama.Client): 初期化済みのOllamaクライアント。
        model_name (str): 両アクターが使用するLLMモデル名。
        agent_actor_role_key (str): メインのエージェント役アクターのロールキー。
        user_actor_role_key (str): ユーザー役アクターのロールキー。
        initial_prompt (str): 対話を開始するための最初の発話。
        max_turns (int, optional): 対話の最大ターン数（1ターン = ユーザー役とエージェント役の1往復）。
        seed (int, optional): 再現性のためのシード値。

    Returns:
        list: エージェント役の最終的な全対話履歴。エラー時はNone。
    """
    # --- 1. エージェント役とユーザー役、2つのアクターを初期化 ---
    # エージェント役アクター
    if agent_actor_role_key not in ROLES:
        print(f"エラー: エージェント役のロール '{agent_actor_role_key}' が prompts_and_roles.py に定義されていません。")
        return None
    agent_system_prompt = ROLES[agent_actor_role_key]
    agent_actor = Actor(
        model_name=model_name,
        role_prompt=agent_system_prompt,
        ollama_client=ollama_client,
        seed=seed
    )

    # ユーザー役アクター
    if user_actor_role_key not in ROLES:
        print(f"エラー: ユーザー役のロール '{user_actor_role_key}' が prompts_and_roles.py に定義されていません。")
        return None
    user_system_prompt = ROLES[user_actor_role_key]
    user_actor = Actor(
        model_name=model_name,
        role_prompt=user_system_prompt,
        ollama_client=ollama_client,
        seed=seed + 1 if seed is not None else None # シードをずらして多様性を出す
    )

    print(f"\n--- PDSエージェントシミュレーション開始 ---")
    print(f"エージェント役: {agent_actor_role_key} | ユーザー役: {user_actor_role_key}")
    print("---------------------------------------")

    # --- 2. 対話ループ ---
    last_response = initial_prompt
    print(f"\n[ターン 0 - PDS (開始)]")
    print(f"最初の発話: {last_response}")

    # 2つのアクターの対話履歴をマージするためのリスト
    merged_conversation_history = [
        {'role': 'system', 'content': f"これはエージェント '{agent_actor_role_key}' とユーザー役 '{user_actor_role_key}' の対話シミュレーションです。"},
        {'role': 'user', 'content': last_response}
    ]

    for i in range(max_turns):
        current_turn_display = i + 1

        # --- エージェント役のターン ---
        print(f"\n[ターン {current_turn_display} - エージェント役 ({agent_actor_role_key}) が応答を生成中...]")

        messages = set_reminder(
            response = last_response,
            actor_role_key = agent_actor_role_key
        )

        agent_response = agent_actor.ask(messages)
        if agent_response is None: break
        print(f"応答: {agent_response}")
        last_response = agent_response
        merged_conversation_history.append({'role': 'assistant', 'content': agent_response})


        # --- ユーザー役のターン ---
        print(f"\n[ターン {current_turn_display} - ユーザー役 ({user_actor_role_key}) が応答を生成中...]")

        messages = set_reminder(
            response = last_response,
            actor_role_key = user_actor_role_key
        )

        user_response = user_actor.ask(messages)
        if user_response is None: break
        print(f"応答: {user_response}")
        last_response = user_response
        merged_conversation_history.append({'role': 'user', 'content': user_response})

        print("--------------------------")
        print("\n--- PDSセッション終了 ---")
    print("最終的な対話履歴 (マージ済み):")
    for message_idx, message in enumerate(merged_conversation_history):
        print(f"  [{message_idx}] {message['role']}: {str(message['content'])[:120]}...")

    # 最終的な履歴として、マージしたものを返す
    return merged_conversation_history


# 毎回の生成前に自分（返答するLLM）の役割をリマインドさせるための処理
def set_reminder(response, actor_role_key):
    if config.ENHANCED_USER_UTTERANCE_KEY == "JA":
        print(actor_role_key)
        enhanced_user_utterance = f"\nあなたは「{ROLES[actor_role_key]}」という役割です。次の発言に答えてください：なお応答は短めにしてください。\n{response}"
    if config.ENHANCED_USER_UTTERANCE_KEY == "EN":
        enhanced_user_utterance = f"\nYour role is '{ROLES[actor_role_key]}'. Please respond to the following statement: \n{response}"


    return enhanced_user_utterance





if __name__ == '__main__':
    # --- PDS実行設定 ---
    TARGET_MODEL_NAME =  config.DEFAULT_MODEL_NAME

    # 2つのアクターのロールをconfigから、または直接指定
    AGENT_ACTOR_ROLE_KEY = config.DEFAULT_TARGET_ACTOR_ROLE_KEY
    USER_ACTOR_ROLE_KEY = config.DEFAULT_USER_ACTOR_ROLE_KEY

    # 対話を開始するための最初の発話
    INITIAL_PROMPT = config.DEFAULT_INITIAL_PROMPT


    # 対話の往復回数を指定
    MAX_TURNS = config.DEFAULT_MAX_TURNS

    SESSION_SEED_VALUE = config.DEFAULT_SEED
    # --------------------

    print("プロジェクトPDS 実行エンジン (エージェントシミュレーションモード)")
    print(f"設定情報: モデル='{TARGET_MODEL_NAME}', エージェント役='{AGENT_ACTOR_ROLE_KEY}', ユーザー役='{USER_ACTOR_ROLE_KEY}', シード={SESSION_SEED_VALUE}")

    # Ollamaクライアントを初期化
    ollama_client = ollama.Client()

    final_conversation_history = run_pds_agent_simulation(
        ollama_client=ollama_client,
        model_name=TARGET_MODEL_NAME,
        agent_actor_role_key=AGENT_ACTOR_ROLE_KEY,
        user_actor_role_key=USER_ACTOR_ROLE_KEY,
        initial_prompt=INITIAL_PROMPT,
        max_turns=MAX_TURNS,
        seed=SESSION_SEED_VALUE
    )

    if final_conversation_history:
        print("\nセッションは完了しました。")

        # --- 対話履歴のファイル保存処理 ---
        try:
            history_dir = "history"
            os.makedirs(history_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_model_name = TARGET_MODEL_NAME.replace('/', '_')

            # ファイル名に両方のアクターロールを含める
            history_filename = f"sim_history_{safe_model_name}_{AGENT_ACTOR_ROLE_KEY}_vs_{USER_ACTOR_ROLE_KEY}_{timestamp}.json"

            full_filepath = os.path.join(history_dir, history_filename)

            import json
            with open(full_filepath, "w", encoding="utf-8") as f:
                json.dump(final_conversation_history, f, ensure_ascii=False, indent=2)

            print(f"対話履歴は {full_filepath} に保存されました。")

        except Exception as e:
            print(f"エラー: 対話履歴のファイル保存中に問題が発生しました - {e}")
