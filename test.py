<<<<<<< HEAD
from maya import cmds
import re

def get_root_node(node):
    """
    指定ノードの最上位の親（ルートノード）を取得
    """
    parent = cmds.listRelatives(node, parent=True, fullPath=True)
    if parent:
        return get_root_node(parent[0])  # 再帰的に親を探す
    return node  # 最上位のノードを返す

def get_joints_in_hierarchy(node):
    """
    指定ノードの階層内にある Joint（ジョイント）のみを再帰的に取得
    """
    joints = []
    children = cmds.listRelatives(node, children=True, fullPath=True) or []  # フルパスで子ノードを取得

    for child in children:
        if cmds.nodeType(child) == "joint":  # Joint の場合のみ追加
            joints.append(child)
        joints.extend(get_joints_in_hierarchy(child))  # 再帰的に子ノードを探索
    
    return joints

# 選択オブジェクトの最上位ルートを取得し、そこから階層全体の Joint を取得
selected = cmds.ls(selection=True, long=True)  # `long=True` でフルパス取得

if selected:
    root_nodes = set()  # 重複を防ぐためセットを使用
    for obj in selected:
        root_nodes.add(get_root_node(obj))  # 最上位の親（ルートノード）を取得

    all_joints = []
    for root in root_nodes:
        all_joints.extend(get_joints_in_hierarchy(root))  # ルートから探索

    print(f"階層全体の Joint ノード: {all_joints}")
    cmds.select(all_joints, replace=True)  # 取得したジョイントを選択
=======
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
>>>>>>> origin/main
