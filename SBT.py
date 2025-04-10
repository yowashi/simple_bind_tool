from maya import cmds

# グローバル変数としてログエリアを保持
log_field = None

def log_message(message):
    """ログエリアにメッセージを表示"""
    global log_field
    if log_field:
        cmds.scrollField(log_field, edit=True, insertText=message + "\n")
    else:
        print(message)  # ログエリアが未設定の場合はコンソールに出力

def create_ui():
    # ウィンドウを削除（存在する場合）
    if cmds.window("myWindow", exists=True):
        cmds.deleteUI("myWindow")

    # ウィンドウを作成
    window = cmds.window("myWindow", title="Simple Bind Tool")
    cmds.columnLayout(adjustableColumn=True)

    # ボタンを追加
    cmds.button(label="select objects body only Bind", command=lambda x: body_bind())
    cmds.button(label="select objects body and sk Bind", command=lambda x: body_sk_bind_ctrl())
    cmds.button(label="unbind", command=lambda x: unbind_ctrl())
    cmds.button(label="Copy Skin Weight", command=lambda x: copy_skin_weights_from_selection())
    cmds.button(label="Remove Influences", command=lambda x: remove_unused_influences())
    cmds.button(label="delete_nondeformer_history", command=lambda x: delete_nondeformer_history())
    cmds.button(label="Close", command=lambda _: cmds.deleteUI(window))

    # ログエリアを追加
    global log_field
    log_field = cmds.scrollField(editable=False, wordWrap=True, height=200)

    # ウィンドウを表示
    cmds.showWindow(window)

# バインドするsetの内容をリストに追加する。
def bind_joint_list(set_name):
    bind_joint = []
    if cmds.objExists(set_name):
        set_elements = cmds.sets(set_name, q=True)
        if set_elements:
            bind_joint.extend(set_elements)
        log_message(f"Elements in the set have been added to the list: {bind_joint}")
    else:
        log_message("そんな要素ねーよ")
    return bind_joint

# 選択しているオブジェクトをリストに格納する。
def select_obj_add_list():
    select_obj = []
    selection = cmds.ls(selection=True)
    if selection:
        select_obj.extend(selection)
        log_message(f"selected_obj: {select_obj}")
    else:
        log_message("NO")
    return select_obj

# select_obj と bind_joint_list の内容を参照してバインドする
def bind_function(bind_joint, select_obj):
    if not bind_joint:
        log_message("Error: No joints provided for binding.")
        return
    if not select_obj:
        log_message("Error: No objects selected for binding.")
        return
    # バインドスキンを実行
    for bind_obj in select_obj:
        cmds.skinCluster(bind_joint, bind_obj, tsb=True, mi=4)
        log_message("Skin binding completed successfully.")

def body_bind():
    set_name = "body_bind"  # bodyのset名を設定
    joints = bind_joint_list(set_name)
    bind_obj = select_obj_add_list()
    bind_function(joints, bind_obj)

def body_sk_bind_ctrl():
    setname_body = "body_bind"  # bodyのset名を設定
    setname_sk = "sk_bind"  # skのset名を設定
    body_joint = bind_joint_list(setname_body)
    sk_joint = bind_joint_list(setname_sk)
    combine_list = body_joint + sk_joint
    bind_obj = select_obj_add_list()
    bind_function(combine_list, bind_obj)

def unbind_ctrl():
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        log_message("No objects selected.")
        return
    for obj in selected_objects:
        skin_clusters = cmds.ls(cmds.listHistory(obj), type="skinCluster")
        if skin_clusters:
            for skin in skin_clusters:
                cmds.delete(skin)
            log_message(f"Unbound skin cluster(s) from: {obj}")
        else:
            log_message(f"No skin cluster found on: {obj}")

def copy_skin_weights_from_selection():
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        log_message("2つのオブジェクトを選択してください。（コピー元→コピー先の順）")
        return

    source_mesh, target_mesh = selection
    try:
        source_skin_cluster = cmds.ls(cmds.listHistory(source_mesh), type='skinCluster')[0]
        target_skin_cluster = cmds.ls(cmds.listHistory(target_mesh), type='skinCluster')[0]
    except IndexError:
        log_message("選択されたオブジェクトのいずれかにスキンクラスタがありません。")
        return

    try:
        cmds.copySkinWeights(
            sourceSkin=source_skin_cluster,
            destinationSkin=target_skin_cluster,
            noMirror=True,
            surfaceAssociation='closestPoint',
            influenceAssociation='closestJoint'
        )
        log_message(f"スキンウェイトを {source_mesh} から {target_mesh} にコピーしました。")
    except Exception as e:
        log_message(f"スキンウェイトのコピー中にエラーが発生しました: {str(e)}")


def remove_unused_influences():
    select_objects = cmds.ls(selection=True)

    if not select_objects:
        print("オブジェクトを選択してください。")
        return

    for obj in select_objects:
        skin_clusters = cmds.ls(cmds.listHistory(obj), type='skinCluster')

        if not skin_clusters:
            print(f"{obj} にはスキンクラスタがありません。")
            continue

        skin_cluster = skin_clusters[0]

        # 削除前のインフルエンス数
        before_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
        before_count = len(before_influences)

        # 不要なインフルエンスを削除
        cmds.skinCluster(skin_cluster, edit=True, removeUnusedInfluence=True)

        # 削除後のインフルエンス数
        after_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
        after_count = len(after_influences)

        # 削除されたインフルエンス数
        removed_count = before_count - after_count

        log_message(f"{obj}: 削除前 {before_count} 個 → 削除後 {after_count} 個 （{removed_count} 個のインフルエンスを削除）")

def delete_nondeformer_history():
    select_objects = cmds.ls(selection = True)
    for obj in select_objects:
        cmds.bakePartialHistory(obj, prePostDeformers=True)

    log_message(f"{select_objects}}: のでフォーマー以外のヒストリーを削除しました。")


create_ui()