#!/usr/bin/env python3

# config.py
# プロジェクトPDSの動作設定を管理するファイルです。

# --- モデル設定 ---
# PDSで使用するデフォルトのLLMモデル名。
# `ollama list` コマンドで利用可能なモデルを確認し、適切なものを設定してください。
# DEFAULT_MODEL_NAME = "gemma3:latest"  # 例: "llama3", "mistral", "phi3"
DEFAULT_MODEL_NAME = "gemma3:27b"  # 例: "llama3", "mistral", "phi3"


# --- デフォルト実行設定 ---
# `main.py` 実行時に使用されるデフォルトのロールと対話シナリオのキーを設定します。
# `prompts_and_roles.py` で定義されているキーを指定してください。

# デフォルトのターゲットアクターロールのキー
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "pint_agent_1"
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "default_assistant"
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "creative_writer"
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "code_explainer"
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "dialogue_partner_neutral"
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "pint_agent_2_JA"
# DEFAULT_TARGET_ACTOR_ROLE_KEY = "pint_agent_2_EN"
DEFAULT_TARGET_ACTOR_ROLE_KEY = "pint_agent_boss_with_feedback"

# デフォルトの対話シナリオのキー
#
#------------------------------------------------------------------------20250611現在使っていない
DIALOGUE_SCENARIOS_KEY = "SCENARIO_PINT_AGENT_TEST_JA"
# DIALOGUE_SCENARIOS_KEY = "SCENARIO_PINT_AGENT_TEST_EN"
# DIALOGUE_SCENARIOS_KEY = "SCENARIO_BOSS_PERSUASION_JA"

#------------------------------------------------------------------------20250611現在使っていない
# --- 再現性設定 ---
# デフォルトのシード値。Noneにすると、実行ごとに結果が変動しやすくなります。
# 特定の数値を設定すると、同じ入力に対して（ほぼ）同じ出力が得られるようになります。
DEFAULT_SEED = 22

# 入力を英語にするか日本語にするか
ENHANCED_USER_UTTERANCE_KEY= "EN"
# ENHANCED_USER_UTTERANCE_KEY = "JA"

# DEFAULT_USER_ACTOR_ROLE_KEY = "dialogue_partner_neutral"
# DEFAULT_USER_ACTOR_ROLE_KEY = "fany_user"
DEFAULT_USER_ACTOR_ROLE_KEY = "explane_user_to_Boss"


# DEFAULT_INITIAL_PROMPT = "こんにちは。あなたの役割について、私に理解できるように説明してください。"
DEFAULT_INITIAL_PROMPT = "Hello. Please explain your role to me so I can understand."


DEFAULT_MAX_TURNS = 5
# --- (オプション) 対話履歴の保存設定 ---
# 必要に応じてコメントを解除し、設定してください。
# SAVE_HISTORY_DIR = "pds_history_logs"
# HISTORY_FILENAME_PREFIX = "pds_dialogue"

#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
# --- (オプション) その他のPDS設定 ---
# 必要に応じて、プロジェクト固有の設定項目を追加できます。
# 例: DEFAULT_USER_ROLE_KEY = "dialogue_partner_neutral"
