#!/usr/bin/env pythonimport ollama # Ollamaクライアントライブラリ
from actor import Actor
from prompts_and_roles import ROLES, DIALOGUE_SCENARIOS
import config
import ollama

import os
from datetime import datetime

def run_pds_session(ollama_client, model_name, actor_role_key, pds_user_prompts, seed=None):

    if actor_role_key not in ROLES: # run_pds_session呼び出し前にチェックする方が良いかもしれません
        print(f"エラー: ロール '{actor_role_key}' が prompts_and_roles.py の ROLES に定義されていません。")
        return None

    actor_system_prompt = ROLES[actor_role_key]

    pds_actor = Actor(
        model_name=model_name,
        role_prompt=actor_system_prompt,
        ollama_client=ollama_client,
        seed=seed
    )

    print(f"\n--- PDSセッション開始 ---")

    overall_turn_counter = 0 # 全体的なターンカウンターを初期化

    for pds_user_utterance in pds_user_prompts:
        # PDS (ユーザー役) のターン
        overall_turn_counter += 1
        print(f"\n[ターン {overall_turn_counter} - PDS (ユーザー役)]")


        # 日本語用
        #
        #
        if config.DIALOGUE_SCENARIOS_KEY == "SCENARIO_PINT_AGENT_TEST_JA":
            enhanced_user_utterance = f"あなたは「{actor_role_key}」という役割です。次の発言に答えてください：{pds_user_utterance}"
        elif config.DIALOGUE_SCENARIOS_KEY == "SCENARIO_PINT_AGENT_TEST_EN":
            enhanced_user_utterance = f"Your role is '{actor_role_key}'. Please respond to the following statement: {pds_user_utterance}"



        print(f"発話: {enhanced_user_utterance}")
        llm_response = pds_actor.ask(enhanced_user_utterance)

        if llm_response is None:
            print(f"エラー: LLMからの応答がありませんでした (ユーザー発話に対するターン {overall_turn_counter})。セッションを中断します。")
            return pds_actor.messages

        # LLMアクターのターン
        overall_turn_counter += 1
        print(f"\n[ターン {overall_turn_counter} - LLMアクター ({actor_role_key})]")
        print(f"応答: {llm_response}")
        print("--------------------------")

    print("\n--- PDSセッション終了 ---")
    print("最終的な対話履歴:")
    for message_idx, message in enumerate(pds_actor.messages): # これは actor.messages のインデックス
        print(f"  [{message_idx}] {message['role']}: {str(message['content'])[:120]}...")

    return pds_actor.messages


if __name__ == '__main__':
    TARGET_MODEL_NAME =  config.DEFAULT_MODEL_NAME # Ollamaに存在するモデル名に変更してください (例: "llama3", "mistral")
    TARGET_ACTOR_ROLE_KEY = config.DEFAULT_TARGET_ACTOR_ROLE_KEY # definitions.ROLES のキーから選択

    #
    # dialogue_script_for_pds_user = SCENARIO_PINT_AGENT_TEST_JA
    target_scenario_key = config.DIALOGUE_SCENARIOS_KEY

    if target_scenario_key in DIALOGUE_SCENARIOS:
        dialogue_script_for_pds_user = DIALOGUE_SCENARIOS[target_scenario_key]
    else:
        print(f"エラー: configで指定されたシナリオキー '{target_scenario_key}' が prompts_and_roles.py に存在しません。")
        exit() # プログラムを終了

    # dialogue_script_for_pds_user = config.DEFAULT_SCENARIO_PINT_AGENT_TEST
    SESSION_SEED_VALUE = config.DEFAULT_SEED # シード値を固定すると再現性が高まります
    # --------------------

    print("プロジェクトPDS 実行エンジンへようこそ！")
    print(f"設定情報: モデル='{TARGET_MODEL_NAME}', ロール='{TARGET_ACTOR_ROLE_KEY}', シード={SESSION_SEED_VALUE}")


    # Ollamaクライアントを初期化
    ollama_client = ollama.Client()

    final_conversation_history = run_pds_session(
        ollama_client=ollama_client,
        model_name=TARGET_MODEL_NAME,
        actor_role_key=TARGET_ACTOR_ROLE_KEY,
        pds_user_prompts=dialogue_script_for_pds_user,
        seed=SESSION_SEED_VALUE
    )
if final_conversation_history:
        print("\nセッションは完了しました。")

        # --- 対話履歴のファイル保存処理 ---
        try:
            # 1. 保存先のディレクトリ名を定義
            history_dir = "history"

            # 2. ディレクトリが存在しない場合は作成
            os.makedirs(history_dir, exist_ok=True)

            # 3. 現在の日時を取得し、ファイル名に含めるフォーマットに変換
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 4. ファイル名に使えない文字を置換 (例: モデル名に含まれる '/')
            safe_model_name = TARGET_MODEL_NAME.replace('/', '_')

            # 5. 日時を含んだ最終的なファイル名を生成
            history_filename = f"pds_history_{safe_model_name}_{TARGET_ACTOR_ROLE_KEY}_{timestamp}_{SESSION_SEED_VALUE}.json"

            # 6. ディレクトリパスとファイル名を結合して、完全なファイルパスを作成
            full_filepath = os.path.join(history_dir, history_filename)

            # 7. JSON形式でファイルに保存
            import json # jsonライブラリはこのスコープでのみ使用するため、ここでインポート
            with open(full_filepath, "w", encoding="utf-8") as f:
                json.dump(final_conversation_history, f, ensure_ascii=False, indent=2)

            print(f"対話履歴は {full_filepath} に保存されました。")

        except Exception as e:
            print(f"エラー: 対話履歴のファイル保存中に問題が発生しました - {e}")




