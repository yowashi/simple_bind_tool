import os
import sys

# このスクリプトとTool.pyが同一階層にあると仮定
script_dir = os.path.dirname(__file__)
tool_path = os.path.join(script_dir, "Maya_QtTool.py")

# Tool.py を実行
if tool_path not in sys.path:
    sys.path.append(script_dir)

# 実行
import Tool
Tool.main()
